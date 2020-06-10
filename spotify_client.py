import requests
import urllib.parse

from creds.refresher import Refresher


class SpotifyClient(object):

    def __init__(self):
        self.api_token = Refresher().refresh()

    def search_song(self, artist, track):
        query = urllib.parse.quote(f'{artist} {track}')
        url = f"https://api.spotify.com/v1/search?q={query}&type=track"
        response = requests.get(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_token}"
            }
        )
        response_json = response.json()

        results = response_json['tracks']['items']
        if results:
            # let's assume the first track in the list is the song we want
            return results[0]['id']
        else:
            raise Exception(f"No song found for {artist} = {track}")

    def add_song_to_spotify(self, song_id):
        url = "https://api.spotify.com/v1/me/tracks"
        response = requests.put(
            url,
            json={
                "ids": [song_id]
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_token}"
            }
        )

    def search_playlist(self, playlist):
        url = "https://api.spotify.com/v1/me/playlists"
        response = requests.get(
            url,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_token}"
            }
        )
        response_json = response.json()

        all_playlists = response_json['items']
        for _playlist in all_playlists:
            if _playlist['name'] == playlist:
                return _playlist['id']

        raise Exception(f"No playlist found for {playlist}")

    def add_song_to_playlist(self, song_id, playlist_id):
        song_uris = ['spotify:track:' + song_id]
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        response = requests.post(
            url,
            json=song_uris,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_token}"
            }
        )

        return response.ok
