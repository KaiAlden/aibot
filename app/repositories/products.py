from sqlalchemy import Select, or_, select
from sqlalchemy.orm import Session

from app.models.product import Product, ProductConstitution
from app.schemas.core import Constitution


def build_product_query(
    tenant_id: int,
    constitution: Constitution | None = None,
    form: str | None = None,
    price_max: float | None = None,
) -> Select[tuple[Product]]:
    query = select(Product).where(Product.tenant_id == tenant_id, Product.is_active.is_(True))

    if constitution is not None:
        query = query.outerjoin(ProductConstitution).where(
            or_(
                Product.is_universal.is_(True),
                ProductConstitution.constitution == constitution.value,
            )
        )
    if form:
        query = query.where(Product.form == form)
    if price_max is not None:
        query = query.where(Product.price <= price_max)

    return query


def list_products_for_tenant(
    db: Session,
    tenant_id: int,
    constitution: Constitution | None = None,
    form: str | None = None,
    price_max: float | None = None,
) -> list[Product]:
    query = build_product_query(tenant_id, constitution, form, price_max)
    return list(db.scalars(query).unique())
