from decimal import Decimal

from sqlalchemy.orm import Session

from app.ingestion.product_importer import ProductImportRow
from app.models.product import Product, ProductConstitution, ProductIngredient


def create_product_from_import_row(db: Session, tenant_id: int, row: ProductImportRow) -> Product:
    product = Product(
        tenant_id=tenant_id,
        name=row.name,
        category=row.category,
        form=row.form,
        description=row.description,
        price=row.price,
        weight=row.weight,
        image_url=row.image_url,
        is_universal=row.is_universal,
        business_weight=Decimal("1.00"),
    )
    product.constitutions = [
        ProductConstitution(constitution=constitution)
        for constitution in row.constitutions
        if not row.is_universal
    ]
    product.ingredients = [ProductIngredient(ingredient=ingredient) for ingredient in row.ingredients]
    db.add(product)
    return product


def import_products(db: Session, tenant_id: int, rows: list[ProductImportRow]) -> list[Product]:
    products = [create_product_from_import_row(db, tenant_id, row) for row in rows]
    db.flush()
    return products


def clear_products_for_tenant(db: Session, tenant_id: int) -> None:
    products = db.query(Product).filter(Product.tenant_id == tenant_id).all()
    for product in products:
        db.delete(product)
    db.flush()
