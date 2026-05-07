from decimal import Decimal

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.models.product import Product, ProductConstitution
from app.models.product import ProductIngredient
from app.schemas.core import Constitution
from app.schemas.product import ProductCreateRequest, ProductItem, ProductUpdateRequest


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


def product_to_item(product: Product) -> ProductItem:
    return ProductItem(
        id=product.id,
        name=product.name,
        category=product.category,
        form=product.form,
        description=product.description,
        price=float(product.price) if product.price is not None else None,
        weight=product.weight,
        image_url=product.image_url,
        is_universal=product.is_universal,
        constitutions=[item.constitution for item in product.constitutions],
        ingredients=[item.ingredient for item in product.ingredients],
    )


def count_active_products(db: Session, tenant_id: int) -> int:
    return int(
        db.scalar(
            select(func.count()).select_from(Product).where(Product.tenant_id == tenant_id, Product.is_active.is_(True))
        )
        or 0
    )


def list_active_products(db: Session, tenant_id: int, page: int, size: int) -> list[Product]:
    statement = (
        select(Product)
        .where(Product.tenant_id == tenant_id, Product.is_active.is_(True))
        .order_by(Product.id.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    return list(db.scalars(statement).unique())


def get_active_product(db: Session, tenant_id: int, product_id: int) -> Product | None:
    return db.scalar(
        select(Product).where(
            Product.id == product_id,
            Product.tenant_id == tenant_id,
            Product.is_active.is_(True),
        )
    )


def _replace_product_children(
    product: Product,
    constitutions: list[str] | None = None,
    ingredients: list[str] | None = None,
) -> None:
    if constitutions is not None:
        product.constitutions = [
            ProductConstitution(constitution=constitution)
            for constitution in constitutions
            if constitution and not product.is_universal
        ]
    if ingredients is not None:
        product.ingredients = [ProductIngredient(ingredient=ingredient) for ingredient in ingredients if ingredient]


def create_product(db: Session, tenant_id: int, payload: ProductCreateRequest) -> Product:
    product = Product(
        tenant_id=tenant_id,
        name=payload.name,
        category=payload.category,
        form=payload.form,
        description=payload.description,
        price=Decimal(str(payload.price)) if payload.price is not None else None,
        weight=payload.weight,
        image_url=payload.image_url,
        is_universal=payload.is_universal,
    )
    _replace_product_children(product, payload.constitutions, payload.ingredients)
    db.add(product)
    db.flush()
    return product


def update_product(db: Session, product: Product, payload: ProductUpdateRequest) -> Product:
    update_data = payload.model_dump(exclude_unset=True)
    child_constitutions = update_data.pop("constitutions", None)
    child_ingredients = update_data.pop("ingredients", None)

    if "price" in update_data and update_data["price"] is not None:
        update_data["price"] = Decimal(str(update_data["price"]))

    for field, value in update_data.items():
        setattr(product, field, value)

    if product.is_universal:
        child_constitutions = []
    _replace_product_children(product, child_constitutions, child_ingredients)
    db.flush()
    return product


def soft_delete_product(db: Session, product: Product) -> None:
    product.is_active = False
    db.flush()
