from decimal import Decimal

from fastapi.testclient import TestClient

from app.api.v1 import dependencies
from app.api.v1.routes import merchant_items
from app.db.session import get_db
from app.main import app
from app.models.product import Product
from app.models.tenant import User, UserRole
from app.models.tenant import Tenant
from app.ingestion.product_importer import ProductImportIssue, ProductImportRow, ProductImportValidationResult
from app.services.auth import create_access_token


class FakeDb:
    def __init__(self) -> None:
        self.committed = False
        self.refreshed = None

    def commit(self) -> None:
        self.committed = True

    def refresh(self, value) -> None:
        self.refreshed = value

    def flush(self) -> None:
        pass


def override_db():
    return FakeDb()


def test_list_items_requires_authorization() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/merchant/items")

    assert response.status_code == 401


def test_list_items_returns_tenant_products(monkeypatch) -> None:
    product = Product(id=1, tenant_id=7, name="黄芪茶", price=Decimal("39.90"), is_universal=False)
    monkeypatch.setattr(merchant_items, "list_active_products", lambda db, tenant_id, page, size: [product])
    monkeypatch.setattr(merchant_items, "count_active_products", lambda db, tenant_id: 1)
    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[merchant_items.get_current_tenant_id] = lambda: 7
    client = TestClient(app)

    response = client.get("/api/v1/merchant/items", headers={"X-Merchant-Code": "QCT001"})

    app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "黄芪茶"


def test_get_item_returns_404_for_other_tenant(monkeypatch) -> None:
    monkeypatch.setattr(merchant_items, "get_active_product", lambda db, tenant_id, product_id: None)
    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[merchant_items.get_current_tenant_id] = lambda: 99
    client = TestClient(app)

    response = client.get("/api/v1/merchant/items/1", headers={"X-Merchant-Code": "OTHER"})

    app.dependency_overrides.clear()
    assert response.status_code == 404


def test_list_items_accepts_merchant_admin_token(monkeypatch) -> None:
    product = Product(id=1, tenant_id=7, name="Token Test Product", price=Decimal("39.90"), is_universal=False)
    user = User(id=3, tenant_id=7, username="merchant", password_hash="x", role=UserRole.merchant_admin)
    monkeypatch.setattr(merchant_items, "list_active_products", lambda db, tenant_id, page, size: [product])
    monkeypatch.setattr(merchant_items, "count_active_products", lambda db, tenant_id: 1)
    monkeypatch.setattr(dependencies, "get_user_by_id", lambda db, user_id: user)
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)
    token = create_access_token("3", UserRole.merchant_admin.value, tenant_id=7)

    response = client.get("/api/v1/merchant/items", headers={"Authorization": f"Bearer {token}"})

    app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Token Test Product"


def test_delete_item_soft_deletes(monkeypatch) -> None:
    product = Product(id=1, tenant_id=7, name="黄芪茶", is_active=True)
    fake_db = FakeDb()
    monkeypatch.setattr(merchant_items, "get_active_product", lambda db, tenant_id, product_id: product)
    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[merchant_items.get_current_tenant_id] = lambda: 7
    client = TestClient(app)

    response = client.delete("/api/v1/merchant/items/1", headers={"X-Merchant-Code": "QCT001"})

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json() == {"deleted": True}
    assert product.is_active is False
    assert fake_db.committed is True


