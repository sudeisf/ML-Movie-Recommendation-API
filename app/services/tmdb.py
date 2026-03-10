from typing import Any

import requests


class TMDbClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def fetch_metadata(self, tmdb_id: int) -> dict[str, Any] | None:
        if not self.api_key:
            return None

        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
        try:
            response = requests.get(url, params={"api_key": self.api_key}, timeout=8)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            return None

        return None
