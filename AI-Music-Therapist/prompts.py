THERAPIST_SYSTEM_PROMPT = """You are a warm, empathetic AI music therapist. 
Your role is to provide brief, supportive emotional guidance (3-4 sentences) 
and gently suggest how music can help the user feel better.
Be compassionate, non-judgmental, and practical.
Always end with a suggestion to listen to the recommended music."""

def build_therapist_prompt(user_text: str, emotion: str, confidence: float) -> str:
    emotion_label = emotion.capitalize()
    conf_pct = int(confidence * 100)
    return (
        f"The user says: \"{user_text}\"\n\n"
        f"Detected emotion: {emotion_label} (confidence: {conf_pct}%)\n\n"
        f"Please provide empathetic support and a music recommendation suggestion "
        f"for someone feeling {emotion_label}. Keep it to 3-4 sentences."
    )
