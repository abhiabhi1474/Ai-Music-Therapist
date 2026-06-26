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
            try:
                album       = item.get("album", {})
                images      = album.get("images", [])
                image_url   = images[0]["url"] if images else None
                artists     = item.get("artists", [])
                ext_urls    = item.get("external_urls", {})
                tracks.append({
                    "id":          item.get("id", ""),
                    "name":        item.get("name", "Unknown"),
                    "artist":      ", ".join(a.get("name", "") for a in artists),
                    "album":       album.get("name", "Unknown Album"),
                    "popularity":  item.get("popularity", 0),
                    "preview_url": item.get("preview_url"),
                    "image_url":   image_url,
                    "spotify_url": ext_urls.get("spotify", ""),
                    "uri":         item.get("uri", ""),
                    "duration_ms": item.get("duration_ms", 210_000),
                })
            except Exception as inner_e:
                print(f"Skipping track due to error: {inner_e}")
                continue
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
