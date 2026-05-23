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

        # x = 경도(longitude), y = 위도(latitude)
        params = {
            "query": keyword,
            "x": str(longitude),
            "y": str(latitude),
            "radius": radius,
            "size": 15,
            "sort": "distance",
            "category_group_code": "FD6"  # 음식점만 필터
        }

        try:
            response = requests.get(
                self.BASE_URL,
                headers=headers,
                params=params,
                timeout=5
            )
            data = response.json()
            return data.get("documents", [])
        except Exception as e:
            print(f"Kakao API error: {e}")
            return []
