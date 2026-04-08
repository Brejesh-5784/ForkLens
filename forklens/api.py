import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# Import current ForkLens logic
from .conversation import (
    generate_greeting_response,
    provide_more_examples,
    correct_user_input,
    detect_conversation_stage,
    feeling_only_response
)
from .rag import rag_emotion_reasoning
from .evaluator import evaluate
from .emotion import predict_emotion
from .prompts import is_greeting, get_display_message

app = FastAPI(title="ForkLens API")

# Enable CORS for the React frontend (usually port 5173 for Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local dev; tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Models ────────────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str
    content: str
    display_content: Optional[str] = None
    emotion_label: Optional[str] = None
    emotion_score: Optional[float] = None
    retrieved_passages: Optional[str] = ""

class ChatRequest(BaseModel):
    user_input: str
    history: List[ChatMessage]

class ChatResponse(BaseModel):
    text: str
    stage: str
    emotion: str
    score: float
    passages: str
    evaluation: Optional[dict] = None

# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
def health_check():
    return {"status": "ok", "message": "ForkLens Backend Active"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    try:
        raw_input = req.user_input
        history = [m.dict() for m in req.history]

        # 1. Autocorrect
        clean_input = correct_user_input(raw_input)
        display_content = get_display_message(clean_input)

        # 2. Check for Greeting
        if is_greeting(clean_input):
            return ChatResponse(
                text=generate_greeting_response(clean_input),
                stage="GREETING",
                emotion="neutral",
                score=0.0,
                passages=""
            )

        # 3. Predict Emotion (Step 1)
        emo = predict_emotion(clean_input)
        emo_label = emo["fine_grained_emotions"][0][0]
        emo_score = emo["fine_grained_emotions"][0][1]

        # 4. Detect Stage (Step 2)
        stage = detect_conversation_stage(
            conversation_history=history,
            user_message=clean_input,
            emotion_score=emo_score
        )

        # 5. Route by Stage (Step 3)
        if stage == "FEELING":
            text = feeling_only_response(clean_input, emo_label)
            result = {
                "text": text,
                "emotion_label": emo_label,
                "emotion_score": emo_score,
                "retrieved_passages": ""
            }
        else:
            # Build full context for Qdrant/RAG
            full_context = " ".join(
                (m.get("display_content") or m.get("content", ""))
                for m in history if m.get("role") == "user"
            ) + " " + (display_content or "")
            
            result = rag_emotion_reasoning(
                user_input=clean_input,
                full_context=full_context,
                conversation_history=history,
                top_k=5,
                conversation_stage=stage
            )
            text = result.get("text")

        # 6. Evaluate (LLM-as-a-Judge)
        eval_result = evaluate(
            user_query=display_content,
            bert_emotion=result.get("emotion_label"),
            bert_score=result.get("emotion_score"),
            retrieved_passages=result.get("retrieved_passages"),
            llm_response=text
        )

        return ChatResponse(
            text=text,
            stage=stage,
            emotion=result.get("emotion_label"),
            score=result.get("emotion_score"),
            passages=result.get("retrieved_passages"),
            evaluation=eval_result.to_dict() if eval_result else None
        )

    except Exception as e:
        print(f"❌ API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
