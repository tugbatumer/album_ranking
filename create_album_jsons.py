import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import os
from dotenv import load_dotenv

load_dotenv()

SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')

if not SPOTIPY_CLIENT_ID or not SPOTIPY_CLIENT_SECRET:
    raise ValueError("Spotify credentials not found in .env")

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET
))

def get_top_5_popular_tracks(album_id, sp):
    album_tracks = sp.album_tracks(album_id)['items']
    track_info = []
    for track in album_tracks:
        popularity = sp.track(track['id'])['popularity']
        track_info.append((track['track_number'] - 1, popularity))  # use 0-based indexing like Yagiz/Tugba

    # Sort by popularity descending, take top 5 track numbers
    top_5 = [track_num for track_num, _ in sorted(track_info, key=lambda x: -x[1])[:5]]
    return top_5


def generate_album_json(album_id, album_slug, yagiz_ranks, tugba_ranks):
    album = sp.album(album_id)
    tracks = {t['track_number']: {
        'name': t['name'],
        'spotify_url': t['external_urls']['spotify']
    } for t in album['tracks']['items']}

    def track_list(rank_list):
        return [tracks[num + 1] for num in rank_list if (num+1) in tracks]

    spotify_ranks = get_top_5_popular_tracks(album_id, sp)

    output = {
        'album': album['name'],
        'artist': album['artists'][0]['name'],
        'spotify_id': album_id,
        'album_art_url': album['images'][0]['url'],
        'yagiz_songs': track_list(yagiz_ranks),
        'tugba_songs': track_list(tugba_ranks),
        'spotify_songs': track_list(spotify_ranks)
    }

    os.makedirs('albums', exist_ok=True)
    with open(f'albums/{album_slug}.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f'Saved albums/{album_slug}.json')


