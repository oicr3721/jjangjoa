from bs4 import BeautifulSoup
import requests


def crawl_content(url: str, config: dict) -> str:
    """
    공지사항 URL에서 본문 HTML을 가져온다.

    config에서 "content_selectors" (리스트) 또는
    "content_selector" (단수 문자열) 둘 다 지원한다.
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # content_selectors (리스트) 와 content_selector (단수) 둘 다 허용
    selectors = config.get("content_selectors") or []
    single = config.get("content_selector")
    if single and single not in selectors:
        selectors = [single] + selectors

    # selector 순차 탐색
    for selector in selectors:
        content = soup.select_one(selector)
        if content:
            print(f"selector success: {selector}")
            return str(content)

    # fallback: 텍스트가 가장 긴 블록 탐색
    print("selector failed -> fallback search")

    candidates = soup.find_all(["article", "div", "section"])
    best = None
    best_len = 0

    for tag in candidates:
        text_len = len(tag.get_text(" ", strip=True))
        if text_len > best_len:
            best = tag
            best_len = text_len

    if best:
        print(f"fallback content found (길이: {best_len})")
        return str(best)

    return ""
