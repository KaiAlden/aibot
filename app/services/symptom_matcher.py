from dataclasses import dataclass

from app.config.settings import settings
from app.ingestion.constitution_seed import CONSTITUTION_SYMPTOMS
from app.schemas import Constitution, SymptomMatchResult


@dataclass(frozen=True)
class SymptomScore:
    constitution: Constitution
    score: float
    evidence: str


SYMPTOM_KEYWORDS: dict[Constitution, set[str]] = {
    Constitution.pinghe: {"精力充沛", "睡眠良好", "食欲正常", "面色红润"},
    Constitution.qixu: {"疲乏", "乏力", "气短", "懒言", "出汗", "容易感冒", "声音低"},
    Constitution.yangxu: {"怕冷", "手脚冰凉", "喜热饮", "喝热水", "大便稀", "腰膝发冷", "畏寒"},
    Constitution.yinxu: {"口干", "咽干", "手足心热", "盗汗", "眼干", "大便干"},
    Constitution.tanshi: {"体胖", "口黏", "痰多", "胸闷", "困倦", "腹部松软"},
    Constitution.shire: {"油腻", "口苦", "长痘", "小便黄", "大便黏", "急躁"},
    Constitution.xueyu: {"肤色晦暗", "瘀斑", "刺痛", "固定疼痛", "舌暗", "唇色暗"},
    Constitution.qiyu: {"情绪低落", "焦虑", "紧张", "胸胁胀", "叹气", "压力"},
    Constitution.tebing: {"过敏", "鼻塞", "喷嚏", "瘙痒", "风团", "花粉"},
}


def score_symptoms(query: str) -> list[SymptomScore]:
    scores: list[SymptomScore] = []
    for seed in CONSTITUTION_SYMPTOMS:
        keywords = SYMPTOM_KEYWORDS[seed.constitution]
        matched = [keyword for keyword in keywords if keyword in query]
        score = min(1.0, len(matched) / 3)
        if matched:
            evidence = "、".join(matched)
        else:
            evidence = seed.symptom_text
        scores.append(SymptomScore(seed.constitution, score, evidence))
    return sorted(scores, key=lambda item: item.score, reverse=True)


def build_followup_question(top_scores: list[SymptomScore]) -> str:
    names = "、".join(score.constitution.value for score in top_scores[:2])
    return f"您的描述可能接近{names}，请再补充是否有怕冷、乏力、口干、胸闷或情绪压力等表现。"


def match_constitution(query: str) -> SymptomMatchResult:
    scores = score_symptoms(query)
    best = scores[0]
    top_constitutions = [score.constitution for score in scores[:2] if score.score > 0]

    if best.score >= settings.symptom_high_confidence:
        return SymptomMatchResult(
            constitution=best.constitution,
            confidence=best.score,
            evidence=f"匹配到症状：{best.evidence}",
            need_followup=False,
            top_constitutions=top_constitutions,
        )

    if best.score >= settings.symptom_low_confidence:
        return SymptomMatchResult(
            constitution=best.constitution,
            confidence=best.score,
            evidence=f"匹配到症状：{best.evidence}",
            need_followup=True,
            followup_question=build_followup_question(scores),
            top_constitutions=top_constitutions,
        )

    return SymptomMatchResult(
        constitution=None,
        confidence=best.score,
        evidence="症状描述不足或不在日常体质调理范围内",
        need_followup=True,
        followup_question="请再描述一下主要感受，例如怕冷、乏力、口干、胸闷、睡眠或情绪情况。",
        top_constitutions=top_constitutions,
    )
