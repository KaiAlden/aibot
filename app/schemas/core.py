from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class Constitution(str, Enum):
    pinghe = "平和质"
    qixu = "气虚质"
    yangxu = "阳虚质"
    yinxu = "阴虚质"
    tanshi = "痰湿质"
    shire = "湿热质"
    xueyu = "血瘀质"
    qiyu = "气郁质"
    tebing = "特禀质"


class SessionContext(BaseModel):
    constitution: Constitution | None = None
    preferences: dict = Field(default_factory=dict)
    chat_history: list[dict] = Field(default_factory=list)


class SymptomMatchResult(BaseModel):
    constitution: Constitution | None = None
    confidence: float
    evidence: str
    need_followup: bool = False
    followup_question: str | None = None
    top_constitutions: list[Constitution] = Field(default_factory=list)


class IntentResult(BaseModel):
    intent: Literal["product", "tcm", "unknown"]
    constraints: dict = Field(default_factory=dict)


class ProductCandidate(BaseModel):
    id: int
    name: str
    form: str | None = None
    price: float | None = None
    image_url: str | None = None
    description: str = ""
    ingredients: list[str] = Field(default_factory=list)
    business_weight: float = 1.0


class RecommendedProduct(BaseModel):
    product_id: int
    name: str
    score: float
    reason: str


class TCMChunk(BaseModel):
    text: str
    source: str
    score: float
