import json
import re

from groq import Groq

from app.core.config import GROQ_API_KEY
from app.data.food_tags import FOOD_TAGS
from app.data.condition_groups import CONDITION_GROUPS

DEFAULT_KEYWORDS = [
    "맛집",
    "식당",
    "음식점"
]

_client = Groq(api_key=GROQ_API_KEY)

GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama3-70b-8192"
]


SYSTEM_PROMPT = """
당신은 음식 추천 전문가입니다.

규칙:
- 한국에서 실제로 널리 알려진 음식만 사용한다.
- 존재 여부가 불확실한 음식은 절대 생성하지 않는다.
- 새로운 음식명을 만들지 않는다.
- 음식 종류명만 출력한다.
- 너무 구체적인 메뉴는 금지한다.
- 반드시 JSON 배열만 출력한다.
- 최대 8개 출력한다.
"""


class KeywordGenerator:

    # =========================
    # ENTRY
    # =========================
    def generate(self, condition_keys: list[str], free_text: str = "") -> list[str]:

        if free_text and free_text.strip():
            keywords = self._generate_from_free_text(free_text.strip())
            return keywords or DEFAULT_KEYWORDS

        if not condition_keys:
            return DEFAULT_KEYWORDS

        return self._generate_from_conditions(condition_keys)

    # =========================
    # MAIN
    # =========================
    def _generate_from_conditions(self, condition_keys: list[str]) -> list[str]:

        positive, negative = self._split_conditions(condition_keys)

        db_candidates = []

        for food, tags in FOOD_TAGS.items():

            if self._match_food(tags, positive, negative):
                db_candidates.append(food)

        print("[DB CANDIDATES]", db_candidates)

        if len(db_candidates) >= 5:
            return db_candidates[:8]

        prompt = self._build_condition_prompt(condition_keys, db_candidates)

        ai_candidates = self._ai_generate(prompt)

        merged = []
        seen = set()

        for food in (db_candidates + ai_candidates):

            if food in seen:
                continue

            seen.add(food)
            merged.append(food)

        return merged[:8]

    # =========================
    # FREE TEXT
    # =========================
    def _generate_from_free_text(self, free_text: str) -> list[str]:

        prompt = f"""
사용자 요청:
{free_text}

카카오맵 검색용 음식 종류를 추천하라.

규칙:
- 음식 종류만 출력
- JSON 배열만 출력
"""

        return self._ai_generate(prompt)

    # =========================
    # 🔥 핵심: CONDITION SPLIT
    # =========================
    def _split_conditions(self, condition_keys: list[str]):

        positive = set()
        negative = set()

        for c in condition_keys:

            if c.startswith("no_"):
                negative.add(c.replace("no_", ""))
            else:
                positive.add(c)

        return positive, negative

    # =========================
    # 🔥 핵심: MATCH LOGIC
    # =========================
    def _match_food(self, food_tags: set[str], positive: set[str], negative: set[str]) -> bool:

        # 1. 먼저 negative 컷 (가장 중요)
        if negative and any(tag in food_tags for tag in negative):
            return False

        # 2. positive 조건 체크
        if positive:
            return all(tag in food_tags for tag in positive)

        return True

    # =========================
    # PROMPT
    # =========================
    def _build_condition_prompt(self, condition_keys: list[str], db_candidates: list[str]) -> str:

        labels = []

        for key in condition_keys:
            condition = CONDITION_GROUPS.get(key)
            if condition:
                labels.append(condition["label"])

        prompt = ["사용자 조건:"]
        prompt.extend(f"- {label}" for label in labels)

        if db_candidates:
            prompt.append("")
            prompt.append("조건을 만족하는 음식 예시:")
            prompt.append(", ".join(db_candidates[:20]))

        prompt.append("")
        prompt.append("조건을 만족하는 실제 음식만 추천하라.")

        return "\n".join(prompt)

    # =========================
    # LLM CALL
    # =========================
    def _ai_generate(self, prompt: str) -> list[str]:

        for model in GROQ_MODELS:

            try:
                print(f"[Groq] 모델 시도: {model}")

                response = _client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2
                )

                raw = response.choices[0].message.content.strip()

                print("[RAW]", raw)

                try:
                    data = json.loads(raw)
                    if isinstance(data, list):
                        return [str(x) for x in data]
                except:
                    pass

                match = re.search(r"\[.*\]", raw, re.DOTALL)

                if match:
                    data = json.loads(match.group())
                    if isinstance(data, list):
                        return [str(x) for x in data]

            except Exception as e:
                print(f"[Groq FAIL] model={model}, error={e}")
                continue

        return []