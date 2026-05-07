from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tenant import Tenant


def get_tenant_by_id(db: Session, tenant_id: int) -> Tenant | None:
    return db.get(Tenant, tenant_id)


def get_tenant_by_code(db: Session, merchant_code: str) -> Tenant | None:
    return db.scalar(select(Tenant).where(Tenant.merchant_code == merchant_code))


def get_or_create_tenant(db: Session, merchant_code: str, name: str, field_mapping: str | None = None) -> Tenant:
    tenant = get_tenant_by_code(db, merchant_code)
    if tenant is not None:
        return tenant

    tenant = Tenant(merchant_code=merchant_code, name=name, field_mapping=field_mapping)
    db.add(tenant)
    db.flush()
    return tenant


def update_tenant_field_mapping(db: Session, tenant: Tenant, field_mapping: str) -> Tenant:
    tenant.field_mapping = field_mapping
    db.flush()
    return tenant
