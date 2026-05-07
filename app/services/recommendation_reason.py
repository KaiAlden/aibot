from app.schemas import Constitution, ProductCandidate, TCMChunk
from app.services.compliance import contains_medical_advice


def build_product_reason(product: ProductCandidate, constitution: Constitution, chunks: list[TCMChunk]) -> str:
    parts: list[str] = []

    if product.description:
        parts.append(f"{product.name}的商品功效描述为“{product.description}”。")
    else:
        parts.append(f"{product.name}可作为{constitution.value}用户的候选商品。")

    safe_chunks = [chunk for chunk in chunks if not contains_medical_advice(chunk.text)]
    if safe_chunks:
        source_names = "、".join(dict.fromkeys(chunk.source for chunk in safe_chunks[:2]))
        parts.append(f"可结合{source_names}中的相关养生理论作为解释依据。")
    else:
        parts.append("当前未找到可安全引用的古籍片段，建议结合个人情况谨慎选择。")

    parts.append("本建议仅作日常养生参考，不替代专业诊疗。")
    return "".join(parts)
