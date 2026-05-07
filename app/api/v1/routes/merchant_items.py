import json
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.api.v1.dependencies import AuthContext, get_current_merchant_context
from app.db.session import get_db
from app.ingestion.product_importer import is_blocking_import_issue, validate_xlsx_products
from app.repositories.products import (
    count_active_products,
    create_product,
    get_active_product,
    list_active_products,
    product_to_item,
    soft_delete_product,
    update_product,
)
from app.repositories.tenants import get_tenant_by_id
from app.repositories.tenants import update_tenant_field_mapping
from app.schemas.product import (
    ProductCreateRequest,
    ProductImportIssueItem,
    ProductImportMappingResponse,
    ProductImportMappingUpdateRequest,
    ProductImportMappingUpdateResponse,
    ProductImportResponse,
    ProductItem,
    ProductListResponse,
    ProductMutationResponse,
    ProductUpdateRequest,
)
from app.services.product_import_service import clear_products_for_tenant, import_products

router = APIRouter(prefix="/merchant/items")
REQUIRED_MAPPING_FIELDS = ["name"]


def get_current_tenant_id(
    context: AuthContext = Depends(get_current_merchant_context),
) -> int:
    return context.tenant_id


@router.get("", response_model=ProductListResponse)
def list_items(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant_id),
) -> ProductListResponse:
    products = list_active_products(db, tenant_id, page, size)
    return ProductListResponse(
        items=[product_to_item(product) for product in products],
        total=count_active_products(db, tenant_id),
        page=page,
        size=size,
    )


@router.post("/import", response_model=ProductImportResponse)
async def import_items(
    file: UploadFile = File(...),
    mapping_json: str | None = Form(default=None),
    all_sheets: bool = Form(default=True),
    replace: bool = Form(default=False),
    dry_run: bool = Form(default=True),
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant_id),
) -> ProductImportResponse:
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="only .xlsx files are supported")

    tenant = get_tenant_by_id(db, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=400, detail="invalid tenant")
    field_mapping = _resolve_field_mapping(mapping_json, tenant.field_mapping)
    path = await _save_upload_to_temp_file(file)
    try:
        result = validate_xlsx_products(path, field_mapping, all_sheets=all_sheets)
        rows = result.rows
        issues = [
            ProductImportIssueItem(
                sheet_name=issue.sheet_name,
                row_number=issue.row_number,
                field=issue.field,
                message=issue.message,
                value=issue.value,
            )
            for issue in result.issues
        ]
        unknown_constitutions = sorted({item for row in rows for item in row.unknown_constitutions})
        blocking_issues = [issue for issue in result.issues if is_blocking_import_issue(issue)]
        if not dry_run and blocking_issues:
            return ProductImportResponse(
                parsed_count=result.total_rows,
                valid_count=len(rows),
                issue_count=len(issues),
                imported_count=0,
                dry_run=dry_run,
                replaced=False,
                unknown_constitutions=unknown_constitutions,
                issues=issues,
            )
        if not dry_run:
            if replace:
                clear_products_for_tenant(db, tenant_id)
            import_products(db, tenant_id, rows)
            db.commit()
        return ProductImportResponse(
            parsed_count=result.total_rows,
            valid_count=len(rows),
            issue_count=len(issues),
            imported_count=0 if dry_run else len(rows),
            dry_run=dry_run,
            replaced=False if dry_run else replace,
            unknown_constitutions=unknown_constitutions,
            issues=issues,
        )
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        try:
            path.unlink(missing_ok=True)
        except PermissionError:
            pass


@router.get("/import/mapping", response_model=ProductImportMappingResponse)
def get_import_mapping(
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant_id),
) -> ProductImportMappingResponse:
    tenant = get_tenant_by_id(db, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=400, detail="invalid tenant")
    mapping = _resolve_field_mapping(None, tenant.field_mapping)
    return ProductImportMappingResponse(mapping=mapping, required_fields=REQUIRED_MAPPING_FIELDS)


@router.put("/import/mapping", response_model=ProductImportMappingUpdateResponse)
def update_import_mapping(
    payload: ProductImportMappingUpdateRequest,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant_id),
) -> ProductImportMappingUpdateResponse:
    tenant = get_tenant_by_id(db, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=400, detail="invalid tenant")
    mapping = _validate_field_mapping(payload.mapping)
    mapping_text = json.dumps(mapping, ensure_ascii=False, separators=(",", ":"))
    if len(mapping_text) > 2048:
        raise HTTPException(status_code=400, detail="field mapping is too large")
    update_tenant_field_mapping(db, tenant, mapping_text)
    db.commit()
    return ProductImportMappingUpdateResponse(mapping=mapping)


@router.get("/{product_id}", response_model=ProductItem)
def get_item(
    product_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant_id),
) -> ProductItem:
    product = get_active_product(db, tenant_id, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="product not found")
    return product_to_item(product)


@router.post("", response_model=ProductMutationResponse)
def create_item(
    payload: ProductCreateRequest,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant_id),
) -> ProductMutationResponse:
    product = create_product(db, tenant_id, payload)
    db.commit()
    db.refresh(product)
    return ProductMutationResponse(item=product_to_item(product))


@router.put("/{product_id}", response_model=ProductMutationResponse)
def update_item(
    product_id: int,
    payload: ProductUpdateRequest,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant_id),
) -> ProductMutationResponse:
    product = get_active_product(db, tenant_id, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="product not found")
    product = update_product(db, product, payload)
    db.commit()
    db.refresh(product)
    return ProductMutationResponse(item=product_to_item(product))


@router.delete("/{product_id}")
def delete_item(
    product_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant_id),
) -> dict[str, bool]:
    product = get_active_product(db, tenant_id, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="product not found")
    soft_delete_product(db, product)
    db.commit()
    return {"deleted": True}


def _resolve_field_mapping(
    mapping_json: str | None,
    tenant_field_mapping: str | None,
) -> dict[str, str | list[str]]:
    raw_mapping = mapping_json or tenant_field_mapping
    if not raw_mapping:
        raise HTTPException(status_code=400, detail="missing field mapping")
    try:
        mapping = json.loads(raw_mapping)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="invalid mapping json") from exc
    if not isinstance(mapping, dict):
        raise HTTPException(status_code=400, detail="field mapping must be an object")
    return _validate_field_mapping(mapping)


def _validate_field_mapping(mapping: dict[str, object]) -> dict[str, str | list[str]]:
    normalized: dict[str, str | list[str]] = {}
    for target, source in mapping.items():
        if not isinstance(target, str) or not target.strip():
            raise HTTPException(status_code=400, detail="mapping field name must be a non-empty string")
        if isinstance(source, str):
            if not source.strip():
                raise HTTPException(status_code=400, detail=f"mapping source for {target} is empty")
            normalized[target.strip()] = source.strip()
            continue
        if isinstance(source, list):
            candidates = [item.strip() for item in source if isinstance(item, str) and item.strip()]
            if not candidates:
                raise HTTPException(status_code=400, detail=f"mapping source for {target} is empty")
            normalized[target.strip()] = candidates
            continue
        raise HTTPException(status_code=400, detail=f"mapping source for {target} must be string or string list")
    missing_fields = [field for field in REQUIRED_MAPPING_FIELDS if field not in normalized]
    if missing_fields:
        raise HTTPException(status_code=400, detail=f"missing required mapping fields: {', '.join(missing_fields)}")
    return normalized


async def _save_upload_to_temp_file(file: UploadFile) -> Path:
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="empty upload file")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_file:
        temp_file.write(content)
        return Path(temp_file.name)
