"""
cleaner.py

HTML → 정제된 텍스트 변환 모듈.

핵심 전략:
  - 블록 태그(p, li, h1~h6 등) 경계에서만 줄바꿈
  - div는 내부에 블록 자식이 없을 때만 인라인 컨테이너로 취급
  - span 등 인라인 태그 안 텍스트는 공백 없이 이어붙여 쪼개진 글자 복원
"""

import re
from bs4 import BeautifulSoup, NavigableString, Tag


# 줄바꿈을 유발하는 블록 태그 (div는 별도 처리)
BLOCK_TAGS = {
    "p", "li", "ul", "ol", "br",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "section", "article", "header", "footer",
    "table", "tr", "td", "th",
    "blockquote", "pre", "hr",
}

# 완전히 건너뛸 태그
SKIP_TAGS = {"script", "style", "noscript", "iframe", "svg", "img"}


def _has_block_child(tag: Tag) -> bool:
    """태그의 직계 자식 중 블록 요소(div 포함)가 있으면 True."""
    for child in tag.children:
        if isinstance(child, Tag):
            name = child.name.lower() if child.name else ""
            if name in BLOCK_TAGS or name == "div":
                return True
    return False


def _walk(node, lines: list, buf: list):
    """
    DOM을 재귀 순회하며 텍스트를 수집한다.

    buf  : 현재 블록 안에 쌓이는 인라인 텍스트 조각
    lines: flush 완료된 줄들
    """

    if isinstance(node, NavigableString):
        text = str(node)
        if text.strip():
            buf.append(text)
        return

    if not isinstance(node, Tag):
        return

    tag_name = node.name.lower() if node.name else ""

    if tag_name in SKIP_TAGS:
        return

    # div 전용 처리:
    # - 블록 자식이 있으면 → 블록처럼 flush 하고 자식 순회
    # - 블록 자식이 없으면 → 인라인처럼 buf에 계속 쌓음
    if tag_name == "div":
        if _has_block_child(node):
            _flush(buf, lines)
            for child in node.children:
                _walk(child, lines, buf)
            _flush(buf, lines)
        else:
            for child in node.children:
                _walk(child, lines, buf)
        return

    if tag_name in BLOCK_TAGS:
        _flush(buf, lines)
        for child in node.children:
            _walk(child, lines, buf)
        _flush(buf, lines)
    else:
        # 인라인 요소 (span, a, strong, em 등) → 그냥 자식 순회
        for child in node.children:
            _walk(child, lines, buf)


def _flush(buf: list, lines: list):
    """buf 조각들을 이어붙여 한 줄로 만들고 lines에 추가."""
    if not buf:
        return

    combined = "".join(buf).strip()

    if combined:
        lines.append(combined)

    buf.clear()


def extract_text_by_blocks(html: str) -> str:
    """HTML → 블록 단위 재조립 텍스트."""

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.find_all(list(SKIP_TAGS)):
        tag.decompose()

    lines: list = []
    buf: list = []
    _walk(soup, lines, buf)
    _flush(buf, lines)  # 마지막 잔여 flush

    result_lines = [line.strip() for line in lines if line.strip()]
    return "\n".join(result_lines)


def clean_text(text: str) -> str:
    """extract_text_by_blocks() 결과를 후처리로 정제."""

    # 1. 특수 공백 / 제로폭 문자
    text = text.replace("\xa0", " ")
    text = re.sub(r"[\u200b-\u200d\ufeff]", "", text)

    # 2. HTML 태그 잔재
    text = re.sub(r"<[^>]+>", " ", text)

    # 3. URL 제거
    text = re.sub(r"https?://\S+", "", text)

    # 4. 특수문자 반복 제거
    text = re.sub(r"[-=_*]{3,}", " ", text)

    # 5. 줄 단위 정리
    lines = []
    for line in text.splitlines():
        line = line.strip()

        if len(line) <= 1:
            continue

        # 같은 문자만 반복되는 줄 제거 (ㅡㅡㅡ, .... 등)
        if re.fullmatch(r"(.)\1{2,}", line):
            continue

        line = re.sub(r"[ \t]+", " ", line)
        lines.append(line)

    text = "\n".join(lines)

    # 6. 연속 빈 줄 압축
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 7. 쪼개진 숫자+단위 복원 ("2 0 2 5 년" → "2025년")
    text = re.sub(
        r"(\d)(\s\d){1,}(\s*[년월일시분])",
        lambda m: re.sub(r"\s", "", m.group(0)),
        text,
    )

    return text.strip()


def html_to_clean_text(html: str) -> str:
    """외부에서 호출하는 메인 함수: HTML → 정제된 텍스트."""
    raw_text = extract_text_by_blocks(html)
    return clean_text(raw_text)
