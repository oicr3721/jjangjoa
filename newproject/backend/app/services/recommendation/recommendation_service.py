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

    # ─────────────────────────────────────────────
    # 내부 헬퍼
    # ─────────────────────────────────────────────
    @staticmethod
    def _enrich(place_id: str, place_url: str) -> dict:

        if not place_url:
            return {
                "place_id": place_id,
                "detail": {}
            }

        detail = fetch_place_detail(place_url)

        return {
            "place_id": place_id,
            "detail": detail
        }
    
    @staticmethod
    def _build_matched_menus(
        keywords: list[str],
        menus: list[dict]
    ) -> dict:

        result = {}

        for keyword in keywords:

            matched = []

            for menu in menus:

                menu_name = (
                    menu.get("name", "")
                )

                if keyword in menu_name:

                    matched.append({
                        "name": menu_name,
                        "price": menu.get(
                            "price",
                            -1
                        )
                    })

            if matched:
                result[keyword] = matched

        return result

    # ─────────────────────────────────────────────
    # 메인 추천 로직
    # ─────────────────────────────────────────────
    def recommend(
        self,
        conditions,
        latitude,
        longitude,
        free_text=""
    ):

        # 조건 → 메뉴 키워드 생성
        keywords = self.keyword_generator.generate(
            conditions,
            free_text
        )

        print("KEYWORDS:", keywords)

        restaurant_map = {}

        # 키워드별 장소 검색
        for keyword in keywords:

            results = self.kakao_client.search_places(
                keyword,
                latitude,
                longitude
            )

            for place in results:

                place_id = place["id"]

                if place_id not in restaurant_map:

                    restaurant_map[place_id] = {
                        "place": place,
                        "matched_keywords": set(),
                    }

                restaurant_map[
                    place_id
                ][
                    "matched_keywords"
                ].add(keyword)

        if not restaurant_map:
            return []

        # ─────────────────────────────────────────
        # 병렬 상세정보 수집
        # ─────────────────────────────────────────
        enriched = {}

        with ThreadPoolExecutor(
            max_workers=12
        ) as pool:

            futures = {
                pool.submit(
                    self._enrich,
                    pid,
                    data["place"].get(
                        "place_url",
                        ""
                    )
                ): pid
                for pid, data
                in restaurant_map.items()
            }

            for future in as_completed(
                futures,
                timeout=10
            ):

                try:

                    res = future.result()

                    enriched[
                        res["place_id"]
                    ] = res["detail"]

                except Exception:

                    pid = futures[future]

                    enriched[pid] = {}

        # ─────────────────────────────────────────
        # 점수 계산
        # ─────────────────────────────────────────

        final_restaurants = []

        for pid, data in restaurant_map.items():

            detail = enriched.get(pid, {})

            data["review_score"] = (
                detail.get("review_score")
            )

            data["review_count"] = (
                detail.get(
                    "review_count",
                    0
                )
            )

            raw_menus = detail.get(
                "menus",
                []
            )

            matched_menus = (
                self._build_matched_menus(
                    list(
                        data[
                            "matched_keywords"
                        ]
                    ),
                    raw_menus
                )
            )

            data["menu_match_count"] = sum(
                len(v)
                for v in matched_menus.values()
            )
            data["is_open"] = detail["is_open"]

            score_result = (
                self.scorer.calculate_score(
                    data,
                    latitude,
                    longitude
                )
            )

            if (
                score_result["final_score"]
                <= 0
            ):
                continue

            place = data["place"]

            final_restaurants.append({

                "name":
                    place.get(
                        "place_name",
                        ""
                    ),

                "address":
                    place.get(
                        "road_address_name",
                        ""
                    ),

                "category":
                    place.get(
                        "category_name",
                        ""
                    ),

                "latitude":
                    float(place["y"]),

                "longitude":
                    float(place["x"]),

                "score":
                    score_result[
                        "final_score"
                    ],

                "keyword_score":
                    score_result[
                        "keyword_score"
                    ],

                "distance_score":
                    score_result[
                        "distance_score"
                    ],

                "review_bonus":
                    score_result[
                        "review_bonus"
                    ],

                "matched_keywords":
                    list(
                        data[
                            "matched_keywords"
                        ]
                    ),

                "matched_count":
                    len(
                        data[
                            "matched_keywords"
                        ]
                    ),

                "distance_m":
                    int(
                        place.get(
                            "distance",
                            0
                        )
                    ),

                "place_url":
                    place.get(
                        "place_url",
                        ""
                    ),

                # ───────── 리뷰 ─────────

                "review_score":
                    detail.get(
                        "review_score"
                    ),

                "review_count":
                    detail.get(
                        "review_count",
                        0
                    ),

                # ───────── 이미지 ─────────

                "image_url":
                    detail.get(
                        "image_url"
                    ),

                # ───────── 영업정보 ─────────

                "is_open":
                    detail.get(
                        "is_open",
                        False
                    ),

                "open_status":
                    detail.get(
                        "open_status",
                        "정보 없음"
                    ),

                "open_hours_info":
                    detail.get(
                        "open_hours_info",
                        ""
                    ),
                
                # ───────── 메뉴 검증 결과 ─────────

                "menus":
                    matched_menus,

                # ───────── 가격 ─────────

                "average_price":
                    detail.get(
                        "average_price"
                    ),

                "price_level":
                    detail.get(
                        "price_level",
                        "가격 정보 없음"
                    ),

                "price_range":
                    detail.get(
                        "price_range",
                        "가격 정보 없음"
                    ),
            })

        final_restaurants.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return final_restaurants