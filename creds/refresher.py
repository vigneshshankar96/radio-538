import requests
from .spotify_secrets import REFRESH_TOKEN, BASE_64


class Refresher:

    def refresh(self):
        query = "https://accounts.spotify.com/api/token"
        response = requests.post(
            query,
            data={
                "grant_type": "refresh_token",
                "refresh_token": REFRESH_TOKEN
            },
            headers={
                "Authorization": f"Basic {BASE_64}"
            }
        )
        response_json = response.json()

        results = response_json["access_token"]
        if results:
            return results
        else:
            raise Exception(f"Could not refresh access token")
