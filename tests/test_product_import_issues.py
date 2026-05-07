from app.ingestion.product_importer import ProductImportIssue, is_blocking_import_issue


def test_unknown_constitution_is_non_blocking_import_issue() -> None:
    issue = ProductImportIssue(sheet_name="Sheet1", row_number=2, field="constitutions", message="unknown constitution")

    assert is_blocking_import_issue(issue) is False


def test_name_issue_is_blocking_import_issue() -> None:
    issue = ProductImportIssue(sheet_name="Sheet1", row_number=2, field="name", message="product name is required")

    assert is_blocking_import_issue(issue) is True
