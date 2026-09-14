"""Small versioned SQL migration runner."""

from pathlib import Path

from .repository import mysql_config


def migrate(directory, connector=None):
    if connector is None:
        import mysql.connector as connector
    connection = connector.connect(**mysql_config())
    cursor = connection.cursor()
    applied = []
    try:
        cursor.execute("CREATE TABLE IF NOT EXISTS schema_migrations (version VARCHAR(100) PRIMARY KEY, applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)")
        cursor.execute("SELECT version FROM schema_migrations")
        completed = {row[0] for row in cursor.fetchall()}
        for path in sorted(Path(directory).glob("*.sql")):
            if path.stem in completed:
                continue
            for statement in path.read_text(encoding="utf-8").split(";"):
                if statement.strip():
                    cursor.execute(statement)
            cursor.execute("INSERT INTO schema_migrations(version) VALUES(%s)", (path.stem,))
            connection.commit()
            applied.append(path.stem)
        return applied
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()
