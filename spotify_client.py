import requests
import urllib.parse

from creds.refresher import Refresher


class SpotifyClient(object):

    def __init__(self):
        self.token_refresher = Refresher()
        self.refresh_token()

    def refresh_token(self):
        self.api_token = self.token_refresher.refresh()

    def search_track(self, artist, track):
        _artist  = " ".join([
            word for word in artist.split()
            if word.lower() not in ["ft."]
        ])
        query = urllib.parse.quote(f"{_artist} {track}")
        url = f"https://api.spotify.com/v1/search?q={query}&type=track"
        response = requests.get(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_token}"
            }
        )
        response_json = response.json()

        results = response_json["tracks"]["items"]
        if results:
            # let's assume the first track in the list is the track we want
            return results[0]["id"]
        else:
            raise Exception(f"No track found for {artist} = {track}")

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

    def add_track_to_playlist(self, track_id, playlist_id):
        track_uris = ['spotify:track:' + track_id]
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        response = requests.post(
            url,
            json=track_uris,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_token}"
            }
        )

        return response.ok

    def get_tracks_in_playlist(self, playlist_id):
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        response = requests.get(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_token}"
            }
        )
        response_json = response.json()

        tracks = []

        results = response_json["items"]
        if results:
            for _item in results:
                item_is_track = _item.get("track", False)
                if item_is_track:
                    tracks.append(_item["track"]["id"])

        return tracks
