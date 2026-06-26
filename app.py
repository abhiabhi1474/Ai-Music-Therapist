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

# ─── CSS ──────────────────────────────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
  --green:   #1DB954;
  --green2:  #15a34a;
  --blue:    #3B82F6;
  --purple:  #8B5CF6;
  --bg:      #080814;
  --surface: #0f0f20;
  --card:    #13132a;
  --border:  #1e1e38;
  --border2: #2a2a48;
  --text:    #e8e8f5;
  --muted:   #6666aa;
  --radius:  16px;
}

*, *::before, *::after { box-sizing: border-box; }

body, .gradio-container, #root {
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'Inter', 'Segoe UI', system-ui, sans-serif !important;
  min-height: 100vh;
}

/* ── Kill default gradio chrome ─── */
.gradio-container { max-width: 1100px !important; margin: 0 auto !important; padding: 0 16px 40px !important; }
footer { display: none !important; }
.svelte-1ed2p3z { display: none !important; }

/* ── Header ─── */
.app-header {
  text-align: center;
  padding: 3rem 1rem 2rem;
  position: relative;
}
.header-glow {
  position: absolute;
  top: 0; left: 50%; transform: translateX(-50%);
  width: 600px; height: 200px;
  background: radial-gradient(ellipse, rgba(29,185,84,0.12) 0%, transparent 70%);
  pointer-events: none;
}
.app-title {
  font-size: clamp(2rem, 5vw, 3rem);
  font-weight: 800;
  background: linear-gradient(135deg, #1DB954 0%, #6EE7B7 40%, #60A5FA 80%, #A78BFA 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 0.5rem;
  letter-spacing: -1px;
  line-height: 1.1;
}
.app-tagline {
  color: var(--muted);
  font-size: 1rem;
  font-weight: 400;
  margin: 0;
  letter-spacing: 0.2px;
}

/* ── Input area ─── */
.input-wrap {
  background: var(--surface);
  border: 1px solid var(--border2);
  border-radius: var(--radius);
  padding: 1.5rem;
  margin-bottom: 1.2rem;
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}

textarea {
  background: var(--card) !important;
  border: 1px solid var(--border2) !important;
  color: var(--text) !important;
  border-radius: 12px !important;
  font-family: inherit !important;
  font-size: 0.95rem !important;
  line-height: 1.6 !important;
  resize: none !important;
  transition: border-color .2s !important;
}
textarea:focus {
  border-color: var(--green) !important;
  box-shadow: 0 0 0 3px rgba(29,185,84,0.12) !important;
  outline: none !important;
}
textarea::placeholder { color: var(--muted) !important; }

/* ── Button ─── */
button.primary, button[variant="primary"], .gr-button-primary {
  background: linear-gradient(135deg, var(--green), var(--green2)) !important;
  border: none !important;
  color: #000 !important;
  font-weight: 700 !important;
  font-size: 0.95rem !important;
  letter-spacing: 0.3px !important;
  border-radius: 12px !important;
  padding: 0.75rem 1.5rem !important;
  width: 100% !important;
  height: 100% !important;
  min-height: 50px !important;
  cursor: pointer !important;
  transition: all .2s !important;
  box-shadow: 0 4px 16px rgba(29,185,84,0.3) !important;
}
button.primary:hover, .gr-button-primary:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 24px rgba(29,185,84,0.45) !important;
}

/* ── Labels ─── */
label span, .label-wrap span {
  color: var(--muted) !important;
  font-size: 0.72rem !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  letter-spacing: 1.5px !important;
}

/* ── Playlist textbox ─── */
.gr-textbox textarea {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  color: #9090c0 !important;
  font-family: 'Fira Code', 'Courier New', monospace !important;
  font-size: 0.82rem !important;
  line-height: 1.8 !important;
}

/* ── Divider ─── */
.section-divider {
  border: none;
  border-top: 1px solid var(--border);
  margin: 0.5rem 0 1.2rem;
}

