"""
API tests for the assets app.

Covers authentication, the Admin/Viewer permission split, telemetry ingest
validation, and the audit trail. Three tests are marked expectedFailure: they
document known defects rather than asserting current behaviour. See the
comment on each for the fix.

Run:  python manage.py test assets -v 2
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from assets.models import Asset, AuditLog, Location

User = get_user_model()


class BaseAPITestCase(APITestCase):
    """One Admin, one Viewer, one Asset. Shared by every test class below."""

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin@example.com',
            email='admin@example.com',
            password='test-pass-12345',
            is_staff=True,
        )
        self.viewer = User.objects.create_user(
            username='viewer@example.com',
            email='viewer@example.com',
            password='test-pass-12345',
            is_staff=False,
        )
        self.asset = Asset.objects.create(
            name='Delivery Van 01',
            asset_type=Asset.AssetType.VEHICLE,
            status=Asset.Status.ACTIVE,
            description='Hyderabad depot',
        )
        self.list_url = reverse('asset-list')
        self.detail_url = reverse('asset-detail', args=[self.asset.id])
        self.telemetry_url = reverse('telemetry')
        self.stats_url = reverse('asset-stats')

    def valid_asset_payload(self, **overrides):
        payload = {
            'name': 'Forklift 07',
            'asset_type': Asset.AssetType.EQUIPMENT,
            'status': Asset.Status.ACTIVE,
            'description': '',
        }
        payload.update(overrides)
        return payload


class AuthenticationTests(BaseAPITestCase):
    """Anonymous traffic must not reach the API."""

    def test_anonymous_list_request_is_rejected(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_create_request_is_rejected(self):
        response = self.client.post(self.list_url, self.valid_asset_payload())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Asset.objects.count(), 1)

    def test_anonymous_stats_request_is_rejected(self):
        response = self.client.get(self.stats_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_endpoint_returns_access_and_refresh(self):
        response = self.client.post(
            reverse('token_obtain_pair'),
            {'username': 'admin@example.com', 'password': 'test-pass-12345'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_token_endpoint_rejects_bad_credentials(self):
        response = self.client.post(
            reverse('token_obtain_pair'),
            {'username': 'admin@example.com', 'password': 'wrong-password'},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_token_authorizes_a_request(self):
        # Exercises the real JWT path end to end rather than force_authenticate.
        token = self.client.post(
            reverse('token_obtain_pair'),
            {'username': 'viewer@example.com', 'password': 'test-pass-12345'},
        ).data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_malformed_token_is_rejected(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer not-a-real-token')
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RolePermissionTests(BaseAPITestCase):
    """IsAdminOrReadOnly: Viewer reads, Admin writes."""

    def test_viewer_can_list_assets(self):
        self.client.force_authenticate(user=self.viewer)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_viewer_cannot_create_asset(self):
        self.client.force_authenticate(user=self.viewer)
        response = self.client.post(self.list_url, self.valid_asset_payload())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Asset.objects.count(), 1)

    def test_viewer_cannot_update_asset(self):
        self.client.force_authenticate(user=self.viewer)
        response = self.client.patch(self.detail_url, {'status': Asset.Status.LOST})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.status, Asset.Status.ACTIVE)

    def test_viewer_cannot_delete_asset(self):
        self.client.force_authenticate(user=self.viewer)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Asset.objects.filter(id=self.asset.id).exists())

    def test_admin_can_create_asset(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.list_url, self.valid_asset_payload())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Asset.objects.filter(name='Forklift 07').exists())

    def test_admin_can_update_asset(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(self.detail_url, {'status': Asset.Status.LOST})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.status, Asset.Status.LOST)

    def test_admin_can_delete_asset(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Asset.objects.filter(id=self.asset.id).exists())


class AssetValidationTests(BaseAPITestCase):
    """Bad payloads stop at the serializer, not the database."""

    def test_invalid_asset_type_is_rejected(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            self.list_url, self.valid_asset_payload(asset_type='spaceship')
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('asset_type', response.data)

    def test_invalid_status_is_rejected(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            self.list_url, self.valid_asset_payload(status='on_fire')
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status', response.data)

    def test_missing_name_is_rejected(self):
        self.client.force_authenticate(user=self.admin)
        payload = self.valid_asset_payload()
        del payload['name']
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)


class AssetFilteringTests(BaseAPITestCase):
    """get_queryset() honours the status and asset_type query params."""

    def setUp(self):
        super().setUp()
        Asset.objects.create(
            name='Pallet Jack 02',
            asset_type=Asset.AssetType.EQUIPMENT,
            status=Asset.Status.LOST,
        )
        self.client.force_authenticate(user=self.viewer)

    def test_filter_by_status(self):
        response = self.client.get(self.list_url, {'status': Asset.Status.LOST})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Pallet Jack 02')

    def test_filter_by_asset_type(self):
        response = self.client.get(
            self.list_url, {'asset_type': Asset.AssetType.VEHICLE}
        )
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Delivery Van 01')

    def test_unfiltered_list_returns_all_assets(self):
        response = self.client.get(self.list_url)
        self.assertEqual(len(response.data), 2)


class TelemetryIngestTests(BaseAPITestCase):
    """The ingest endpoint is the pipeline's front door — it must validate."""

    def valid_ping(self, **overrides):
        payload = {
            'asset_id': str(self.asset.id),
            'latitude': '17.385000',
            'longitude': '78.486700',
        }
        payload.update(overrides)
        return payload

    def test_valid_ping_creates_location(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.telemetry_url, self.valid_ping(), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.asset.locations.count(), 1)

    def test_valid_ping_writes_audit_entry(self):
        self.client.force_authenticate(user=self.admin)
        self.client.post(self.telemetry_url, self.valid_ping(), format='json')
        entry = AuditLog.objects.latest('timestamp')
        self.assertEqual(entry.action, 'telemetry_ping')
        self.assertEqual(entry.performed_by, self.admin)
        self.assertEqual(entry.asset, self.asset)

    def test_ping_surfaces_as_latest_location_on_asset_detail(self):
        # Integration check: ingest is visible through the read API.
        self.client.force_authenticate(user=self.admin)
        self.client.post(self.telemetry_url, self.valid_ping(), format='json')
        response = self.client.get(self.detail_url)
        self.assertIsNotNone(response.data['latest_location'])
        self.assertEqual(
            str(response.data['latest_location']['latitude']), '17.385000'
        )

    def test_unknown_asset_id_is_rejected(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            self.telemetry_url,
            self.valid_ping(asset_id='2b0e4b3e-0000-4000-8000-000000000000'),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('asset_id', response.data)
        self.assertEqual(Location.objects.count(), 0)

    def test_non_numeric_latitude_is_rejected(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            self.telemetry_url, self.valid_ping(latitude='not-a-number'), format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('latitude', response.data)

    def test_missing_longitude_is_rejected(self):
        self.client.force_authenticate(user=self.admin)
        payload = self.valid_ping()
        del payload['longitude']
        response = self.client.post(self.telemetry_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('longitude', response.data)

    def test_rejected_ping_writes_no_audit_entry(self):
        self.client.force_authenticate(user=self.admin)
        self.client.post(
            self.telemetry_url, self.valid_ping(latitude='bad'), format='json'
        )
        self.assertEqual(AuditLog.objects.count(), 0)

    def test_viewer_cannot_post_telemetry(self):
        # Documents current behaviour: TelemetryView uses IsAdminOrReadOnly, so
        # ingest requires is_staff. A real device fleet would need a staff
        # service account — worth a dedicated ingest permission class later.
        self.client.force_authenticate(user=self.viewer)
        response = self.client.post(self.telemetry_url, self.valid_ping(), format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_out_of_range_latitude_is_rejected(self):
        # Regression test: TelemetrySerializer only checks decimal shape, so a
        # latitude of 250 is stored happily. Fix: add
        # MinValueValidator(-90)/MaxValueValidator(90) on latitude and
        # -180/180 on longitude in TelemetrySerializer.
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            self.telemetry_url, self.valid_ping(latitude='250.000000'), format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LocationEndpointTests(BaseAPITestCase):
    """LocationViewSet.create() hand-rolls validation instead of using a serializer."""

    def setUp(self):
        super().setUp()
        self.location_url = reverse('location-list')

    def test_missing_asset_id_is_rejected(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            self.location_url, {'latitude': '17.4', 'longitude': '78.5'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('asset_id', response.data)

    def test_unknown_asset_id_is_rejected(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            self.location_url,
            {
                'asset_id': '2b0e4b3e-0000-4000-8000-000000000000',
                'latitude': '17.4',
                'longitude': '78.5',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_locations_can_be_filtered_by_asset(self):
        Location.objects.create(asset=self.asset, latitude='17.4', longitude='78.5')
        self.client.force_authenticate(user=self.viewer)
        response = self.client.get(self.location_url, {'asset_id': str(self.asset.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_missing_latitude_returns_400_not_500(self):
        # Regression test: create() passes request.data.get('latitude') straight into
        # Location.objects.create(), so a missing latitude raises IntegrityError
        # and surfaces as a 500. Fix: run the payload through a serializer
        # instead of hand-rolling the checks.
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            self.location_url,
            {'asset_id': str(self.asset.id), 'longitude': '78.5'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AuditLogTests(BaseAPITestCase):
    """
    An API write must leave an audit trail. These assert a side effect across
    two models rather than just a status code.
    """

    def test_create_writes_audit_entry_attributed_to_actor(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.list_url, self.valid_asset_payload())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(AuditLog.objects.count(), 1)
        entry = AuditLog.objects.get()
        self.assertEqual(entry.action, 'asset_created')
        self.assertEqual(entry.performed_by, self.admin)
        self.assertEqual(str(entry.asset.id), response.data['id'])

    def test_update_writes_audit_entry_with_changed_fields(self):
        self.client.force_authenticate(user=self.admin)
        self.client.patch(self.detail_url, {'status': Asset.Status.LOST})

        entry = AuditLog.objects.latest('timestamp')
        self.assertEqual(entry.action, 'asset_updated')
        self.assertEqual(entry.performed_by, self.admin)
        self.assertEqual(entry.details['data']['status'], Asset.Status.LOST)

    def test_forbidden_write_leaves_no_audit_entry(self):
        # A rejected request must not pollute the trail.
        self.client.force_authenticate(user=self.viewer)
        self.client.post(self.list_url, self.valid_asset_payload())
        self.assertEqual(AuditLog.objects.count(), 0)

    def test_invalid_payload_leaves_no_audit_entry(self):
        self.client.force_authenticate(user=self.admin)
        self.client.post(self.list_url, self.valid_asset_payload(asset_type='spaceship'))
        self.assertEqual(AuditLog.objects.count(), 0)

    def test_delete_is_audited_and_the_trail_survives(self):
        # Regression test for two former defects:
        #   1. AssetViewSet.perform_destroy() broadcasts over the channel layer
        #      but never writes an AuditLog row.
        #   2. Even if it did, AuditLog.asset is on_delete=CASCADE, so deleting
        #      an asset wipes its entire history — the one event an audit log
        #      exists to record also destroys the evidence.
        # Fix: make AuditLog.asset null=True, on_delete=SET_NULL, add a
        # denormalised asset_name column, then log inside perform_destroy().
        self.client.force_authenticate(user=self.admin)
        self.client.delete(self.detail_url)

        entry = AuditLog.objects.get(action='asset_deleted')
        self.assertEqual(entry.performed_by, self.admin)
        self.assertIsNone(entry.asset)          # FK nulled by the delete
        self.assertEqual(entry.asset_name, 'Delivery Van 01')   # name preserved

    def test_history_of_a_deleted_asset_is_retained(self):
        # The create and update entries must outlive the asset itself.
        self.client.force_authenticate(user=self.admin)
        self.client.patch(self.detail_url, {'status': Asset.Status.LOST})
        self.client.delete(self.detail_url)

        self.assertFalse(Asset.objects.filter(id=self.asset.id).exists())
        actions = set(AuditLog.objects.values_list('action', flat=True))
        self.assertEqual(actions, {'asset_updated', 'asset_deleted'})
        for entry in AuditLog.objects.all():
            self.assertEqual(entry.asset_name, 'Delivery Van 01')


class AssetStatsTests(BaseAPITestCase):
    """Stats endpoint is read-only and open to any authenticated user."""

    def setUp(self):
        super().setUp()
        Asset.objects.create(name='Lost Tag', asset_type='equipment', status='lost')
        Asset.objects.create(name='Idle Rig', asset_type='equipment', status='inactive')

    def test_counts_are_correct(self):
        self.client.force_authenticate(user=self.viewer)
        response = self.client.get(self.stats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 3)
        self.assertEqual(response.data['active'], 1)
        self.assertEqual(response.data['inactive'], 1)
        self.assertEqual(response.data['lost'], 1)

    def test_is_admin_flag_reflects_the_requesting_user(self):
        self.client.force_authenticate(user=self.viewer)
        self.assertFalse(self.client.get(self.stats_url).data['is_admin'])

        self.client.force_authenticate(user=self.admin)
        self.assertTrue(self.client.get(self.stats_url).data['is_admin'])
