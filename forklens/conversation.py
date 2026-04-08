"""
forklens/conversation.py
========================
Handles all multi-turn conversation logic:
  - Greeting responses
  - Conversational follow-up (listening phase)
  - Literary advice intent detection
  - More-examples intent detection
  - Closure / goodbye detection and responses
  - Providing additional literary examples
"""

from .llm_client import client, get_model_name
from .rag import rag_additional_examples
from .config import log
from .prompts import (
    GREETING_SYSTEM_PROMPT,
    CONVERSATION_SYSTEM_PROMPT,
    ENDING_SYSTEM_PROMPT,
    END_CHECK_PROMPT,
    ADVICE_CHECK_PROMPT,
    TEXT_CORRECTION_PROMPT,
    STAGE_DETECTION_PROMPT,
    FEELING_ONLY_PROMPT,
)


# ── Greeting ──────────────────────────────────────────────────────────────────

def generate_greeting_response(user_input: str) -> str:
    """Generate a warm, dynamic greeting response."""
    log(f"👋 GREETING: '{user_input}'")
    try:
        resp = client.chat.completions.create(
            model=get_model_name(),
            messages=[
                {"role": "system", "content": GREETING_SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ],
        )
        return resp.choices[0].message.content
    except Exception as exc:
        log(f"❌ Greeting error: {exc}", "ERROR")
        return (
            "Hello! 😊 I'm here to help. Share a situation or emotion you're going through, "
            "and I'll find literary characters who faced similar crossroads."
        )


# ── Conversation Stage Detection ──────────────────────────────────────────────

def detect_conversation_stage(
    conversation_history: list,
    user_message: str,
    emotion_score: float = 0.0
) -> str:
    """
    Returns "FEELING", "EMERGING", or "READY".
    Uses keyword counting + turn count (deterministic, no LLM call needed).
    READY  → Qdrant fetches + literary character surfaces.
    """
    user_turns = [m for m in conversation_history if m["role"] == "user"]
    turn_count = len(user_turns) + 1  # +1 for the current message

    all_user_text = " ".join([
        (m.get("display_content") or m.get("content", ""))
        for m in conversation_history
        if m.get("role") == "user"
    ]) + " " + user_message
    all_user_text_lower = all_user_text.lower()

    # Situation-signal keywords — each one means context has been shared
    situation_keywords = [
        "job", "work", "career", "years", "family",
        "friend", "relationship", "money", "health",
        "decision", "choice", "leaving", "staying",
        "lost", "failed", "ended", "died", "left",
        "because", "since", "when", "after", "before",
        "studies", "college", "university", "degree",
        "boss", "manager", "partner", "parent", "child",
        "fired", "quit", "promoted", "rejected", "alone",
        "married", "divorced", "moved", "stuck", "trapped",
        "higher", "pick", "choose", "confused about",
    ]

    situation_count = sum(
        1 for kw in situation_keywords if kw in all_user_text_lower
    )

    # ── READY: trigger Qdrant + character ──
    if (
        turn_count >= 3
        or situation_count >= 2
        or (situation_count >= 1 and emotion_score >= 0.25)
    ):
        stage = "READY"
    elif situation_count >= 1:
        stage = "EMERGING"
    else:
        stage = "FEELING"

    log(f"🎯 STAGE: {stage} | turns={turn_count} | keywords={situation_count} | emotion_score={emotion_score:.2f}")
    return stage


# ── Feeling-Only Response (Stage == FEELING) ──────────────────────────────────

def feeling_only_response(user_message: str, emotion_label: str) -> str:
    """Generate a short, warm acknowledgment when the user has only shared a feeling."""
    log("💭 FEELING-ONLY response (no Qdrant)")
    try:
        resp = client.chat.completions.create(
            model=get_model_name(),
            messages=[
                {
                    "role": "user",
                    "content": FEELING_ONLY_PROMPT.format(
                        emotion=emotion_label,
                        user_message=user_message,
                    ),
                }
            ],
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()
    except Exception as exc:
        log(f"❌ Feeling-only error: {exc}", "ERROR")
        return "I can feel the weight in those words. I’m right here with you."


# ── Follow-up (listening phase) ───────────────────────────────────────────────

def generate_followup(conversation_history: list) -> str:
    """Encourage the user to share more context."""
    try:
        messages = [{"role": "system", "content": CONVERSATION_SYSTEM_PROMPT}]
        messages.extend({"role": m["role"], "content": m["content"]} for m in conversation_history)
        resp = client.chat.completions.create(model=get_model_name(), messages=messages)
        return resp.choices[0].message.content
    except Exception as exc:
        print(f"❌ Follow-up error: {exc}")
        return "Tell me more about what you're going through. What's been on your mind?"


# ── Advice-intent detection ───────────────────────────────────────────────────

def check_wants_advice(user_message: str) -> bool:
    """Use the LLM to decide whether the user wants literary advice."""
    log(f"🤔 ADVICE CHECK: '{user_message[:50]}...'")
    try:
        resp = client.chat.completions.create(
            model=get_model_name(),
            messages=[
                {"role": "system", "content": ADVICE_CHECK_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
        answer = resp.choices[0].message.content.strip().upper()
        log(f"LLM decision: '{answer}'")
        return "ADVICE" in answer
    except Exception as exc:
        log(f"❌ Advice-check error: {exc}", "ERROR")
        return False



# ── Conversation-end pre-filter ───────────────────────────────────────────────

EXPLICIT_END_SIGNALS = [
    "bye", "goodbye", "good bye", "see you", "see ya", "farewell",
    "thank you", "thanks", "thx", "thank u", "ty",
    "that's all for now", "that's all i needed",
    "that helped", "this helped", "i feel better now",
    "i'm good now", "you've helped", "i know what to do now",
]

def should_check_end(user_message: str) -> bool:
    """
    Fast keyword pre-filter — returns True ONLY if the message contains
    an explicit goodbye or gratitude signal.
    This MUST pass before check_wants_to_end() or wants_to_end() are called.
    Emotional statements ('I feel empty', 'I'm sad') will ALWAYS return False.
    """
    text = user_message.lower().strip()
    return any(signal in text for signal in EXPLICIT_END_SIGNALS)


# ── Conversation-end detection (LLM) ─────────────────────────────────────────

def check_wants_to_end(user_message: str) -> bool:
    """Use the LLM to decide whether the user wants to end the conversation."""
    log(f"🔚 END CHECK: '{user_message[:50]}...'")
    try:
        resp = client.chat.completions.create(
            model=get_model_name(),
            messages=[
                {"role": "system", "content": END_CHECK_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
        answer = resp.choices[0].message.content.strip().upper()
        log(f"LLM decision: '{answer}'")
        return "END" in answer
    except Exception as exc:
        log(f"❌ End-check error: {exc}", "ERROR")
        return False


# ── Closure ───────────────────────────────────────────────────────────────────

def generate_closure_response(user_input: str) -> str:
    """Generate a warm goodbye when the user expresses satisfaction."""
    try:
        resp = client.chat.completions.create(
            model=get_model_name(),
            messages=[
                {"role": "system", "content": ENDING_SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ],
        )
        return resp.choices[0].message.content
    except Exception as exc:
        print(f"❌ Closure error: {exc}")
        return (
            "You're so welcome! 😊 Remember, every story has its chapters, and yours is still being written. "
            "Take care, and feel free to return anytime you need literary wisdom! 📚✨"
        )


# ── More examples ─────────────────────────────────────────────────────────────

def provide_more_examples(original_situation: str, offset: int = 5) -> dict:
    """Provide additional literary examples when the user asks for more."""
    try:
        # returns {"text": ..., "prompt_payload": ...}
        return rag_additional_examples(original_situation, offset=offset)
    except Exception as exc:
        log(f"❌ More-examples error: {exc}", "ERROR")
        return {
            "text": "I'm having a little trouble recalling more stories right now, but let's keep reflecting on what we've found.",
            "prompt_payload": ""
        }
# ── Text Auto-Correction ──────────────────────────────────────────────────────

def correct_user_input(text: str) -> str:
    """Fix obvious spelling/grammar typos using the LLM editor."""
    if not text.strip() or len(text.split()) < 2:
        return text
        
    log(f"📝 AUTOCORRECT: '{text[:50]}...'")
    try:
        resp = client.chat.completions.create(
            model=get_model_name(),
            messages=[
                {"role": "user", "content": TEXT_CORRECTION_PROMPT.format(text=text)},
            ],
            temperature=0.1,  # Low temp for accuracy
        )
        corrected = resp.choices[0].message.content.strip()
        # Clean potential quotes from LLM output
        corrected = corrected.strip('"`\'')
        
        if corrected.lower() != text.lower():
             log(f"✅ Fixed: '{corrected}'")
        return corrected
    except Exception as exc:
        log(f"❌ Autocorrect error: {exc}", "ERROR")
        return text
