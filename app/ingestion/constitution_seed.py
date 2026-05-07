from dataclasses import dataclass

from app.schemas import Constitution


@dataclass(frozen=True)
class ConstitutionSymptomSeed:
    constitution: Constitution
    symptom_text: str


CONSTITUTION_SYMPTOMS: list[ConstitutionSymptomSeed] = [
    ConstitutionSymptomSeed(
        Constitution.pinghe,
        "精力充沛，睡眠良好，食欲正常，面色红润，性格平和，较少疲劳或生病。",
    ),
    ConstitutionSymptomSeed(
        Constitution.qixu,
        "容易疲乏，气短懒言，出汗较多，声音低弱，活动后不适明显，容易感冒。",
    ),
    ConstitutionSymptomSeed(
        Constitution.yangxu,
        "怕冷，手脚冰凉，喜热饮，大便偏稀，精神不振，腹部或腰膝发冷。",
    ),
    ConstitutionSymptomSeed(
        Constitution.yinxu,
        "口燥咽干，手足心热，潮热盗汗，眼睛干涩，大便偏干，睡眠不安。",
    ),
    ConstitutionSymptomSeed(
        Constitution.tanshi,
        "体形偏胖，腹部松软，口黏，痰多，胸闷，容易困倦，喜食肥甘。",
    ),
    ConstitutionSymptomSeed(
        Constitution.shire,
        "面部油腻，口苦口干，易长痘，小便短黄，大便黏滞，容易急躁。",
    ),
    ConstitutionSymptomSeed(
        Constitution.xueyu,
        "肤色晦暗，唇色偏暗，容易出现瘀斑，身体刺痛或固定疼痛，舌质偏暗。",
    ),
    ConstitutionSymptomSeed(
        Constitution.qiyu,
        "情绪低落，容易紧张焦虑，胸胁胀满，常叹气，睡眠较差，对压力敏感。",
    ),
    ConstitutionSymptomSeed(
        Constitution.tebing,
        "过敏体质，容易鼻塞喷嚏、皮肤风团或瘙痒，对花粉、食物、气味较敏感。",
    ),
]
