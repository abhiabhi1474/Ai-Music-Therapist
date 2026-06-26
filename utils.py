import plotly.graph_objects as go
from config import EMOTION_META, PLAYLIST_MINUTES


def build_emotion_chart(all_scores: list[dict]) -> str:
    """Build a stunning HTML emotion chart instead of Plotly."""
    palette = {
        "joy":      {"bar": "#FFD700", "glow": "rgba(255,215,0,0.3)"},
        "sadness":  {"bar": "#60A5FA", "glow": "rgba(96,165,250,0.3)"},
        "anger":    {"bar": "#F87171", "glow": "rgba(248,113,113,0.3)"},
        "fear":     {"bar": "#A78BFA", "glow": "rgba(167,139,250,0.3)"},
        "disgust":  {"bar": "#34D399", "glow": "rgba(52,211,153,0.3)"},
        "surprise": {"bar": "#FB923C", "glow": "rgba(251,146,60,0.3)"},
        "neutral":  {"bar": "#94A3B8", "glow": "rgba(148,163,184,0.3)"},
        "stress":   {"bar": "#F472B6", "glow": "rgba(244,114,182,0.3)"},
    }

    sorted_scores = sorted(all_scores, key=lambda x: x["score"], reverse=True)
    top_emotion   = sorted_scores[0]["label"].lower() if sorted_scores else "neutral"

    rows = []
    for item in sorted_scores:
        label   = item["label"].lower()
        pct     = round(item["score"] * 100, 1)
        meta    = EMOTION_META.get(label, {"emoji": "🎵", "label": label.capitalize()})
        colors  = palette.get(label, {"bar": "#888", "glow": "rgba(136,136,136,0.2)"})
        is_top  = label == top_emotion
        bold    = "font-weight:700;" if is_top else "font-weight:400;"
        opacity = "1" if is_top else "0.55"
        scale   = "transform:scale(1.01);" if is_top else ""

        rows.append(f"""
<div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;
            opacity:{opacity};transition:opacity .2s;{scale}">
  <div style="width:28px;text-align:center;font-size:1.1rem;">{meta['emoji']}</div>
  <div style="width:110px;font-size:0.82rem;color:#c8c8e0;{bold}
              white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
    {meta['label']}
  </div>
  <div style="flex:1;background:#1e1e35;border-radius:20px;height:10px;overflow:hidden;">
    <div style="width:{pct}%;height:100%;border-radius:20px;
                background:{colors['bar']};
                box-shadow:0 0 8px {colors['glow']};
                transition:width 0.8s cubic-bezier(.4,0,.2,1);"></div>
  </div>
  <div style="width:46px;text-align:right;font-size:0.8rem;color:#9090b0;{bold}">{pct}%</div>
</div>""")

    return f"""
<div style="background:linear-gradient(135deg,#0f0f20,#13132a);
            border:1px solid #2a2a4a;border-radius:16px;padding:20px 24px;">
  <div style="font-size:0.7rem;font-weight:700;letter-spacing:2px;
              color:#1DB954;text-transform:uppercase;margin-bottom:16px;">
    📊 Emotion Breakdown
  </div>
  {"".join(rows)}
</div>"""


