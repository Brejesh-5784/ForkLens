"""
forklens/emotion.py
===================
Emotion detection using the locally fine-tuned BERT model.
Falls back to a neutral placeholder if the model is not found.
"""

import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from .config import EMOTION_MODEL_PATH, log

# ── Load model at import time ─────────────────────────────────────────────────

def _load_model():
    if not os.path.exists(EMOTION_MODEL_PATH):
        print(f"⚠️  Emotion model not found at '{EMOTION_MODEL_PATH}'")
        return None, None, None
    try:
        tokenizer = AutoTokenizer.from_pretrained(EMOTION_MODEL_PATH)
        model = AutoModelForSequenceClassification.from_pretrained(EMOTION_MODEL_PATH)
        model.eval()
        label_map = model.config.id2label
        print("✅ Emotion model loaded successfully")
        return tokenizer, model, label_map
    except Exception as exc:
        print(f"❌ Error loading emotion model: {exc}")
        return None, None, None


_tokenizer, _model, _label_map = _load_model()


# ── Public API ────────────────────────────────────────────────────────────────

def predict_emotion(text: str, k: int = 15) -> dict:
    """
    Return the top-k emotions for *text* using the local fine-tuned model.

    Returns:
        {"fine_grained_emotions": [(emotion_label, score), ...]}
    """
    log(f"🎭 EMOTION: Analysing '{text[:50]}...'")

    if not all([_tokenizer, _model, _label_map]):
        log("⚠️  Emotion model unavailable – returning neutral placeholder", "WARN")
        return {"fine_grained_emotions": [("neutral", 0.8), ("contemplative", 0.2)]}

    try:
        inputs = _tokenizer(text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            logits = _model(**inputs).logits
            probs = torch.nn.functional.softmax(logits, dim=-1)[0]

        topk = torch.topk(probs, min(k, probs.size(0)))
        emotions = [(_label_map[int(i)], float(probs[i])) for i in topk.indices]

        log(f"🎯 Emotion distribution ({len(emotions)} labels):")
        for idx, (label, score) in enumerate(emotions):
            log(f"   {idx+1}. {label}: {score:.3f}")
            
        return {"fine_grained_emotions": emotions}

    except Exception as exc:
        log(f"❌ Emotion prediction error: {exc}", "ERROR")
        return {"fine_grained_emotions": [("neutral", 0.8), ("contemplative", 0.2)]}
