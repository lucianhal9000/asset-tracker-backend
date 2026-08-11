"""
Tests for the accounts app (registration).

Run:  python manage.py test accounts -v 2
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class RegistrationTests(APITestCase):
    def setUp(self):
        self.url = reverse('register')
        self.payload = {
            'email': 'New.User@Example.com',
            'password': 'test-pass-12345',
            'password2': 'test-pass-12345',
            'first_name': 'New',
            'last_name': 'User',
        }

    def test_registration_creates_user(self):
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='new.user@example.com').exists())

    def test_email_is_normalised_to_lowercase(self):
        self.client.post(self.url, self.payload)
        user = User.objects.get(email='new.user@example.com')
        self.assertEqual(user.username, 'new.user@example.com')

    def test_password_is_hashed_not_stored_plaintext(self):
        self.client.post(self.url, self.payload)
        user = User.objects.get(email='new.user@example.com')
        self.assertNotEqual(user.password, 'test-pass-12345')
        self.assertTrue(user.check_password('test-pass-12345'))

    def test_new_user_is_not_staff_by_default(self):
        # Registration must never mint an Admin.
        self.client.post(self.url, self.payload)
        user = User.objects.get(email='new.user@example.com')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_registered_user_can_obtain_a_token(self):
        self.client.post(self.url, self.payload)
        response = self.client.post(
            reverse('token_obtain_pair'),
            {'username': 'new.user@example.com', 'password': 'test-pass-12345'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_mismatched_passwords_are_rejected(self):
        payload = dict(self.payload, password2='something-else-12345')
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password2', response.data)
        self.assertEqual(User.objects.count(), 0)

    def test_invalid_email_is_rejected(self):
        response = self.client.post(self.url, dict(self.payload, email='not-an-email'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_short_password_is_rejected(self):
        payload = dict(self.payload, password='short', password2='short')
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_response_does_not_leak_the_password(self):
        response = self.client.post(self.url, self.payload)
        self.assertNotIn('password', response.data)

    def test_duplicate_email_returns_400_not_500(self):
        # Regression test: RegisterSerializer never checks whether the email is
        # already taken, so create_user() hits the username unique constraint
        # and raises IntegrityError -> 500. Fix: add a validate_email() that
        # raises ValidationError when a user with that email already exists.
        self.client.post(self.url, self.payload)
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
