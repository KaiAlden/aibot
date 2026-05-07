from sqlalchemy.sql import Select

from app.repositories.products import build_product_query
from app.schemas import Constitution


def test_product_query_always_filters_tenant() -> None:
    query: Select = build_product_query(tenant_id=12, constitution=Constitution.qixu)
    compiled = str(query.compile(compile_kwargs={"literal_binds": True}))

    assert "products.tenant_id = 12" in compiled
    assert "product_constitution.constitution = '气虚质'" in compiled
