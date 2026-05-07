from sqlalchemy import func, select

from app.db.session import SessionLocal
from app.models.product import Product, ProductConstitution
from app.repositories.tenants import get_tenant_by_code


def check_qingchuntang() -> dict[str, int]:
    with SessionLocal() as db:
        tenant = get_tenant_by_code(db, "QCT001")
        if tenant is None:
            return {"tenants": 0, "products": 0, "constitution_links": 0}

        product_count = db.scalar(select(func.count()).select_from(Product).where(Product.tenant_id == tenant.id)) or 0
        link_count = (
            db.scalar(
                select(func.count())
                .select_from(ProductConstitution)
                .join(Product)
                .where(Product.tenant_id == tenant.id)
            )
            or 0
        )
        return {"tenants": 1, "products": product_count, "constitution_links": link_count}


if __name__ == "__main__":
    print(check_qingchuntang())
