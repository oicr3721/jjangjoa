FOOD_TAGS = {

    # ======================
    # 매운 식사
    # ======================
    "제육볶음": {"spicy", "meal", "hearty", "solo"},
    "제육덮밥": {"spicy", "meal", "hearty", "solo"},
    "김치찌개": {"spicy", "meal", "hearty", "solo"},
    "부대찌개": {"spicy", "meal", "hearty", "group"},
    "닭갈비": {"spicy", "meal", "hearty", "group"},
    "닭발": {"spicy", "drinking", "group"},
    "떡볶이": {"spicy", "snack"},

    # ======================
    # 안 매운 식사
    # ======================
    "국밥": {"no_spicy", "meal", "hearty", "solo"},
    "곰탕": {"no_spicy", "meal", "hearty", "solo"},
    "설렁탕": {"no_spicy", "meal", "hearty", "solo"},
    "백반": {"meal", "solo", "hearty"},
    "비빔밥": {"meal", "solo"},
    "돈까스": {"meal", "solo", "no_spicy"},
    "삼겹살": {"meal", "group", "no_spicy"},
    "갈비": {"meal", "group", "no_spicy"},

    # ======================
    # 면
    # ======================
    "짬뽕": {"spicy", "meal", "noodle", "seafood"},
    "우동": {"meal", "solo", "no_spicy", "noodle"},
    "라멘": {"meal", "solo", "noodle"},
    "라면": {"spicy", "meal", "solo", "noodle"},
    "칼국수": {"meal", "solo", "no_spicy", "noodle"},
    "쌀국수": {"meal", "solo", "noodle"},

    # ======================
    # 해산물
    # ======================
    "회": {"raw", "seafood", "group", "drinking"},
    "초밥": {"meal", "raw", "seafood", "date"},
    "오마카세": {"date", "quiet", "seafood"},

    # ======================
    # 양식
    # ======================
    "파스타": {"meal", "date", "noodle"},
    "스테이크": {"meal", "date", "hearty"},
    "피자": {"meal", "group"},
    "브런치": {"snack", "date", "quiet"},
    "샌드위치": {"snack", "light", "solo"},
    "샐러드": {"light", "solo"},

    # ======================
    # 술
    # ======================
    "곱창": {"group", "drinking", "hearty"},
    "이자카야": {"group", "drinking"},
    "호프집": {"group", "drinking", "hearty"},
}