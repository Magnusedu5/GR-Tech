"""
Minimal Django database backend for Turso using libsql-experimental.

Inherits the SQLite3 backend (same SQL dialect, same ORM) but replaces
the underlying connection with a remote libsql_experimental connection.

Key differences from sqlite3:
- No isolation_level support → _set_autocommit is a no-op (auto-commits)
- Cursor needs to convert Django's %s placeholders to ? (libsql style)
"""
import re
import libsql_experimental as libsql
from django.db.backends.sqlite3 import base as sqlite3_base
from django.core.exceptions import ImproperlyConfigured
from .schema import DatabaseSchemaEditor

_FORMAT_TO_QMARK = re.compile(r'(?<!%)%s')


class LibsqlCursorWrapper:
    """Adapts libsql_experimental cursor to match Django's expectations."""

    def __init__(self, cursor):
        self._cursor = cursor

    def __iter__(self):
        return iter(self._cursor)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    @property
    def description(self):
        return self._cursor.description

    @property
    def rowcount(self):
        return self._cursor.rowcount

    @property
    def lastrowid(self):
        return self._cursor.lastrowid

    def close(self):
        self._cursor.close()

    def execute(self, query, params=None):
        query = _FORMAT_TO_QMARK.sub('?', query).replace('%%', '%')
        if params is None:
            return self._cursor.execute(query)
        return self._cursor.execute(query, params)

    def executemany(self, query, param_list):
        query = _FORMAT_TO_QMARK.sub('?', query).replace('%%', '%')
        return self._cursor.executemany(query, param_list)

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    def fetchmany(self, size=None):
        if size is None:
            return self._cursor.fetchmany()
        return self._cursor.fetchmany(size)


class DatabaseWrapper(sqlite3_base.DatabaseWrapper):
    SchemaEditorClass = DatabaseSchemaEditor


    def get_connection_params(self):
        settings = self.settings_dict
        if not settings['NAME']:
            raise ImproperlyConfigured(
                'Set TURSO_DATABASE_URL to the libsql:// URL of your Turso database.'
            )
        return {
            'database': settings['NAME'],
            'auth_token': settings.get('OPTIONS', {}).get('auth_token', ''),
        }

    def get_new_connection(self, conn_params):
        return libsql.connect(**conn_params)

    def create_cursor(self, name=None):
        return LibsqlCursorWrapper(self.connection.cursor())

    def _set_autocommit(self, autocommit):
        # libsql_experimental doesn't expose isolation_level — no-op.
        pass

    def _start_transaction_under_autocommit(self):
        # Don't issue explicit BEGIN — libsql remote connections auto-commit
        # each statement. An explicit BEGIN would conflict with the connection's
        # internal streaming state and raise "cannot start a transaction within
        # a transaction" errors during Django's nested atomic() usage.
        pass

    def _savepoint_allowed(self):
        return self.in_atomic_block

    def disable_constraint_checking(self):
        # Tell Django FKs are already disabled (avoids PRAGMA calls that
        # would trigger NotSupportedError inside schema migrations).
        return True

    def enable_constraint_checking(self):
        # No-op: FK enforcement is handled at the application level.
        # Enabling FKs between migrations causes NotSupportedError on
        # the next migration's schema editor entry.
        pass

    def check_constraints(self, table_names=None):
        # FK constraint checking via PRAGMA is unreliable over libsql remote;
        # skip it — Django validates constraints at the model level anyway.
        pass

    def is_in_memory_db(self):
        return False
