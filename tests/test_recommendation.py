from decimal import Decimal

import pytest

from app.models.product import Product, ProductIngredient
from app.models.tenant import Tenant
from app.schemas import Constitution
from app.services import recommendation
from app.services.recommendation import MerchantNotFoundError, product_to_candidate, recommend_products


class FakeRedis:
    def hget_float(self, key: str, field: str, default: float = 0.0) -> float:
        if key == "ingredient_cache:黄芪" and field == "气虚质":
            return 0.9
        return default


class FakeDb:
    pass


def test_product_to_candidate_includes_ingredients() -> None:
    product = Product(
        id=1,
        tenant_id=1,
        name="黄芪茶",
        description="补气",
        business_weight=Decimal("1.00"),
    )
    product.ingredients = [ProductIngredient(product_id=1, ingredient="黄芪")]

    candidate = product_to_candidate(product)

    assert candidate.ingredients == ["黄芪"]


def test_recommend_products_ranks_candidates(monkeypatch) -> None:
    tenant = Tenant(id=1, merchant_code="QCT001", name="青春塘")
    product = Product(
        id=1,
        tenant_id=1,
        name="黄芪茶",
        description="补气",
        business_weight=Decimal("1.00"),
    )
    product.ingredients = [ProductIngredient(product_id=1, ingredient="黄芪")]

    monkeypatch.setattr(recommendation, "get_tenant_by_code", lambda db, merchant_code: tenant)
    monkeypatch.setattr(recommendation, "list_products_for_tenant", lambda *args, **kwargs: [product])
    monkeypatch.setattr(recommendation, "retrieve_tcm", lambda *args, **kwargs: [])

    items = recommend_products(FakeDb(), "QCT001", Constitution.qixu, "补气", redis_client=FakeRedis())

    assert items[0].product_id == 1
    assert items[0].score > 0
    assert items[0].reason != "待生成推荐理由"


def test_recommend_products_rejects_unknown_merchant(monkeypatch) -> None:
    monkeypatch.setattr(recommendation, "get_tenant_by_code", lambda db, merchant_code: None)

    with pytest.raises(MerchantNotFoundError):
        recommend_products(FakeDb(), "BAD", Constitution.qixu, "补气", redis_client=FakeRedis())
