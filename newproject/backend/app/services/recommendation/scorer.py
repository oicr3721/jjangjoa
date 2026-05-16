class RestaurantScorer:

    def calculate_score(
        self,
        restaurant_data,
        user_lat,
        user_lng
    ):

        place = restaurant_data["place"]

        matched_count = len(
            restaurant_data["matched_keywords"]
        )

        keyword_score = matched_count * 10

        # 카카오 distance 사용 (meter)
        distance_m = int(
            place.get("distance", 9999)
        )

        # 거리 점수
        distance_score = max(
            0,
            30 - (distance_m / 100)
        )

        final_score = (
            keyword_score
            + distance_score
        )

        return {
            "distance_m": distance_m,
            "final_score": round(
                final_score,
                2
            )
        }