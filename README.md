## Tests

51 tests covering JWT authentication, the Admin/Viewer permission split,
telemetry ingest validation, and the audit trail.

    python manage.py test --settings=core.test_settings

Runs in ~0.3s using in-memory SQLite and a fast password hasher. Run
`python manage.py test` to execute against PostgreSQL instead.

Writing the suite surfaced four defects, since fixed:

- `AuditLog.asset` was `on_delete=CASCADE`, so deleting an asset erased
  its entire history — the one event an audit log exists to record
- Telemetry accepted out-of-range coordinates (latitude 250 was stored)
- `POST /api/locations/` returned 500 on a missing latitude
- Duplicate registration email returned 500 instead of 400
