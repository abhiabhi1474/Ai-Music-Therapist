import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_TRACK_LIMIT

_spotify_client = None


def get_spotify_client():
    global _spotify_client
    if _spotify_client is None:
        if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
            raise ValueError(
                "Spotify credentials missing. Set SPOTIFY_CLIENT_ID and "
                "SPOTIFY_CLIENT_SECRET in your environment / HuggingFace secrets."
            )
        auth = SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
        )
        _spotify_client = spotipy.Spotify(auth_manager=auth)
    return _spotify_client


def search_tracks(query: str, limit: int = SPOTIFY_TRACK_LIMIT) -> list[dict]:
    """
    Search Spotify for tracks matching `query`.
    Returns a list of track dicts with normalised fields.
    """
    try:
        sp = get_spotify_client()
        results = sp.search(q=query, type="track", limit=limit)
        tracks = []
        for item in results["tracks"]["items"]:
            album_images = item["album"]["images"]
            image_url = album_images[0]["url"] if album_images else None
            tracks.append({
                "id":         item["id"],
                "name":       item["name"],
                "artist":     ", ".join(a["name"] for a in item["artists"]),
                "album":      item["album"]["name"],
                "popularity": item["popularity"],
                "preview_url":item["preview_url"],
                "image_url":  image_url,
                "spotify_url":item["external_urls"]["spotify"],
                "uri":        item["uri"],
                "duration_ms":item["duration_ms"],
            })
        return tracks
    except Exception as e:
        print(f"Spotify search error: {e}")
        return []


def get_embed_url(track_id: str) -> str:
    return f"https://open.spotify.com/embed/track/{track_id}?utm_source=generator&theme=0"


def format_duration(ms: int) -> str:
    seconds = ms // 1000
    m, s = divmod(seconds, 60)
    return f"{m}:{s:02d}"
