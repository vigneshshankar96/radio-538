from bs4 import BeautifulSoup
import datetime
import pytz
import requests
import time

from spotify_client import SpotifyClient


if __name__ == "__main__":

    spotify_client = SpotifyClient()

    pst_timezone = pytz.timezone('US/Pacific')
    ist_timezone = pytz.timezone('Asia/Kolkata')

    playlist_id = spotify_client.search_playlist('Radio 538 Non Stop')

    while True:
        query = "http://api.dar.fm/playlist.php"
        radio_538_non_stop_id = "144282"
        r = requests.get(
            query,
            params={
                "station_id": radio_538_non_stop_id,
                "partner_token": "1836719856"
            },
            headers={
                'User-Agent': 'Chrome/72.0.3626.109',
            }
        )

        current_time = time.time()
        radio_station = BeautifulSoup(r.text, 'html.parser').playlist.station
        local_time = datetime.datetime.strptime(
            radio_station.songstamp.text.strip(),
            "%Y-%m-%d %H:%M:%S"
        )
        utc_time = pst_timezone.localize(local_time, is_dst=None)
        song_stamp = utc_time.astimezone(ist_timezone)

        title = radio_station.title.text.strip()
        artist = radio_station.artist.text.strip()
        seconds_remaining = int(radio_station.seconds_remaining.text)
        song_length = 0
        if seconds_remaining == 0:
            time.sleep(15)
            continue
        print(f'{song_stamp} | "{title}" by {artist}')
        try:
            song_id = spotify_client.search_song(artist, title)
            print(f'Found song on Spotify by ID: {song_id}')
        except:
            song_id = None
            print(f'Song not found on Spotify')
        if song_id:
            if spotify_client.add_song_to_playlist(song_id, playlist_id):
                print(f'Added song to playlist')
            else:
                print(f'Song not added to playlist')
        time.sleep(seconds_remaining)
