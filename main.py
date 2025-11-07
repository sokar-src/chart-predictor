import get_data
import artist_list
import sys


def main():
    sp = get_data.connect_to_spotify()

    hiphop_artists_slice = artist_list.hiphop_artists[0:30]

    artist_ids = get_data.get_artist_id(sp, hiphop_artists_slice)
    print(f"Found {len(artist_ids)} artist IDs.")

    song_ids = get_data.get_all_song_ids_from_artist(sp, artist_ids)
    print(f"Found {len(song_ids)} unique songs.")

    full_data = get_data.get_details_for_song(sp, song_ids)

    get_data.save_as_csv(full_data, "raw_data.csv")
    print("Data Pipeline Complete")


if __name__ == "__main__":
    main()
