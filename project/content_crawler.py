import requests
from bs4 import BeautifulSoup


def crawl_content(url):

    try:

        res = requests.get(url)

        soup = BeautifulSoup(res.text, "html.parser")

        content = soup.get_text()

        return content

    except:

        return ""