/* ── Scrollbar ─── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }
"""

# ─── HTML builders for sections ────────────────────────────────────────────────

def _section(title: str, content: str, accent: str = "#1DB954") -> str:
    return f"""
<div style="background:linear-gradient(160deg,#0f0f20,#11112a);
            border:1px solid #1e1e38;border-radius:16px;
            padding:20px 22px;margin-bottom:14px;
            box-shadow:0 6px 28px rgba(0,0,0,0.35);">
  <div style="font-size:0.68rem;font-weight:700;letter-spacing:2px;
              color:{accent};text-transform:uppercase;margin-bottom:14px;">
    {title}
  </div>
  {content}
</div>"""


# ─── Core pipeline ─────────────────────────────────────────────────────────────

def analyze(user_text: str):
    blank = "<div style='color:#333;padding:8px;'>—</div>"

    if not user_text or not user_text.strip():
        return blank, blank, blank, blank, blank, ""

    # 1 — Emotion
    result      = detect_emotion(user_text)
    top_emotion = result["top_emotion"]
    top_score   = result["top_score"]
    all_scores  = result["all_scores"]

    meta = EMOTION_META.get(top_emotion, {"emoji": "🎵", "label": top_emotion.capitalize()})
    pct  = int(top_score * 100)

    # Confidence ring colour
    ring_color = "#1DB954" if pct > 70 else "#F59E0B" if pct > 40 else "#EF4444"

    emotion_badge = f"""
<div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap;">
  <!-- Ring -->
  <div style="position:relative;width:80px;height:80px;flex-shrink:0;">
    <svg width="80" height="80" viewBox="0 0 80 80" style="transform:rotate(-90deg);">
      <circle cx="40" cy="40" r="34" fill="none" stroke="#1e1e38" stroke-width="7"/>
      <circle cx="40" cy="40" r="34" fill="none" stroke="{ring_color}" stroke-width="7"
        stroke-dasharray="{round(2*3.14159*34*pct/100,1)} {round(2*3.14159*34*(100-pct)/100,1)}"
        stroke-linecap="round"/>
    </svg>
    <div style="position:absolute;inset:0;display:flex;flex-direction:column;
                align-items:center;justify-content:center;font-size:1.5rem;line-height:1;">
      {meta['emoji']}
    </div>
  </div>
  <!-- Info -->
  <div>
    <div style="font-size:1.5rem;font-weight:800;color:#f0f0ff;letter-spacing:-0.5px;">
      {meta['label']}
    </div>
    <div style="font-size:0.82rem;color:{ring_color};font-weight:600;margin-top:3px;">
      {pct}% confidence
    </div>
    <div style="font-size:0.75rem;color:#444466;margin-top:4px;">
      Detected via distilroberta
    </div>
  </div>
</div>"""

    emotion_html = _section("🧠 Detected Emotion", emotion_badge, ring_color)

    # 2 — Chart (HTML)
    chart_html = _section("📊 Emotion Breakdown", build_emotion_chart(all_scores))

    # 3 — Therapist
    therapy_text = get_therapy_response(user_text, top_emotion, top_score)
    therapy_content = f"""
<div style="background:linear-gradient(135deg,#0a1f0c,#0c1626);
            border-left:3px solid #1DB954;border-radius:10px;
            padding:16px 18px;color:#c8ecd0;font-size:0.93rem;
            line-height:1.75;white-space:pre-wrap;">
  {therapy_text}
</div>"""
    therapist_html = _section("💬 AI Therapist · Qwen2.5", therapy_content)

    # 4 — Spotify
    query  = EMOTION_TO_QUERY.get(top_emotion, "relaxing music")
    tracks = search_tracks(query)

    tracks_html = _section(
        f'🎵 Recommended Songs &nbsp;·&nbsp; <span style="color:#555;font-weight:400;text-transform:none;letter-spacing:0;">"{query}"</span>',
        build_tracks_html(tracks)
    )

    embed_html = _section("▶ Spotify Player", build_embed_html(tracks))

    playlist = build_playlist_text(tracks)

    return emotion_html, chart_html, therapist_html, tracks_html, embed_html, playlist


# ─── Gradio UI ─────────────────────────────────────────────────────────────────

def build_ui():
    with gr.Blocks(title="🎵 AI Music Therapist") as demo:

        gr.HTML("""
<div class="app-header">
  <div class="header-glow"></div>
  <h1 class="app-title">🎵 AI Music Therapist</h1>
  <p class="app-tagline">Share how you feel &mdash; get empathetic support &amp; music curated for your mood.</p>
</div>""")

        # ── Input ──
        with gr.Group(elem_classes="input-wrap"):
            with gr.Row(equal_height=True):
                with gr.Column(scale=5):
                    user_input = gr.Textbox(
                        placeholder="e.g. I'm really anxious about tomorrow's interview and can't stop overthinking…",
                        label="How are you feeling today?",
                        lines=3,
                        max_lines=6,
                    )
                with gr.Column(scale=1, min_width=130):
                    analyze_btn = gr.Button("✨ Analyse", variant="primary")

        # ── Row 1: Emotion badge + Chart side by side ──
        with gr.Row():
            with gr.Column(scale=1):
                emotion_out = gr.HTML()
            with gr.Column(scale=1):
                chart_out = gr.HTML()

        # ── Therapist ──
        therapist_out = gr.HTML()

        # ── Tracks ──
        tracks_out = gr.HTML()

        # ── Embeds ──
        embed_out = gr.HTML()

        # ── Playlist ──
        playlist_out = gr.Textbox(
            label="🎶 Generated Playlist (~30 min)",
            lines=8,
            interactive=False,
        )

        gr.HTML("""
<div style="text-align:center;color:#333355;font-size:0.75rem;
            padding:1.5rem 0 0.5rem;border-top:1px solid #1a1a30;margin-top:0.5rem;">
  Built with HuggingFace Transformers · Spotify Web API · Gradio &nbsp;|&nbsp; 100% Free
</div>""")

        # Wire up
        outs = [emotion_out, chart_out, therapist_out, tracks_out, embed_out, playlist_out]
        analyze_btn.click(fn=analyze, inputs=[user_input], outputs=outs)
        user_input.submit(fn=analyze, inputs=[user_input], outputs=outs)

    return demo


if __name__ == "__main__":
    demo = build_ui()
    demo.launch(css=CSS)
