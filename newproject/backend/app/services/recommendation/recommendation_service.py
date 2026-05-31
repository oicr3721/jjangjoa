from concurrent.futures import ThreadPoolExecutor, as_completed

from app.services.recommendation.keyword_generator import KeywordGenerator
from app.services.kakao.kakao_client import KakaoClient
from app.services.kakao.kakao_scraper import fetch_place_detail
from app.services.recommendation.scorer import RestaurantScorer


class RecommendationService:

    def __init__(self):
        self.keyword_generator = KeywordGenerator()
        self.kakao_client = KakaoClient()
        self.scorer = RestaurantScorer()

    # ── 내부 헬퍼: 단일 장소 크롤링 ──────────────────────────────────
    @staticmethod
    def _enrich(place_id: str, place_url: str) -> dict:
        """place_url 에서 review_score, image_url 을 가져온다."""
        if not place_url:
            return {"place_id": place_id, "review_score": None, "image_url": None}
        detail = fetch_place_detail(place_url)
        return {
            "place_id": place_id,
            "review_score": detail.get("review_score"),
            "review_count" : detail.get("review_count"),
            "image_url": detail.get("image_url"),
        }

    # ── 메인 추천 로직 ────────────────────────────────────────────────
    def recommend(self, conditions, latitude, longitude, free_text=""):

        # 조건 → 메뉴 키워드 생성
        keywords = self.keyword_generator.generate(conditions, free_text)
        print("KEYWORDS:", keywords)

        restaurant_map = {}

        # 키워드별 카카오 장소 검색
        for keyword in keywords:
            results = self.kakao_client.search_places(keyword, latitude, longitude)
            for place in results:
                place_id = place["id"]
                if place_id not in restaurant_map:
                    restaurant_map[place_id] = {
                        "place": place,
                        "matched_keywords": set(),
                    }
                restaurant_map[place_id]["matched_keywords"].add(keyword)

        if not restaurant_map:
            return []

        # ── 병렬 크롤링 (최대 12 스레드, 타임아웃 관대하게) ──────────
        enriched = {}  # place_id → {review_score, image_url}
        with ThreadPoolExecutor(max_workers=12) as pool:
            futures = {
                pool.submit(
                    self._enrich,
                    pid,
                    data["place"].get("place_url", "")
                ): pid
                for pid, data in restaurant_map.items()
            }
            for future in as_completed(futures, timeout=10):
                try:
                    res = future.result()
                    enriched[res["place_id"]] = {
                        "review_score": res["review_score"],
                        "review_count": res["review_count"],
                        "image_url": res["image_url"],
                    }
                except Exception:
                    pid = futures[future]
                    enriched[pid] = {"review_score": None, "review_count": 0, "image_url": None}

        # ── 점수 계산 → 최종 목록 빌드 ───────────────────────────────
        final_restaurants = []

        for pid, data in restaurant_map.items():
            ext = enriched.get(pid, {})
            data["review_score"] = ext.get("review_score")
            data["review_count"] = ext.get("review_count", 0)

            score_result = self.scorer.calculate_score(data, latitude, longitude)

            if score_result["final_score"] <= 0:
                continue

            place = data["place"]
            final_restaurants.append({
                "name": place.get("place_name", ""),
                "address": place.get("road_address_name", ""),
                "category": place.get("category_name", ""),
                "latitude": float(place["y"]),
                "longitude": float(place["x"]),
                "score": score_result["final_score"],
                "keyword_score": score_result["keyword_score"],
                "distance_score": score_result["distance_score"],
                "review_bonus": score_result["review_bonus"],
                "matched_keywords": list(data["matched_keywords"]),
                "matched_count": len(data["matched_keywords"]),
                "distance_m": int(place.get("distance", 0)),
                "place_url": place.get("place_url", ""),
                "review_score": data["review_score"],
                "review_count": data.get("review_count", 0),
                "image_url": ext.get("image_url"),
            })

        # 기본: 최적순(최종 점수 내림차순)
        final_restaurants.sort(key=lambda x: x["score"], reverse=True)

        return final_restaurants
