import math

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

        # 거리 점수 (최대 30)
        distance_score = max(
            0,
            30 - (distance_m / 100)
        )

        # 리뷰 점수 반영 (0~5점 → 0~20점으로 스케일)
        review_score_raw = restaurant_data.get("review_score")
        review_count = restaurant_data.get("review_count")
        if review_score_raw and review_count:
            review_bonus = (
                review_score_raw *
                math.log(review_count + 1)
            )
        else:
            review_bonus = 0

        final_score = (
            keyword_score
            + distance_score
            + review_bonus
        )

        return {
            "distance_m": distance_m,
            "keyword_score": round(keyword_score, 2),
            "distance_score": round(distance_score, 2),
            "review_bonus": round(review_bonus, 2),
            "final_score": round(final_score, 2)
        }
