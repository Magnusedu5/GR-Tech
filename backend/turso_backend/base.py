"""
Minimal Django database backend for Turso using libsql-experimental.

Inherits everything from Django's sqlite3 backend (same SQL dialect, same ORM
behavior) but replaces the underlying connection with a remote libsql_experimental
connection to a Turso database.
"""
import libsql_experimental as libsql
from django.db.backends.sqlite3 import base as sqlite3_base
from django.core.exceptions import ImproperlyConfigured


class DatabaseWrapper(sqlite3_base.DatabaseWrapper):

    def get_connection_params(self):
        settings = self.settings_dict
        if not settings["NAME"]:
            raise ImproperlyConfigured(
                "TURSO_DATABASE_URL is not set. "
                "Set it to the libsql:// URL of your Turso database."
            )
        return {
            "database": settings["NAME"],
            "auth_token": settings.get("OPTIONS", {}).get("auth_token", ""),
        }

    def get_new_connection(self, conn_params):
        conn = libsql.connect(**conn_params)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
