import requests

from app.core.config import KAKAO_REST_API_KEY


class KakaoClient:

    BASE_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"

    def search_places(
        self,
        keyword,
        latitude,
        longitude,
        radius=3000
    ):

        headers = {
            "Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"
        }

        params = {
            "query": keyword,
            "x": longitude,
            "y": latitude,
            "radius": radius,
            "size": 15,
            "sort": "distance"
        }

        response = requests.get(
            self.BASE_URL,
            headers=headers,
            params=params
        )

        #print(response.status_code)
        #print(response.text)

        return response.json().get("documents", [])