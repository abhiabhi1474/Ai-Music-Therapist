from transformers import pipeline
from config import EMOTION_MODEL

_emotion_pipeline = None

def get_emotion_pipeline():
    global _emotion_pipeline
    if _emotion_pipeline is None:
        print(f"Loading emotion model: {EMOTION_MODEL} ...")
        _emotion_pipeline = pipeline(
            "text-classification",
            model=EMOTION_MODEL,
            top_k=None,          # return all labels
            truncation=True,
            max_length=512,
        )
        print("Emotion model loaded.")
    return _emotion_pipeline


def detect_emotion(text: str) -> dict:
    """
    Returns a dict with:
      - top_emotion: str
      - top_score: float
      - all_scores: list of {label, score} sorted desc
    """
    pipe = get_emotion_pipeline()
    results = pipe(text)[0]           # list of {label, score}
    results_sorted = sorted(results, key=lambda x: x["score"], reverse=True)

    return {
        "top_emotion": results_sorted[0]["label"].lower(),
        "top_score":   results_sorted[0]["score"],
        "all_scores":  results_sorted,
    }
