"""
AI Music Therapist — main Gradio application
Deploy on Hugging Face Spaces (SDK: Gradio)
Secrets required: SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
"""

import gradio as gr
from emotion import detect_emotion
from therapist import get_therapy_response
from spotify import search_tracks
from config import EMOTION_TO_QUERY, EMOTION_META
from utils import (
    build_emotion_chart,
    build_playlist_text,
    build_tracks_html,
    build_embed_html,
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
CSS = """
/* ── Root & globals ─────────────────────────────────────── */
:root {
  --brand:   #1DB954;
  --brand2:  #1565C0;
  --bg:      #0d0d1a;
  --surface: #141427;
  --card:    #1a1a2e;
  --border:  #2a2a4a;
  --text:    #e8e8f0;
  --muted:   #8888aa;
  --radius:  14px;
}

body, .gradio-container {
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'Inter', 'Segoe UI', sans-serif !important;
}

/* ── Header ─────────────────────────────────────────────── */
.app-header {
  text-align: center;
  padding: 2.5rem 1rem 1.5rem;
  background: linear-gradient(135deg, #0d0d1a 0%, #141430 60%, #0d0d1a 100%);
  border-bottom: 1px solid var(--border);
  margin-bottom: 1.5rem;
}

.app-title {
  font-size: 2.6rem;
  font-weight: 800;
  background: linear-gradient(90deg, var(--brand), #6ee7b7, var(--brand2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 0.4rem;
  letter-spacing: -0.5px;
}

.app-tagline {
  color: var(--muted);
  font-size: 1rem;
  margin: 0;
}

/* ── Panels ─────────────────────────────────────────────── */
.panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.4rem;
  margin-bottom: 1rem;
}

.panel-title {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  color: var(--brand);
  margin: 0 0 0.8rem;
}

/* ── Emotion badge ───────────────────────────────────────── */
.emotion-badge {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: linear-gradient(135deg, #1a1a2e, #1e1e3a);
  border: 1px solid var(--border);
  border-radius: 50px;
  padding: 0.6rem 1.2rem;
  font-size: 1.1rem;
  font-weight: 700;
}

.emotion-emoji { font-size: 1.5rem; }
.emotion-score { color: var(--brand); font-size: 0.85rem; margin-left: 6px; }

/* ── Therapist box ───────────────────────────────────────── */
.therapist-box {
  background: linear-gradient(135deg, #0f1f10, #0d1a2a);
  border: 1px solid #1a3a1a;
  border-left: 4px solid var(--brand);
  border-radius: var(--radius);
  padding: 1.2rem 1.4rem;
  color: #d0f0d0;
  font-size: 0.95rem;
  line-height: 1.7;
  white-space: pre-wrap;
}

/* ── Gradio overrides ────────────────────────────────────── */
.gr-button-primary {
  background: linear-gradient(135deg, var(--brand), #15a34a) !important;
  border: none !important;
  color: #000 !important;
  font-weight: 700 !important;
  border-radius: 50px !important;
  padding: 0.7rem 2.5rem !important;
  font-size: 1rem !important;
  transition: transform .15s, box-shadow .15s !important;
}
.gr-button-primary:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 20px rgba(29,185,84,0.4) !important;
}

textarea, input[type=text] {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
  border-radius: 10px !important;
}

.gr-box, .gr-panel { background: var(--surface) !important; border-color: var(--border) !important; }
label, .label-wrap { color: var(--muted) !important; font-size: 0.8rem !important; text-transform: uppercase; letter-spacing: 1px; }

/* ── Footer ─────────────────────────────────────────────── */
.app-footer {
  text-align: center;
  color: var(--muted);
  font-size: 0.8rem;
  padding: 2rem 0 1rem;
  border-top: 1px solid var(--border);
  margin-top: 2rem;
}
"""

# ─── Core analysis function ───────────────────────────────────────────────────

def analyze(user_text: str):
    """Full pipeline: text → emotion → therapist + spotify."""

    if not user_text or not user_text.strip():
        empty = "<p style='color:#666;'>Please enter how you're feeling.</p>"
        return (
            empty,          # emotion_html
            None,           # chart
            empty,          # therapist_html
            empty,          # tracks_html
            empty,          # embed_html
            empty,          # playlist_text
        )

    # 1. Emotion detection
    result     = detect_emotion(user_text)
    top_emotion = result["top_emotion"]
    top_score  = result["top_score"]
    all_scores = result["all_scores"]

    meta = EMOTION_META.get(top_emotion, {"emoji": "🎵", "label": top_emotion.capitalize()})
    emotion_html = f"""
<div class="panel">
  <div class="panel-title">Detected Emotion</div>
  <div class="emotion-badge">
    <span class="emotion-emoji">{meta['emoji']}</span>
    <span>{meta['label']}</span>
    <span class="emotion-score">{int(top_score*100)}% confidence</span>
  </div>
</div>"""

    # 2. Emotion chart
    chart = build_emotion_chart(all_scores)

    # 3. AI therapist
    therapy_text = get_therapy_response(user_text, top_emotion, top_score)
    therapist_html = f"""
<div class="panel">
  <div class="panel-title">💬 AI Therapist</div>
  <div class="therapist-box">{therapy_text}</div>
</div>"""

    # 4. Spotify search
    query  = EMOTION_TO_QUERY.get(top_emotion, "relaxing music")
    tracks = search_tracks(query)

    # 5. Track cards
    tracks_html = f"""
<div class="panel">
  <div class="panel-title">🎵 Recommended Songs · "{query}"</div>
  {build_tracks_html(tracks)}
</div>"""

    # 6. Embedded player
    embed_html = f"""
<div class="panel">
  <div class="panel-title">▶ Spotify Player</div>
  {build_embed_html(tracks)}
</div>"""

    # 7. Playlist
    playlist = build_playlist_text(tracks)

    return emotion_html, chart, therapist_html, tracks_html, embed_html, playlist


# ─── Gradio UI ────────────────────────────────────────────────────────────────

def build_ui():
    with gr.Blocks(css=CSS, title="🎵 AI Music Therapist") as demo:

        # Header
        gr.HTML("""
<div class="app-header">
  <h1 class="app-title">🎵 AI Music Therapist</h1>
  <p class="app-tagline">
    Share how you feel — get empathetic support &amp; music curated for your mood.
  </p>
</div>""")

        # Input
        with gr.Row():
            with gr.Column(scale=4):
                user_input = gr.Textbox(
                    placeholder="e.g. I'm feeling anxious about tomorrow's interview…",
                    label="How are you feeling today?",
                    lines=3,
                )
            with gr.Column(scale=1, min_width=140):
                analyze_btn = gr.Button("✨ Analyse", variant="primary")

        # Outputs — row 1: emotion + chart
        with gr.Row():
            emotion_out = gr.HTML(label="")
            chart_out   = gr.Plot(label="Emotion Confidence", show_label=False)

        # Row 2: therapist
        therapist_out = gr.HTML(label="")

        # Row 3: tracks
        tracks_out = gr.HTML(label="")

        # Row 4: embedded player
        embed_out = gr.HTML(label="")

        # Row 5: playlist
        playlist_out = gr.Textbox(
            label="🎵 Generated Playlist",
            lines=10,
            interactive=False,
        )

        # Footer
        gr.HTML("""
<div class="app-footer">
  Built with ❤️ using HuggingFace Transformers, Spotify Web API &amp; Gradio
</div>""")

        # Wire up
        analyze_btn.click(
            fn=analyze,
            inputs=[user_input],
            outputs=[emotion_out, chart_out, therapist_out, tracks_out, embed_out, playlist_out],
        )
        user_input.submit(
            fn=analyze,
            inputs=[user_input],
            outputs=[emotion_out, chart_out, therapist_out, tracks_out, embed_out, playlist_out],
        )

    return demo


if __name__ == "__main__":
    demo = build_ui()
    demo.launch()
