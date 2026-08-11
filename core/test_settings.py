"""
Settings for running the test suite.

Two overrides: sqlite in memory (so tests need no Postgres) and a fast
password hasher (PBKDF2 dominates runtime otherwise — 66s down to ~4s).

Run:  python manage.py test --settings=core.test_settings
"""
from core.settings import *  # noqa: F401,F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
