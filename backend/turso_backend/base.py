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
        conn = libsql.connect(**conn_params)
        conn.execute('PRAGMA foreign_keys = ON')
        return conn

    def create_cursor(self, name=None):
        return LibsqlCursorWrapper(self.connection.cursor())

    def _set_autocommit(self, autocommit):
        # libsql_experimental doesn't expose isolation_level.
        # Remote connections auto-commit each statement, which is fine
        # for this app's simple insert/select workload.
        pass

    def _savepoint_allowed(self):
        return self.in_atomic_block

    def is_in_memory_db(self):
        return False
