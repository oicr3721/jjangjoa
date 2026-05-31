"""
카카오맵 식당 상세 정보 수집기

수집 항목
- 리뷰 평점
- 리뷰 수
- 음식 사진 URL (우선)
- 일반 사진 URL (fallback)

멀티스레드 크롤링 대응
"""

import logging
import re
from typing import Optional, TypedDict
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter


# -----------------------------
# Logging
# -----------------------------
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger(__name__)


# -----------------------------
# Headers
# -----------------------------
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/148.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://place.map.kakao.com/",
    "Origin": "https://place.map.kakao.com",
    "pf": "PC",
    "appversion": "6.6.0",
}


# -----------------------------
# Session
# -----------------------------
SESSION = requests.Session()

adapter = HTTPAdapter(
    pool_connections=100,
    pool_maxsize=100,
)

SESSION.mount("http://", adapter)
SESSION.mount("https://", adapter)

SESSION.headers.update(HEADERS)


# -----------------------------
# Types
# -----------------------------
class PlaceDetail(TypedDict):
    review_score: Optional[float]
    review_count: int
    image_url: Optional[str]


# -----------------------------
# Utils
# -----------------------------
def extract_place_id(place_url: str) -> Optional[str]:
    """
    지원 예시

    https://place.map.kakao.com/123456
    https://place.map.kakao.com/123456?entry=pll
    https://place.map.kakao.com/123456/
    """

    try:
        path = urlparse(place_url).path

        match = re.search(r"(\d+)", path)

        if match:
            return match.group(1)

    except Exception:
        logger.exception("place_id parse failed")

    return None


def safe_get_json(url: str) -> Optional[dict]:
    try:
        response = SESSION.get(
            url,
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    except Exception:
        logger.exception("request failed: %s", url)

    return None


# -----------------------------
# Review
# -----------------------------
def fetch_review_info(
    place_id: str
) -> tuple[Optional[float], int]:

    url = (
        f"https://place-api.map.kakao.com/"
        f"places/tab/reviews/kakaomap/{place_id}"
        f"?order=RECOMMENDED&only_photo_review=false"
    )

    data = safe_get_json(url)

    if not data:
        return None, 0

    score_set = data.get("score_set")

    if not isinstance(score_set, dict):
        return None, 0

    try:
        score = score_set.get("average_score")
        count = score_set.get("review_count", 0)

        return (
            float(score) if score is not None else None,
            int(count)
        )

    except Exception:
        logger.exception(
            "review parsing failed (%s)",
            place_id
        )

    return None, 0


# -----------------------------
# Photos
# -----------------------------
def fetch_photo(
    place_id: str,
    food_only: bool = True
) -> Optional[str]:

    if food_only:
        url = (
            f"https://place-api.map.kakao.com/"
            f"places/tab/photos/{place_id}"
            f"?tag=FOOD&page=1"
        )
    else:
        url = (
            f"https://place-api.map.kakao.com/"
            f"places/tab/photos/{place_id}"
            f"?page=1"
        )

    data = safe_get_json(url)

    if not data:
        return None

    photos = data.get("photos")

    if not isinstance(photos, list):
        return None

    if not photos:
        return None

    first_photo = photos[0]

    if not isinstance(first_photo, dict):
        return None

    return first_photo.get("url")


# -----------------------------
# Main
# -----------------------------
def fetch_place_detail(
    place_url: str
) -> PlaceDetail:

    result: PlaceDetail = {
        "review_score": None,
        "review_count": 0,
        "image_url": None,
    }

    place_id = extract_place_id(place_url)

    if not place_id:
        return result

    review_score, review_count = (
        fetch_review_info(place_id)
    )

    result["review_score"] = review_score
    result["review_count"] = review_count

    image_url = fetch_photo(
        place_id,
        food_only=True
    )

    if image_url is None:
        image_url = fetch_photo(
            place_id,
            food_only=False
        )

    result["image_url"] = image_url

    return result