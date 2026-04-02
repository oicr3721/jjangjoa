import requests
from bs4 import BeautifulSoup


def crawl_list(site_name, config):

    print(f"[CRAWL] {site_name}")

    res = requests.get(config["list_url"])
    soup = BeautifulSoup(res.text, "html.parser")

    items = soup.select(config["item_selector"])

    results = []

    for item in items:

        try:

            # 제목
            if "title_attr" in config:
                title = item.get(config["title_attr"])
            else:
                title_tag = item.select_one(config["title_selector"])
                title = title_tag.get_text(strip=True)

            # 날짜
            date_tag = item.select_one(config["date_selector"])
            date = date_tag.get_text(strip=True) if date_tag else ""

            # 링크
            if config.get("link_selector"):
                link_tag = item.select_one(config["link_selector"])
                href = link_tag.get("href")
            else:
                href = item.get("href")

            if not href:
                continue

            if href.startswith("http"):
                url = href
            else:
                url = config["base_url"] + href

            results.append({
                "game": site_name,
                "title": title,
                "date": date,
                "url": url
            })

        except Exception as e:
            print("parse error:", e)

    print("found:", len(results))

    return results