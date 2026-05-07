import json
from pathlib import Path

from app.db.session import SessionLocal
from app.ingestion.product_importer import import_xlsx_products
from app.repositories.tenants import get_or_create_tenant
from app.services.product_import_service import clear_products_for_tenant, import_products


def import_products_from_xlsx(path: Path, tenant_id: int, mapping_path: Path, all_sheets: bool = False) -> int:
    field_mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    rows = import_xlsx_products(path, field_mapping, all_sheets=all_sheets)
    with SessionLocal() as db:
        import_products(db, tenant_id, rows)
        db.commit()
    return len(rows)


def import_merchant_products(
    merchant_code: str,
    merchant_name: str,
    path: Path,
    mapping_path: Path,
    all_sheets: bool = False,
    replace: bool = False,
) -> int:
    field_mapping_text = mapping_path.read_text(encoding="utf-8")
    field_mapping = json.loads(field_mapping_text)
    rows = import_xlsx_products(path, field_mapping, all_sheets=all_sheets)

    with SessionLocal() as db:
        tenant = get_or_create_tenant(db, merchant_code, merchant_name, field_mapping=field_mapping_text)
        if replace:
            clear_products_for_tenant(db, tenant.id)
        import_products(db, tenant.id, rows)
        db.commit()

    return len(rows)


if __name__ == "__main__":
    count = import_merchant_products(
        merchant_code="QCT001",
        merchant_name="青春塘",
        path=Path(r"d:\yd_project\aibot_rag\aibotcode\ai_bot\src\yuanshuju\青春塘产品对应体质.xlsx"),
        mapping_path=Path("examples/qingchuntang_field_mapping.json"),
        all_sheets=True,
        replace=True,
    )
    print(f"Imported {count} products for merchant QCT001")
