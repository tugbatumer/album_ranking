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

def generate_album_json(album_id, album_slug, yagiz_ranks, tugba_ranks):
    album = sp.album(album_id)
    tracks = {t['track_number']: {
        'name': t['name'],
        'spotify_url': t['external_urls']['spotify']
    } for t in album['tracks']['items']}

    def track_list(rank_list):
        return [tracks[num] for num in rank_list if num in tracks]

    output = {
        'album': album['name'],
        'artist': album['artists'][0]['name'],
        'spotify_id': album_id,
        'album_art_url': album['images'][0]['url'],
        'yagiz_songs': track_list(yagiz_ranks),
        'tugba_songs': track_list(tugba_ranks)
    }

    os.makedirs('albums', exist_ok=True)
    with open(f'albums/{album_slug}.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f'Saved albums/{album_slug}.json')


