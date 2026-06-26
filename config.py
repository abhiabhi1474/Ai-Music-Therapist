import os
from dotenv import load_dotenv

load_dotenv()

# Spotify API credentials
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")

# HuggingFace model names
EMOTION_MODEL = "j-hartmann/emotion-english-distilroberta-base"
THERAPIST_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"

# Emotion → Spotify search query mapping
EMOTION_TO_QUERY = {
    "anger":    "relaxing instrumental calming music",
    "disgust":  "feel good positive vibes music",
    "fear":     "anxiety relief calm music",
    "joy":      "party hits happy upbeat songs",
    "neutral":  "ambient background music focus",
    "sadness":  "uplifting songs hope motivation",
    "surprise": "feel good songs energetic",
    "stress":   "stress relief meditation music",
}

# Emotion display names & emojis
EMOTION_META = {
    "anger":    {"emoji": "😠", "label": "Anger"},
    "disgust":  {"emoji": "🤢", "label": "Disgust"},
    "fear":     {"emoji": "😨", "label": "Fear / Anxiety"},
    "joy":      {"emoji": "😊", "label": "Joy"},
    "neutral":  {"emoji": "😐", "label": "Neutral"},
    "sadness":  {"emoji": "😢", "label": "Sadness"},
    "surprise": {"emoji": "😲", "label": "Surprise"},
    "stress":   {"emoji": "😰", "label": "Stress"},
}

# Number of Spotify tracks to fetch
SPOTIFY_TRACK_LIMIT = 10

# Playlist duration target (minutes)
PLAYLIST_MINUTES = 30
