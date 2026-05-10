"""
summarizer.py

Groq API를 사용한 한국어 공지사항 요약기.
LLaMA 3.3 70B 모델 사용 (한국어 품질 우수, 무료 한도 넉넉)

설치:
    pip install groq

API 키 설정:
    GROQ_API_KEY 변수에 발급받은 키를 입력하세요.
"""

from groq import Groq


# ── API 키 설정 ───────────────────────────────────────────────────────────────

GROQ_API_KEY = "이 곳에 Groq API 키를 입력"

# ── 모델 설정 ─────────────────────────────────────────────────────────────────

GROQ_MODEL = "llama-3.3-70b-versatile"  # 한국어 품질 가장 좋은 무료 모델

SUMMARIZE_PROMPT = """다음은 게임 공지사항 텍스트입니다. 핵심 내용을 3~5줄로 요약해주세요.

요약 규칙:
- 이벤트 기간, 보상, 변경사항, 점검 일정 등 중요한 정보를 반드시 포함
- 날짜와 수치는 정확하게 유지
- 자연스러운 한국어 문장으로 작성
- 요약문만 출력하고 설명이나 머리말은 제외

공지사항:
{text}

요약:"""

# ── 클라이언트 초기화 (최초 1회) ─────────────────────────────────────────────

_client = None


def _load_client():
    global _client
    if _client is not None:
        return

    if not GROQ_API_KEY or GROQ_API_KEY == "여기에_API_키_입력":
        raise ValueError(
            "GROQ_API_KEY가 설정되지 않았습니다.\n"
            "summarizer.py 상단의 GROQ_API_KEY에 발급받은 키를 입력하세요."
        )

    _client = Groq(api_key=GROQ_API_KEY)


# ── 요약 ─────────────────────────────────────────────────────────────────────

def summarize_with_groq(text: str, max_input_chars: int = 3000) -> str:
    if not text or not text.strip():
        return "요약할 내용이 없습니다."

    try:
        _load_client()
    except ValueError as e:
        return f"[오류] {e}"

    if len(text) > max_input_chars:
        text = text[:max_input_chars] + "\n...(이하 생략)"

    prompt = SUMMARIZE_PROMPT.format(text=text)

    try:
        response = _client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=512,
        )
        summary = response.choices[0].message.content.strip()

        if not summary:
            return "요약 결과가 비어있습니다."

        return summary

    except Exception as e:
        return f"[오류] 요약 실패: {e}"


def summarize_text(text: str) -> str:
    """외부에서 호출하는 메인 함수."""
    return summarize_with_groq(text)


# ── 직접 실행 시 동작 확인 ───────────────────────────────────────────────────

if __name__ == "__main__":
    sample = """
    메이플스토리 2025년 5월 정기 점검 안내입니다.
    점검 일시는 5월 14일 오전 6시부터 오전 11시까지이며,
    점검 보상으로 경험치 2배 쿠폰 1장이 지급될 예정입니다.
    점검 중에는 게임 접속이 불가하오니 양해 부탁드립니다.
    """
    print("=== 요약 테스트 ===")
    result = summarize_text(sample)
    print(result)