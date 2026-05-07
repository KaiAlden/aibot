from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories.products import list_products_for_tenant
from app.repositories.tenants import get_tenant_by_code
from app.schemas import Constitution, ProductCandidate, RecommendedProduct
from app.services.product_ranking import rank_products
from app.services.recommendation_reason import build_product_reason
from app.services.redis_client import RedisClient
from app.services.tcm_retrieval import retrieve_tcm


class RecommendationError(Exception):
    pass


class MerchantNotFoundError(RecommendationError):
    pass


def product_to_candidate(product: Product) -> ProductCandidate:
    return ProductCandidate(
        id=product.id,
        name=product.name,
        form=product.form,
        price=float(product.price) if product.price is not None else None,
        image_url=product.image_url,
        description=product.description or "",
        ingredients=[item.ingredient for item in product.ingredients],
        business_weight=float(product.business_weight),
    )


def recommend_products(
    db: Session,
    merchant_code: str,
    constitution: Constitution,
    query: str,
    form: str | None = None,
    price_max: float | None = None,
    top_n: int = 5,
    redis_client: RedisClient | None = None,
) -> list[RecommendedProduct]:
    tenant = get_tenant_by_code(db, merchant_code)
    if tenant is None:
        raise MerchantNotFoundError(f"invalid merchant_code: {merchant_code}")

    products = list_products_for_tenant(
        db,
        tenant_id=tenant.id,
        constitution=constitution,
        form=form,
        price_max=price_max,
    )
    candidates = [product_to_candidate(product) for product in products]
    ranked = rank_products(candidates, query=query, constitution=constitution, redis_client=redis_client)
    candidate_by_id = {candidate.id: candidate for candidate in candidates}
    enriched: list[RecommendedProduct] = []
    for item in ranked[:top_n]:
        candidate = candidate_by_id[item.product_id]
        reason_query = " ".join(part for part in [candidate.description, candidate.name, query] if part)
        chunks = retrieve_tcm(db, reason_query, top_k=2)
        enriched.append(
            RecommendedProduct(
                product_id=item.product_id,
                name=item.name,
                score=item.score,
                reason=build_product_reason(candidate, constitution, chunks),
            )
        )
    return enriched
