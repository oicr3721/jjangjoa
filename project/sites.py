SITE_CONFIG = {

    "maplestory": {
        "list_url": "https://maplestory.nexon.com/News/Notice",
        "base_url": "https://maplestory.nexon.com",

        "item_selector": ".news_board li",
        "title_selector": "a",
        "date_selector": ".heart_date dd",
        "link_selector": "a"
    },

    "valorant": {
        "list_url": "https://playvalorant.com/ko-kr/news/",
        "base_url": "https://playvalorant.com",

        "item_selector": 'a[data-testid="articlefeaturedcard-component"]',
        "title_attr": "aria-label",
        "date_selector": "time"
    }
}