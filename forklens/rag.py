"""
forklens/rag.py
===============
Core RAG pipeline:
  - Embed user query
  - Retrieve passages from Qdrant
  - Filter by emotion overlap
  - Build narrative context
  - Generate LLM response

Also contains the fallback path used when Qdrant is unavailable.
"""

from sentence_transformers import SentenceTransformer

from .config import EMBED_MODEL_NAME, COLLECTION_NAME, TOP_K_RESULTS, CONTEXT_WINDOW, log
from .db import qdrant_client, QDRANT_AVAILABLE
from .emotion import predict_emotion
from .llm_client import client, get_model_name
from .prompts import (
    COUNSELOR_SYSTEM_PROMPT,
    get_rag_emotion_prompt,
    get_additional_examples_prompt,
)

# ── Embedding model ───────────────────────────────────────────────────────────
_embed_model = SentenceTransformer(EMBED_MODEL_NAME)


# ── Public API ────────────────────────────────────────────────────────────────

def get_cumulative_emotion_score(conversation_history: list) -> float:
    scores = [
        msg.get("emotion_score", 0.0)
        for msg in conversation_history[-3:]
        if msg["role"] == "user"
    ]
    return sum(scores) / len(scores) if scores else 0.0

def rag_emotion_reasoning(
    user_input: str,
    full_context: str = None,
    conversation_history: list = None,
    top_k: int = TOP_K_RESULTS,
    context_window: int = CONTEXT_WINDOW,
    conversation_stage: str = "READY"
) -> dict:
    """
    Full RAG pipeline and conversational response handler.
    - FEELING / EMERGING: skips Qdrant, responds with warm listening only.
    - READY: full embedding, Qdrant search, and literary character response.
    """
    history = conversation_history or []
    log(f"🚀 RAG START: stage={conversation_stage} | '{user_input[:50]}...'")


    if not QDRANT_AVAILABLE:
        log("⚠️  Qdrant unavailable – fallback mode", "WARN")
        emo = predict_emotion(user_input)
        tags = [e for e, _ in emo["fine_grained_emotions"]]
        return _fallback_response(user_input, tags)

    try:
        # Always detect emotion on the raw user input
        search_query = user_input
        log("Step 1: Emotion detection")
        emo = predict_emotion(search_query)
        primary = emo["fine_grained_emotions"][0]
        emotion_label = primary[0]
        emotion_score = primary[1]
        tags = [e for e, _ in emo["fine_grained_emotions"]]
        log(f"Detected primary: {emotion_label} ({emotion_score:.2f})")

        # STAGE GATE: Only search Qdrant when the situation is clear
        if conversation_stage != "READY":
            log(f"⏭️  Stage '{conversation_stage}' — skipping Qdrant, using listening response")
            context = ""
            should_give_insight = False
        else:
            # 2 – Embed query
            log("Step 2: Embedding query")
            vector = _embed_model.encode([search_query])[0].tolist()

            # 3 – Qdrant search
            log(f"Step 3: Qdrant search (top {top_k * 3})")
            try:
                results = qdrant_client.query_points(
                    collection_name=COLLECTION_NAME,
                    query=vector,
                    limit=top_k * 3,
                )
            except Exception as exc:
                log(f"❌ Qdrant query failed: {exc}", "ERROR")
                return _fallback_response(user_input, tags)

            # 4 – Emotion filter
            log("Step 4: Emotion filtering")
            filtered = _filter_by_emotion(results.points, tags)
            if not filtered:
                return _fallback_response(user_input, tags)

            # 5 – Build context
            log("Step 5: Building literary context")
            context = _build_context(filtered, top_k, context_window)
            if not context.strip():
                return _fallback_response(user_input, tags)

        # 6 – Generate response
        log("Step 6: Generating unified LLM response")

        prompt = get_rag_emotion_prompt(
            user_message=user_input,
            emotion_label=emotion_label,
            emotion_score=emotion_score,
            retrieved_passages=context,
            conversation_history=history,
            conversation_stage=conversation_stage
        )
        
        # Build the proper message list for the LLM call
        messages = [{"role": "system", "content": COUNSELOR_SYSTEM_PROMPT}]
        # Visible chat history — clean turns
        if history:
            messages.extend({"role": m["role"], "content": m["content"]} for m in history)
        
        # Final instruction turn (hidden context from UI)
        messages.append({"role": "user", "content": prompt})
        
        resp = client.chat.completions.create(
            model=get_model_name(),
            messages=messages,
        )
        return {
            "text": resp.choices[0].message.content,
            "prompt_payload": prompt,
            "emotion_label": emotion_label,
            "emotion_score": emotion_score,
            "retrieved_passages": context
        }

    except Exception as exc:
        log(f"❌ RAG Error: {exc}", "ERROR")
        return {
            "text": f"⚠️ Error in reasoning: {exc}", 
            "prompt_payload": "", 
            "emotion_label": "unknown", 
            "emotion_score": 0.0,
            "retrieved_passages": ""
        }


