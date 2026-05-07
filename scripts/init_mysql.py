from pathlib import Path

from sqlalchemy import create_engine, text

from app.config.settings import settings


SCHEMA_PATH = Path(__file__).resolve().parents[1] / "migrations" / "schema.sql"


def split_sql_statements(sql: str) -> list[str]:
    statements: list[str] = []
    buffer: list[str] = []

    for line in sql.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        buffer.append(line)
        if stripped.endswith(";"):
            statements.append("\n".join(buffer).rstrip(";"))
            buffer = []

    if buffer:
        statements.append("\n".join(buffer))

    return statements


def init_mysql() -> None:
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    engine = create_engine(settings.mysql_dsn, pool_pre_ping=True)

    with engine.begin() as connection:
        for statement in split_sql_statements(schema_sql):
            connection.execute(text(statement))


if __name__ == "__main__":
    init_mysql()
    print(f"MySQL schema initialized from {SCHEMA_PATH}")