def build_playlist_text(tracks: list[dict]) -> str:
    if not tracks:
        return "No tracks found."

    playlist  = []
    total_ms  = 0
    target_ms = PLAYLIST_MINUTES * 60 * 1000

    for i, track in enumerate(tracks, 1):
        dur = track.get("duration_ms", 210_000)
        if total_ms + dur > target_ms and playlist:
            break
        playlist.append((i, track, dur))
        total_ms += dur

    lines = [f"🎵 ~{PLAYLIST_MINUTES}-Minute Playlist\n{'─'*36}"]
    for rank, (i, t, dur) in enumerate(playlist, 1):
        m, s = divmod(dur // 1000, 60)
        lines.append(f"{rank}. {t['name']} — {t['artist']}  ({m}:{s:02d})")

    total_m, total_s = divmod(total_ms // 1000, 60)
    lines.append(f"{'─'*36}\nTotal: {total_m}:{total_s:02d}")
    return "\n".join(lines)


def build_tracks_html(tracks: list[dict]) -> str:
    if not tracks:
        return """
<div style="text-align:center;padding:2rem;color:#555;font-size:0.9rem;">
  🔑 No tracks found — check your Spotify credentials in HF Secrets.
</div>"""

    cards = []
    for t in tracks:
        img = (
            f'<img src="{t["image_url"]}" alt="album art" '
            f'style="width:100%;aspect-ratio:1/1;object-fit:cover;">'
            if t["image_url"] else
            '<div style="background:linear-gradient(135deg,#1a1a2e,#252545);'
            'aspect-ratio:1/1;display:flex;align-items:center;'
            'justify-content:center;font-size:2.5rem;">🎵</div>'
        )
        pop = t.get("popularity", 0)
        pop_dots = "".join([
            f'<span style="width:6px;height:6px;border-radius:50%;background:'
            f'{"#1DB954" if i < round(pop/20) else "#2a2a4a"};display:inline-block;margin:0 1px;"></span>'
            for i in range(5)
        ])
        preview_btn = (
            f'<a href="{t["preview_url"]}" target="_blank" '
            f'style="background:#0d2b10;color:#1DB954;border:1px solid #1DB954;'
            f'padding:3px 9px;border-radius:20px;font-size:0.7rem;'
            f'text-decoration:none;font-weight:600;">▶ Preview</a>'
            if t["preview_url"] else '<span></span>'
        )
        cards.append(f"""
<div style="background:#13132a;border:1px solid #2a2a4a;border-radius:14px;
            overflow:hidden;display:flex;flex-direction:column;
            transition:transform .2s,box-shadow .2s;
            box-shadow:0 4px 20px rgba(0,0,0,0.4);">
  <div style="overflow:hidden;">
    {img}
  </div>
  <div style="padding:12px;flex:1;display:flex;flex-direction:column;gap:5px;">
    <div style="font-weight:700;font-size:0.88rem;color:#f0f0ff;
                white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"
         title="{t['name']}">{t['name']}</div>
    <div style="font-size:0.76rem;color:#8888bb;">{t['artist']}</div>
    <div style="font-size:0.7rem;color:#555566;white-space:nowrap;
                overflow:hidden;text-overflow:ellipsis;">{t['album']}</div>
    <div style="display:flex;align-items:center;gap:4px;margin-top:2px;">
      {pop_dots}
      <span style="font-size:0.65rem;color:#555;">{pop}/100</span>
    </div>
    <div style="margin-top:8px;display:flex;justify-content:space-between;align-items:center;">
      {preview_btn}
      <a href="{t['spotify_url']}" target="_blank"
         style="background:linear-gradient(135deg,#1DB954,#15a34a);color:#000;
                padding:4px 11px;border-radius:20px;font-size:0.72rem;
                font-weight:700;text-decoration:none;letter-spacing:.3px;">
        Open ↗
      </a>
    </div>
  </div>
</div>""")

    grid = "\n".join(cards)
    return f"""
<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(155px,1fr));
            gap:14px;padding:4px 2px;">
  {grid}
</div>"""


def build_embed_html(tracks: list[dict]) -> str:
    if not tracks:
        return "<p style='color:#444;font-size:0.85rem;'>No tracks to embed.</p>"

    embeds = []
    for t in tracks[:3]:
        embed_url = (
            f"https://open.spotify.com/embed/track/{t['id']}"
            f"?utm_source=generator&theme=0"
        )
        embeds.append(f"""
<div style="margin-bottom:10px;">
  <iframe style="border-radius:14px;" src="{embed_url}"
    width="100%" height="80" frameborder="0"
    allowfullscreen
    allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
    loading="lazy">
  </iframe>
</div>""")

    return "\n".join(embeds)