def test_import_items_dry_run_parses_upload(monkeypatch) -> None:
    row = ProductImportRow(name="Import Product", constitutions=["气虚质"], unknown_constitutions=["血虚质"])
    monkeypatch.setattr(merchant_items, "get_tenant_by_id", lambda db, tenant_id: Tenant(id=7, merchant_code="QCT001", name="青春塘", field_mapping='{"name":"商品名称"}'))
    monkeypatch.setattr(
        merchant_items,
        "validate_xlsx_products",
        lambda path, field_mapping, all_sheets: ProductImportValidationResult(rows=[row], issues=[], total_rows=1),
    )
    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[merchant_items.get_current_tenant_id] = lambda: 7
    client = TestClient(app)

    response = client.post(
        "/api/v1/merchant/items/import",
        files={"file": ("products.xlsx", b"fake-xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"dry_run": "true", "all_sheets": "true"},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert data["parsed_count"] == 1
    assert data["valid_count"] == 1
    assert data["issue_count"] == 0
    assert data["imported_count"] == 0
    assert data["dry_run"] is True
    assert data["unknown_constitutions"] == ["血虚质"]


def test_import_items_replace_commits(monkeypatch) -> None:
    calls = {"cleared": False, "imported": 0}
    row = ProductImportRow(name="Import Product")
    fake_db = FakeDb()
    monkeypatch.setattr(merchant_items, "get_tenant_by_id", lambda db, tenant_id: Tenant(id=7, merchant_code="QCT001", name="青春塘", field_mapping='{"name":"商品名称"}'))
    monkeypatch.setattr(
        merchant_items,
        "validate_xlsx_products",
        lambda path, field_mapping, all_sheets: ProductImportValidationResult(rows=[row], issues=[], total_rows=1),
    )
    monkeypatch.setattr(merchant_items, "clear_products_for_tenant", lambda db, tenant_id: calls.update(cleared=True))
    monkeypatch.setattr(merchant_items, "import_products", lambda db, tenant_id, rows: calls.update(imported=len(rows)))
    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[merchant_items.get_current_tenant_id] = lambda: 7
    client = TestClient(app)

    response = client.post(
        "/api/v1/merchant/items/import",
        files={"file": ("products.xlsx", b"fake-xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"dry_run": "false", "replace": "true"},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["imported_count"] == 1
    assert calls == {"cleared": True, "imported": 1}
    assert fake_db.committed is True


def test_import_items_reports_validation_issues(monkeypatch) -> None:
    issue = ProductImportIssue(sheet_name="Tea", row_number=3, field="name", message="product name is required")
    monkeypatch.setattr(
        merchant_items,
        "get_tenant_by_id",
        lambda db, tenant_id: Tenant(id=7, merchant_code="QCT001", name="QCT", field_mapping='{"name":"Product Name"}'),
    )
    monkeypatch.setattr(
        merchant_items,
        "validate_xlsx_products",
        lambda path, field_mapping, all_sheets: ProductImportValidationResult(rows=[], issues=[issue], total_rows=1),
    )
    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[merchant_items.get_current_tenant_id] = lambda: 7
    client = TestClient(app)

    response = client.post(
        "/api/v1/merchant/items/import",
        files={"file": ("products.xlsx", b"fake-xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"dry_run": "true"},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert data["parsed_count"] == 1
    assert data["valid_count"] == 0
    assert data["issue_count"] == 1
    assert data["issues"][0]["sheet_name"] == "Tea"
    assert data["issues"][0]["row_number"] == 3


def test_get_import_mapping_returns_tenant_mapping(monkeypatch) -> None:
    monkeypatch.setattr(
        merchant_items,
        "get_tenant_by_id",
        lambda db, tenant_id: Tenant(
            id=7,
            merchant_code="QCT001",
            name="QCT",
            field_mapping='{"name":"Product Name","price":["Price","Sale Price"]}',
        ),
    )
    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[merchant_items.get_current_tenant_id] = lambda: 7
    client = TestClient(app)

    response = client.get("/api/v1/merchant/items/import/mapping")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert data["mapping"]["name"] == "Product Name"
    assert data["mapping"]["price"] == ["Price", "Sale Price"]
    assert data["required_fields"] == ["name"]


def test_update_import_mapping_saves_normalized_json(monkeypatch) -> None:
    tenant = Tenant(id=7, merchant_code="QCT001", name="QCT")
    fake_db = FakeDb()
    monkeypatch.setattr(merchant_items, "get_tenant_by_id", lambda db, tenant_id: tenant)
    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[merchant_items.get_current_tenant_id] = lambda: 7
    client = TestClient(app)

    response = client.put(
        "/api/v1/merchant/items/import/mapping",
        json={"mapping": {"name": " Product Name ", "price": ["", " Price "]}},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["saved"] is True
    assert response.json()["mapping"] == {"name": "Product Name", "price": ["Price"]}
    assert tenant.field_mapping == '{"name":"Product Name","price":["Price"]}'
    assert fake_db.committed is True


def test_update_import_mapping_requires_name(monkeypatch) -> None:
    monkeypatch.setattr(merchant_items, "get_tenant_by_id", lambda db, tenant_id: Tenant(id=7, merchant_code="QCT001", name="QCT"))
    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[merchant_items.get_current_tenant_id] = lambda: 7
    client = TestClient(app)

    response = client.put("/api/v1/merchant/items/import/mapping", json={"mapping": {"price": "Price"}})

    app.dependency_overrides.clear()
    assert response.status_code == 400
    assert "missing required mapping fields" in response.json()["detail"]
