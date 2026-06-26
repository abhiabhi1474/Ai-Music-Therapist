import plotly.graph_objects as go
from config import EMOTION_META, PLAYLIST_MINUTES


def build_emotion_chart(all_scores: list[dict]) -> go.Figure:
    """Build a horizontal bar chart of emotion confidence scores."""
    labels = []
    values = []
    colors = []

    palette = {
        "joy":      "#FFD700",
        "sadness":  "#6495ED",
        "anger":    "#FF4500",
        "fear":     "#9370DB",
        "disgust":  "#32CD32",
        "surprise": "#FF69B4",
        "neutral":  "#A9A9A9",
        "stress":   "#FF8C00",
    }

    for item in sorted(all_scores, key=lambda x: x["score"]):
        label = item["label"].lower()
        meta  = EMOTION_META.get(label, {"emoji": "🎵", "label": label.capitalize()})
        labels.append(f'{meta["emoji"]} {meta["label"]}')
        values.append(round(item["score"] * 100, 1))
        colors.append(palette.get(label, "#888888"))

    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker_color=colors,
        text=[f"{v}%" for v in values],
        textposition="outside",
    ))

    fig.update_layout(
        title="Emotion Confidence Scores",
        xaxis=dict(title="Confidence (%)", range=[0, 110]),
        yaxis=dict(title=""),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=13),
        height=320,
        margin=dict(l=20, r=40, t=50, b=20),
    )
    return fig


def build_playlist_text(tracks: list[dict]) -> str:
    """
    Build a ~30-minute playlist from the track list.
    Returns a formatted string.
    """
    if not tracks:
        return "No tracks found."

    playlist = []
    total_ms  = 0
    target_ms = PLAYLIST_MINUTES * 60 * 1000

    for i, track in enumerate(tracks, 1):
        dur = track.get("duration_ms", 210_000)   # default ~3.5 min
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
    """Build an HTML card grid for the recommended tracks."""
    if not tracks:
        return "<p style='color:#888'>No tracks found for this emotion. Please check your Spotify credentials.</p>"

    cards = []
    for t in tracks:
        img = (
            f'<img src="{t["image_url"]}" alt="album art" '
            f'style="width:100%;border-radius:8px 8px 0 0;object-fit:cover;height:160px;">'
            if t["image_url"] else
            '<div style="background:#333;height:160px;border-radius:8px 8px 0 0;display:flex;'
            'align-items:center;justify-content:center;font-size:2rem;">🎵</div>'
        )
        preview_btn = (
            f'<a href="{t["preview_url"]}" target="_blank" '
            f'style="font-size:0.75rem;color:#1DB954;text-decoration:none;">▶ Preview</a>'
            if t["preview_url"] else ""
        )
        cards.append(f"""
<div style="background:#1a1a2e;border-radius:10px;overflow:hidden;
            box-shadow:0 4px 15px rgba(0,0,0,0.3);display:flex;flex-direction:column;">
  {img}
  <div style="padding:12px;flex:1;display:flex;flex-direction:column;gap:4px;">
    <div style="font-weight:700;font-size:0.9rem;color:#fff;
                white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"
         title="{t['name']}">{t['name']}</div>
    <div style="font-size:0.78rem;color:#aaa;">{t['artist']}</div>
    <div style="font-size:0.72rem;color:#666;">{t['album']}</div>
    <div style="font-size:0.72rem;color:#888;">⭐ {t['popularity']}/100</div>
    <div style="margin-top:auto;display:flex;justify-content:space-between;align-items:center;">
      {preview_btn}
      <a href="{t['spotify_url']}" target="_blank"
         style="background:#1DB954;color:#000;padding:4px 10px;border-radius:20px;
                font-size:0.75rem;font-weight:700;text-decoration:none;">Open ↗</a>
    </div>
  </div>
</div>""")

    grid = "\n".join(cards)
    return f"""
<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));
            gap:12px;padding:4px;">
  {grid}
</div>"""


def build_embed_html(tracks: list[dict]) -> str:
    """Build Spotify embed iframes for the first 3 tracks."""
    if not tracks:
        return "<p style='color:#888;'>No tracks to embed.</p>"

    embeds = []
    for t in tracks[:3]:
        embed_url = f"https://open.spotify.com/embed/track/{t['id']}?utm_source=generator&theme=0"
        embeds.append(
            f'<iframe style="border-radius:12px;margin-bottom:8px;" '
            f'src="{embed_url}" width="100%" height="80" frameborder="0" '
            f'allowfullscreen allow="autoplay; clipboard-write; encrypted-media; '
            f'fullscreen; picture-in-picture" loading="lazy"></iframe>'
        )

    return "\n".join(embeds)
