from django.db.backends.sqlite3.schema import DatabaseSchemaEditor as SQLite3SchemaEditor
from django.db.backends.base.schema import BaseDatabaseSchemaEditor


class DatabaseSchemaEditor(SQLite3SchemaEditor):
    # Don't wrap each migration in an atomic() block. Django's nested
    # BEGIN/SAVEPOINT pattern breaks libsql_experimental's remote connections.
    # Each DDL statement auto-commits individually instead.
    atomic_migration = False

    def __init__(self, connection, collect_sql=False, atomic=True):
        # Call grand-parent to avoid SQLite3's __init__ if it does special things,
        # but we use BaseDatabaseSchemaEditor's __init__ directly.
        BaseDatabaseSchemaEditor.__init__(self, connection, collect_sql=collect_sql, atomic=False)
        # Force no transaction wrapper regardless of what the executor passes.
        self.atomic = None

    def __enter__(self):
        self.deferred_sql = []
        # Skip self.atomic.__enter__() — no transactions during DDL.
        return self
