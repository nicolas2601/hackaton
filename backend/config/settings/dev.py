"""Dev settings."""
import sys
from .base import *  # noqa: F401,F403
from .base import DATABASES  # noqa: F401

DEBUG = True
ALLOWED_HOSTS = ["*"]

_IS_TESTING = "test" in sys.argv or "pytest" in sys.argv[0]

if _IS_TESTING:
    # Use in-memory SQLite for tests — Supabase doesn't allow CREATE DATABASE.
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
else:
    # Supabase pooler (pgbouncer transaction mode) requires short-lived connections
    # and disables server-side cursors / prepared statements.
    DATABASES["default"]["CONN_MAX_AGE"] = 0
    DATABASES["default"].setdefault("OPTIONS", {})
    DATABASES["default"]["OPTIONS"]["prepare_threshold"] = None
    DATABASES["default"]["DISABLE_SERVER_SIDE_CURSORS"] = True
