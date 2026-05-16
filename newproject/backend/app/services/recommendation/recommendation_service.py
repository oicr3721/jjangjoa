from app.services.recommendation.keyword_generator import (
    KeywordGenerator
)

from app.services.kakao.kakao_client import (
    KakaoClient
)

from app.services.recommendation.scorer import (
    RestaurantScorer
)


class RecommendationService:

    def __init__(self):

        self.keyword_generator = KeywordGenerator()
        self.kakao_client = KakaoClient()
        self.scorer = RestaurantScorer()

    def recommend(
        self,
        conditions,
        latitude,
        longitude
    ):

        # 조건 → 메뉴 키워드 생성
        keywords = self.keyword_generator.generate(
            conditions
        )

        print("KEYWORDS:", keywords)

        restaurant_map = {}

        # 키워드별 카카오 장소 검색
        for keyword in keywords:

            results = self.kakao_client.search_places(
                keyword,
                latitude,
                longitude
            )

            print(f"{keyword} 검색 결과 수:", len(results))

            for place in results:

                place_id = place["id"]

                # 최초 등장 식당 저장
                if place_id not in restaurant_map:

                    restaurant_map[place_id] = {
                        "place": place,
                        "matched_keywords": set()
                    }

                # 어떤 키워드에 매칭됐는지 저장
                restaurant_map[place_id][
                    "matched_keywords"
                ].add(keyword)

        final_restaurants = []

        # 식당 점수 계산
        for data in restaurant_map.values():

            score_result = self.scorer.calculate_score(
                data,
                latitude,
                longitude
            )

            #print(score_result)

            # 점수 0 이하 제거
            if score_result["final_score"] <= 0:
                continue

            place = data["place"]

            final_restaurants.append({
                "name": place.get("place_name", ""),
                "address": place.get(
                    "road_address_name",
                    ""
                ),
                "category": place.get(
                    "category_name",
                    ""
                ),
                "latitude": float(place["y"]),
                "longitude": float(place["x"]),
                "score": round(
                    score_result["final_score"],
                    2
                ),
                "matched_keywords": list(
                    data["matched_keywords"]
                ),
                "distance_m": int(
                    place.get("distance", 0)
                ),
                "place_url": place.get(
                    "place_url",
                    ""
                )
            })

        # 점수순 정렬
        final_restaurants.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        print("FINAL RESTAURANTS:")
        print(final_restaurants)

        return final_restaurants