from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch
from config import THERAPIST_MODEL
from prompts import THERAPIST_SYSTEM_PROMPT, build_therapist_prompt

_therapist_pipeline = None


def get_therapist_pipeline():
    global _therapist_pipeline
    if _therapist_pipeline is None:
        print(f"Loading therapist model: {THERAPIST_MODEL} ...")
        _therapist_pipeline = pipeline(
            "text-generation",
            model=THERAPIST_MODEL,
            torch_dtype=torch.float32,
            device_map="auto",
            trust_remote_code=True,
        )
        print("Therapist model loaded.")
    return _therapist_pipeline


def get_therapy_response(user_text: str, emotion: str, confidence: float) -> str:
    """Generate empathetic therapist response."""
    try:
        pipe = get_therapist_pipeline()
        user_prompt = build_therapist_prompt(user_text, emotion, confidence)

        messages = [
            {"role": "system", "content": THERAPIST_SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt},
        ]

        output = pipe(
            messages,
            max_new_tokens=200,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            pad_token_id=pipe.tokenizer.eos_token_id,
        )

        # Extract generated text from the assistant turn
        generated = output[0]["generated_text"]
        if isinstance(generated, list):
            # Chat template returns list of messages
            for msg in reversed(generated):
                if msg.get("role") == "assistant":
                    return msg["content"].strip()
        return str(generated).strip()

    except Exception as e:
        print(f"Therapist error: {e}")
        return _fallback_response(emotion)


def _fallback_response(emotion: str) -> str:
    fallbacks = {
        "fear":    "It's completely natural to feel anxious sometimes. Take a slow, deep breath and remind yourself that you've handled challenges before. Gentle, calming music can help quiet the mind — give the recommendations below a listen.",
        "sadness": "It's okay to feel sad; your feelings are valid. Be gentle with yourself today. Uplifting music has a wonderful way of slowly shifting our mood — let the playlist below accompany you.",
        "anger":   "Feeling angry is a natural response to frustration. Give yourself a moment to breathe and step back. Calming instrumental music can ease tension — try the tracks below.",
        "joy":     "It's wonderful that you're feeling joyful! Celebrate this moment. The upbeat playlist below will keep your energy high.",
        "neutral": "Sometimes a neutral state is the perfect canvas for creativity. Ambient music can help you focus or simply relax — enjoy the selection below.",
        "disgust": "Those feelings of discomfort are completely valid. Take a breath and redirect your energy. Some positive, feel-good music might help shift the mood.",
        "surprise":"Life is full of unexpected moments! Channel that energy positively. The energetic playlist below might be just what you need.",
    }
    return fallbacks.get(emotion, "Your feelings matter. Music is a powerful companion — let the playlist below support you right now.")
