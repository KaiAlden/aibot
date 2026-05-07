from app.schemas import Constitution, ProductCandidate
from app.services.product_ranking import rank_products


class FakeRedis:
    def hget_float(self, key: str, field: str, default: float = 0.0) -> float:
        scores = {
            ("ingredient_cache:黄芪", "气虚质"): 0.9,
            ("ingredient_cache:薄荷", "气虚质"): 0.1,
        }
        return scores.get((key, field), default)


def test_rank_products_uses_ingredient_cache() -> None:
    products = [
        ProductCandidate(id=1, name="黄芪茶", description="补气", ingredients=["黄芪"]),
        ProductCandidate(id=2, name="薄荷茶", description="清爽", ingredients=["薄荷"]),
    ]

    ranked = rank_products(products, "补气", Constitution.qixu, redis_client=FakeRedis())

    assert ranked[0].product_id == 1
