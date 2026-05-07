from scripts.init_mysql import split_sql_statements


def test_split_sql_statements_ignores_comments() -> None:
    sql = """
-- comment
CREATE TABLE demo (
    id INT
);

CREATE TABLE demo2 (
    id INT
);
"""

    statements = split_sql_statements(sql)

    assert len(statements) == 2
    assert statements[0].startswith("CREATE TABLE demo")
    assert statements[1].startswith("CREATE TABLE demo2")
