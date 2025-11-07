import os
import csv
import time
import pandas as pd
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


def connect_to_spotify():  # handles all the authentication
    # read env file
    load_dotenv()

    # get client id and secret
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise ValueError("Kets not found")

    authentication_manager = SpotifyClientCredentials(
        client_id=client_id, client_secret=client_secret
    )
    sp = spotipy.Spotify(
        auth_manager=authentication_manager, requests_timeout=30, retries=3
    )

    print("Connected Successfully")
    return sp


def get_artist_id(sp, hiphop_artist_name_list):
    artist_ids = []

    for name in hiphop_artist_name_list:
        result = sp.search(q=name, type="artist", limit=1)  # search name of artist once
        if result["artists"]["items"]:  # if list is not empty
            artist_id = result["artists"]["items"][0]["id"]
            artist_ids.append(artist_id)
            print(f"Found ID for {name}: {artist_id}")

    return artist_ids


def get_all_song_ids_from_artist(sp, artist_id_list):
    all_song_ids = set()  # some songs are the same: deluxe albums, greatest hits, single and album version -> non duplicate storage -> set

    for artist_id in artist_id_list:
        print(f"Processing artist {artist_id}")

        album_offset = 0  # create an offset due to spotify api call limit of 50
        while True:
            try:
                albums = sp.artist_albums(
                    artist_id,
                    album_type="album,single",
                    limit=50,
                    offset=album_offset,  # album type is necessary since it will show other categories like: featured on, compliations...
                )
            except Exception as e:
                print(f"Error getting albums for artist {artist_id}: {e}.")
                break

            if not albums["items"]:
                break  # No more albums for this artist

            for album in albums["items"]:
                song_offset = 0  # same creation of offset for songs
                while True:
                    try:
                        songs = sp.album_tracks(
                            album["id"], limit=50, offset=song_offset
                        )
                    except Exception as e:
                        print(f"Error getting songs for album {album['id']}: {e}")
                        break

                    if not songs["items"]:
                        break

                    for song in songs["items"]:
                        all_song_ids.add(song["id"])

                    song_offset += len(songs["items"])

            album_offset += len(albums["items"])

    print(f"Found {len(all_song_ids)} total unique songs.")
    return list(all_song_ids)


def get_details_for_song(sp, song_id_list):
    all_song_data = []

    for i in range(0, len(song_id_list), 50):  # batches of 50
        batch_ids = song_id_list[i : i + 50]
        print(f"Song details batch {i // 50 + 1} / {len(song_id_list) // 50 + 1}.")

        results = None
        for attempt in range(3):
            try:
                results = sp.tracks(batch_ids)
                break
            except Exception as e:
                print(f"Error batch {i} (Attempt {attempt + 1}): {e}")
                if attempt < 3 - 1:
                    time.sleep(5)
        if not results:
            continue  # Skip batch if it fails

        for song in results["tracks"]:
            if song:
                all_song_data.append(
                    {
                        "id": song["id"],
                        "name": song["name"],
                        "popularity": song["popularity"],
                        "artists_full": ", ".join([a["name"] for a in song["artists"]]),
                        "primary_artist_id": song["artists"][0]["id"]
                        if song["artists"]
                        else None,
                        "explicit": song["explicit"],
                        "release_date": song["album"]["release_date"],
                    }
                )

    print(f"Found details for {len(all_song_data)} songs.")
    return all_song_data


def save_as_csv(song_list, filename):
    if not song_list:
        print("No songs to save.")
        return

    print(f"Saving {len(song_list)} songs to {filename}.")

    df = pd.DataFrame(song_list)
    df = df.sort_values(by="popularity", ascending=False)
    df.drop_duplicates(subset=["name", "primary_artist_id"], keep="first", inplace=True)
    df.to_csv(
        filename, index=False, encoding="utf-8"
    )  # utf-8 to maintain all character are saved properly
    print(f"Saved {len(df)} unique songs to {filename}.")
