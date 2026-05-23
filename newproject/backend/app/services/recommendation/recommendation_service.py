from app.services.recommendation.keyword_generator import KeywordGenerator
from app.services.kakao.kakao_client import KakaoClient
from app.services.recommendation.scorer import RestaurantScorer


class RecommendationService:

    def __init__(self):
        self.keyword_generator = KeywordGenerator()
        self.kakao_client = KakaoClient()
        self.scorer = RestaurantScorer()

    def recommend(self, conditions, latitude, longitude, free_text=""):
        keywords = self.keyword_generator.generate(conditions, free_text)
        print("KEYWORDS:", keywords)

        restaurant_map = {}
        for keyword in keywords:
            results = self.kakao_client.search_places(keyword, latitude, longitude)
            print(f"{keyword} 검색 결과 수: {len(results)}")
            for place in results:
                pid = place["id"]
                if pid not in restaurant_map:
                    restaurant_map[pid] = {"place": place, "matched_keywords": set()}
                restaurant_map[pid]["matched_keywords"].add(keyword)

        final = []
        for data in restaurant_map.values():
            score_result = self.scorer.calculate_score(data, latitude, longitude)
            if score_result["final_score"] <= 0:
                continue
            place = data["place"]
            final.append({
                "name": place.get("place_name", ""),
                "address": place.get("road_address_name", ""),
                "category": place.get("category_name", ""),
                "latitude": float(place["y"]),
                "longitude": float(place["x"]),
                "score": round(score_result["final_score"], 2),
                "matched_keywords": list(data["matched_keywords"]),
                "distance_m": int(place.get("distance", 0)),
                "place_url": place.get("place_url", ""),
                "thumbnail": place.get("thumbnail", ""),
            })

        final.sort(key=lambda x: x["score"], reverse=True)
        return final
