import json
import re
from groq import Groq

from app.data.condition_rules import CONDITION_RULES
from app.core.config import GROQ_API_KEY

DEFAULT_KEYWORDS = ["맛집", "식당", "음식점"]

# 🔥 Groq 클라이언트
_client = Groq(api_key=GROQ_API_KEY)

# 🔥 fallback 모델 리스트 (중요)
GROQ_MODELS = [
    "llama-3.3-70b-versatile",   # 최신/정확
    "llama-3.1-8b-instant",      # 빠르고 안정
    "llama3-70b-8192"            # 레거시 대체
]

SYSTEM_PROMPT = """
당신은 음식점 검색 키워드 생성기입니다.

사용자의 조건을 보고 카카오맵 검색에 적합한 음식 종류 키워드를 생성하세요.

규칙:
- 음식 종류명만 출력 (예: 국밥, 초밥, 삼겹살, 파스타)
- 너무 구체적인 요리는 금지 (바지락칼국수 X → 칼국수 O)
- 8개 이하
- 반드시 JSON 배열만 출력
- 설명 금지
- 반드시 한국어 음식명만 사용 (영어 금지, 예: bossam → 보쌈)

예:
["국밥", "삼겹살", "초밥"]
"""


class KeywordGenerator:

    def generate(self, conditions: list[str], free_text: str = "") -> list[str]:
        if free_text and free_text.strip():
            return self._ai_generate(free_text.strip())

        if not conditions:
            return DEFAULT_KEYWORDS

        rule_context = self._build_rule_context(conditions)
        return self._ai_generate(rule_context)

    def _build_rule_context(self, conditions: list[str]) -> str:
        include_set = set()
        exclude_set = set()

        for cond in conditions:
            rule = CONDITION_RULES.get(cond)
            if not rule:
                continue
            include_set.update(rule.get("include", []))
            exclude_set.update(rule.get("exclude", []))

        include_list = list(include_set - exclude_set)
        exclude_list = list(exclude_set)

        parts = [f"선택 조건: {', '.join(conditions)}"]

        if include_list:
            parts.append(f"추천 음식 힌트: {', '.join(include_list[:12])}")

        if exclude_list:
            parts.append(f"제외 음식: {', '.join(exclude_list[:8])}")

        return " / ".join(parts)

    def _ai_generate(self, user_input: str) -> list[str]:

        #  모델 fallback 루프
        for model in GROQ_MODELS:
            try:
                print(f"[Groq] 모델 시도: {model}")

                response = _client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_input}
                    ],
                    temperature=0.2,
                )

                raw = response.choices[0].message.content.strip()
                print(f"[Groq RAW] {raw}")

                # 1차 JSON 파싱
                try:
                    data = json.loads(raw)
                    if isinstance(data, list):
                        return [str(x) for x in data]
                except:
                    pass

                # 2차 regex 파싱
                match = re.search(r"\[.*\]", raw, re.DOTALL)
                if match:
                    data = json.loads(match.group())
                    if isinstance(data, list):
                        return [str(x) for x in data]

            except Exception as e:
                print(f"[Groq FAIL] model={model}, error={e}")
                continue  #  다음 모델로 이동

        #  모든 모델 실패 시 fallback
        print("[Groq] 모든 모델 실패 → DEFAULT_KEYWORDS 반환")
        return DEFAULT_KEYWORDS