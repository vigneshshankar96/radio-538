import datetime
import logging
import time

import pytz
import requests
from bs4 import BeautifulSoup

from spotify_client import SpotifyClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

if __name__ == "__main__":

    spotify_client = SpotifyClient()

    pst_timezone = pytz.timezone("US/Pacific")
    ist_timezone = pytz.timezone("Asia/Kolkata")

    # Radio Station ID
    radio_538_non_stop_id = "144282"
    # Spotify Playlist ID
    playlist_id = spotify_client.search_playlist("Radio 538 Non Stop")
    # Shelf life of Spotify Authentication Token (in seconds)
    spotify_token_shelf_life = 3600

    token_expiry_timestamp = (
        time.time() + spotify_token_shelf_life - 10
    )

    while True:
        current_time = time.time()

        # If current token is about to expire, refresh token
        if current_time >= token_expiry_timestamp:
            token_expiry_timestamp = (
                current_time + spotify_token_shelf_life - 10
            )
            logging.info("="*80)
            logging.warning(f"Spotify Auth Token has been refreshed")
            spotify_client.refresh_token()

        # Query playlist info of station
        query = "http://api.dar.fm/playlist.php"
        response = requests.get(
            query,
            params={
                "station_id": radio_538_non_stop_id,
                "partner_token": "1836719856"
            },
            headers={
                "User-Agent": "Chrome/72.0.3626.109",
            }
        )
        radio_station = (
            BeautifulSoup(response.text, "html.parser").playlist.station
        )
        local_time = datetime.datetime.strptime(
            radio_station.songstamp.text.strip(),
            "%Y-%m-%d %H:%M:%S"
        )
        utc_time = pst_timezone.localize(local_time, is_dst=None)

        # Start time, Title, Artist and Seconds remaining of current track
        track_start_timestamp = (
            utc_time.astimezone(ist_timezone).strftime("%d-%b-%y %H:%M:%S")
        )
        title = radio_station.title.text.strip()
        artist = radio_station.artist.text.strip()
        seconds_remaining = int(radio_station.seconds_remaining.text)

        # If ad was foung playing, wait for it to get over
        if seconds_remaining == 0:
            time.sleep(15)
            continue
        logging.info("="*80)
        logging.info(
            f'"{title}" by "{artist}" aired at {track_start_timestamp} IST'
        )

        # Search if the track aired is available in Spotify, get ID if yes
        try:
            track_id = spotify_client.search_track(artist, title)
            logging.info(f"+ Found track on Spotify by ID: {track_id}")
        except:
            track_id = None
            logging.info(f"! Track not found on Spotify")

        # If Track ID was fetched, add it to playlist
        if track_id:
            if track_id in spotify_client.get_tracks_in_playlist(playlist_id):
                logging.info(
                    f"! Track already exists in Playlist ID: {playlist_id}"
                )
            elif spotify_client.add_track_to_playlist(track_id, playlist_id):
                logging.info(
                    f"+ Added to Spotify playlist of ID: {playlist_id}"
                )
            else:
                logging.info(f"- Track not added to Spotify playlist")

        # Wait until current track has finished before retrying
        time.sleep(seconds_remaining)