def rag_additional_examples(
    original_situation: str,
    top_k: int = TOP_K_RESULTS,
    context_window: int = CONTEXT_WINDOW,
    offset: int = 5,
) -> str:
    """Return additional literary examples with an offset to avoid repetition."""
    try:
        emo = predict_emotion(original_situation)
        tags = [e for e, _ in emo["fine_grained_emotions"]]
        if not tags:
            return "Let me share some different perspectives from literature on your situation."

        vector = _embed_model.encode([original_situation])[0].tolist()

        results = qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            query=vector,
            limit=top_k * 3,
            offset=offset,
        )

        filtered = _filter_by_emotion(results.points, tags)
        if not filtered:
            return "Here are some different literary perspectives that might resonate with your situation..."

        context = _build_context(filtered, top_k, context_window)

        # Build prompt using the context block
        prompt = get_additional_examples_prompt(original_situation, tags, context, [])
        
        # Build the message list (for more examples, we just start fresh with the context as the user's turn)
        messages = [
            {"role": "system", "content": COUNSELOR_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        resp = client.chat.completions.create(
            model=get_model_name(),
            messages=messages,
        )
        return {
            "text": resp.choices[0].message.content,
            "prompt_payload": prompt
        }

    except Exception as exc:
        log(f"❌ Additional examples error: {exc}", "ERROR")
        return {
            "text": "Let me share another perspective from literature that might help illuminate your path forward.",
            "prompt_payload": ""
        }


# ── Internal helpers ──────────────────────────────────────────────────────────

def _filter_by_emotion(points, emotion_tags: list) -> list:
    filtered = []
    for hit in points:
        payload = hit.payload or {}
        top_emotions = payload.get("top_emotions", {})
        if not isinstance(top_emotions, dict):
            continue
        overlap = [e for e in top_emotions.keys() if e in emotion_tags]
        if overlap:
            filtered.append((hit, overlap))
    return filtered


def _build_context(filtered_points: list, top_k: int, context_window: int) -> str:
    context = ""
    for hit, _ in filtered_points[:top_k]:
        hit_id = hit.id
        neighbor_ids = [i for i in range(hit_id - context_window, hit_id + context_window + 1) if i >= 0]

        try:
            neighbors = qdrant_client.retrieve(collection_name=COLLECTION_NAME, ids=neighbor_ids)
        except Exception:
            continue

        choice_dict: dict = {}
        for point in neighbors:
            if not point.payload:
                continue
            text = point.payload.get("text", "")
            choice = point.payload.get("choice_made", "Not specified")
            outcome = point.payload.get("outcome", "Unknown outcome")
            if choice not in choice_dict:
                choice_dict[choice] = f"{text} (Choice: {choice}, Outcome: {outcome})"

        choices = list(choice_dict.items())
        if choices:
            context += choices[0][1]
            if len(choices) > 1:
                context += f"\n\n{choices[1][1]}"
            context += "\n---\n"

    return context


def _fallback_response(user_input: str, emotion_tags: list) -> dict:
    """LLM-only response when Qdrant is unavailable."""
    try:
        prompt = get_rag_emotion_prompt(
            user_message=user_input,
            emotion_label=emotion_tags[0] if emotion_tags else "neutral",
            emotion_score=1.0,  # We just pass 1 for fallback to trigger advice rules
            retrieved_passages="(Database offline: Use your internal LLM knowledge to provide a character or wisdom that matches this situation.)",
            conversation_history=None
        )
        resp = client.chat.completions.create(
            model=get_model_name(),
            messages=[
                {"role": "system", "content": COUNSELOR_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        return {
            "text": resp.choices[0].message.content + "\n\n*Note: I'm currently having trouble accessing my full literary database, but I hope this perspective helps.*",
            "prompt_payload": prompt,
            "emotion_label": emotion_tags[0] if emotion_tags else "neutral",
            "emotion_score": 1.0,
            "retrieved_passages": "(Database offline)"
        }
    except Exception as exc:
        return {
            "text": f"I understand you're feeling {', '.join(emotion_tags[:3])} about your situation. While I'm having technical difficulties right now, remember that many great literary characters have faced similar crossroads. Your feelings are valid, and this challenging time will pass.",
            "prompt_payload": "",
            "emotion_label": emotion_tags[0] if emotion_tags else "neutral",
            "emotion_score": 0.0,
            "retrieved_passages": ""
        }
