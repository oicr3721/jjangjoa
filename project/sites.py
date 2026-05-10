SITE_CONFIG = {

    "maplestory": {

        "list_url": "https://maplestory.nexon.com/News/Notice",
        "base_url": "https://maplestory.nexon.com",

        "item_selector": ".news_board li",
        "title_selector": "a",
        "date_selector": ".heart_date dd",
        "link_selector": "a",

        # content_selector → content_selectors 로 통일 (복수 리스트)
        "content_selectors": [
            ".se-contents",
            ".news_contents",
            ".article_view",
        ],
    },

    "valorant": {

        "list_url": "https://playvalorant.com/ko-kr/news/",
        "base_url": "https://playvalorant.com",

        "item_selector": 'a[data-testid="articlefeaturedcard-component"]',
        "title_attr": "aria-label",
        "date_selector": "time",

        "content_selectors": [
            '[data-testid="rich-text"]',
            ".richText",
            ".article-body",
            ".d_flex.flex-d_column",
        ],
    },
}
