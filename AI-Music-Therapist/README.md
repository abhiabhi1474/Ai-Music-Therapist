# 🎵 AI Music Therapist

> An AI-powered emotional wellness assistant that understands your emotions and instantly recommends playable Spotify music.

[![Hugging Face Spaces](https://img.shields.io/badge/🤗%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces)

---

## ✨ Features

| Feature | Details |
|---|---|
| 🧠 Emotion Detection | `j-hartmann/emotion-english-distilroberta-base` — 7 emotion labels with confidence scores |
| 💬 AI Therapist | `Qwen/Qwen2.5-0.5B-Instruct` — empathetic, context-aware responses |
| 🎵 Live Music Search | Spotify Web API — real tracks based on your detected emotion |
| ▶ Embedded Player | Play Spotify tracks directly inside the app |
| 📊 Emotion Chart | Interactive Plotly bar chart of all emotion scores |
| 🎶 Playlist Generator | Auto-generates a ~30-minute playlist from results |

---

## 🚀 Deploy on Hugging Face Spaces

### 1. Create a new Space

- Go to [huggingface.co/new-space](https://huggingface.co/new-space)
- SDK: **Gradio**
- Visibility: Public or Private

### 2. Upload all project files

Upload every file in this folder to your Space repository.

### 3. Add Spotify secrets

In your Space → **Settings → Repository secrets**, add:

| Secret name | Value |
|---|---|
| `SPOTIFY_CLIENT_ID` | Your Spotify app Client ID |
| `SPOTIFY_CLIENT_SECRET` | Your Spotify app Client Secret |

> **Get Spotify credentials free:**
> 1. Go to [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
> 2. Create an app (Redirect URI: `http://localhost`)
> 3. Copy the Client ID and Client Secret

### 4. That's it!

Hugging Face will install `requirements.txt` and launch the app automatically.

---

## 🗂 Project Structure

```
AI-Music-Therapist/
├── app.py          # Main Gradio app & UI
├── config.py       # Settings, model names, emotion→query map
├── emotion.py      # HuggingFace emotion detection pipeline
├── therapist.py    # HuggingFace therapist LLM pipeline
├── spotify.py      # Spotify search & embed helpers
├── prompts.py      # System prompt & prompt builder
├── utils.py        # Chart, playlist, HTML builders
├── requirements.txt
└── README.md
```

---

## 🔄 Application Flow

```
User input
    │
    ▼
Emotion Detection (distilroberta)
    │
    ├──────────────────┐
    ▼                  ▼
AI Therapist        Spotify Search
(Qwen2.5-0.5B)     (emotion query)
    │                  │
    ▼                  ▼
Empathetic text    Track cards + Embeds + Playlist
```

---

## 🎭 Emotion → Music Mapping

| Emotion | Search Query |
|---|---|
| Fear / Anxiety | `anxiety relief calm music` |
| Sadness | `uplifting songs hope motivation` |
| Anger | `relaxing instrumental calming music` |
| Joy | `party hits happy upbeat songs` |
| Neutral | `ambient background music focus` |
| Disgust | `feel good positive vibes music` |
| Surprise | `feel good songs energetic` |

---

## 🛠 Tech Stack (100% Free)

| Component | Technology |
|---|---|
| Frontend | Gradio |
| Emotion Model | `j-hartmann/emotion-english-distilroberta-base` |
| Therapist Model | `Qwen/Qwen2.5-0.5B-Instruct` |
| Music | Spotify Web API via `spotipy` |
| Charts | Plotly |
| Env vars | python-dotenv |
| Hosting | Hugging Face Spaces |

---

## 📝 License

MIT
