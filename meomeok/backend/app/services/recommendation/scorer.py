import math


FINAL_CONDITION_WEIGHT = 0.7
FINAL_POPULARITY_WEIGHT = 0.3


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

        distance_m = int(
            place.get("distance", 9999)
        )

        distance_score = max(
            0,
            30 - (distance_m / 100)
        )

        review_score_raw = restaurant_data.get(
            "review_score"
        )

        review_count = restaurant_data.get(
            "review_count",
            0
        )

        if review_score_raw and review_count:

            review_bonus = (
                review_score_raw *
                math.log(review_count + 1)
            )

        else:
            review_bonus = 0

        matched_menu_count = restaurant_data.get(
            "matched_menu_count",
            0
        )

        menu_bonus = min(
            matched_menu_count * 2,
            15
        )

        is_open = restaurant_data.get(
            "is_open",
            False
        )

        open_bonus = 5 if is_open else -30

        condition_score = (
            keyword_score
            + distance_score
            + review_bonus
            + menu_bonus
            + open_bonus
        )

        popularity_score = restaurant_data.get(
            "popularity_score",
            0
        )

        final_score = (
            condition_score
            * FINAL_CONDITION_WEIGHT
            +
            popularity_score
            * FINAL_POPULARITY_WEIGHT
        )

        return {
            "distance_m": distance_m,

            "keyword_score":
                round(keyword_score, 2),

            "distance_score":
                round(distance_score, 2),

            "review_bonus":
                round(review_bonus, 2),

            "menu_bonus":
                round(menu_bonus, 2),

            "open_bonus":
                round(open_bonus, 2),

            "condition_score":
                round(condition_score, 2),

            "popularity_score":
                round(popularity_score, 2),

            "final_score":
                round(final_score, 2)
        }