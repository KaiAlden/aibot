from app.config.settings import settings
from app.schemas.core import Constitution, ProductCandidate, RecommendedProduct
from app.services.redis_client import RedisClient


def text_relevance(query: str, product: ProductCandidate) -> float:
    if not query:
        return 0.0
    haystack = f"{product.name} {product.description}".lower()
    tokens = [token for token in query.lower().split() if token]
    if not tokens:
        return 0.0
    return sum(1 for token in tokens if token in haystack) / len(tokens)


def rank_products(
    candidates: list[ProductCandidate],
    query: str,
    constitution: Constitution,
    redis_client: RedisClient | None = None,
) -> list[RecommendedProduct]:
    redis_client = redis_client or RedisClient()
    ranked: list[RecommendedProduct] = []

    for product in candidates:
        ingredient_scores = [
            redis_client.hget_float(f"ingredient_cache:{ingredient}", constitution.value, default=0.0)
            for ingredient in product.ingredients
        ]
        tcm_score = sum(ingredient_scores) / len(ingredient_scores) if ingredient_scores else 0.0
        score = (
            text_relevance(query, product) * settings.product_text_weight
            + tcm_score * settings.product_tcm_weight
            + product.business_weight * settings.product_business_weight
        )
        ranked.append(
            RecommendedProduct(
                product_id=product.id,
                name=product.name,
                score=round(score, 4),
                reason="待生成推荐理由",
            )
        )

    return sorted(ranked, key=lambda item: item.score, reverse=True)
