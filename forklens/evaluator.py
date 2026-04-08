"""
forklens/evaluator.py
=====================
LLM-as-Judge evaluator for ForkLens end-to-end quality assessment.

Scores each response across five dimensions:
  1. Emotion Accuracy    — did BERT's prediction match the user's true feeling?
  2. Retrieval Relevance — are the Qdrant passages actually relevant?
  3. Literary Fit        — are the characters/stories a good crossroads match?
  4. Empathy & Helpfulness — does the final response feel warm and useful?
  5. Proactive Engagement — did ForkLens surface a character naturally?

Usage (module):
    from forklens.evaluator import evaluate
    result = evaluate(user_query, bert_emotion, bert_score, retrieved_passages, llm_response)
    print(result)
"""

import json
import re
from dataclasses import dataclass, asdict
from typing import Literal

from .llm_client import client
from .config import JUDGE_MODEL, GROQ_API_KEY, log
from .prompts import get_judge_prompt
from openai import OpenAI

# ── Groq Judge Client ─────────────────────────────────────────────────────────
if GROQ_API_KEY:
    groq_client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=GROQ_API_KEY
    )
else:
    groq_client = None


# ── Data model ────────────────────────────────────────────────────────────────

@dataclass
class DimensionScore:
    score: int
    reason: str


@dataclass
class EvaluationResult:
    emotion_accuracy: DimensionScore
    retrieval_relevance: DimensionScore
    literary_fit: DimensionScore
    empathy_helpfulness: DimensionScore
    proactive_engagement: DimensionScore
    overall_verdict: Literal["good", "needs_improvement", "poor"]
    suggested_fix: str

    @property
    def average_score(self) -> float:
        scores = [
            self.emotion_accuracy.score,
            self.retrieval_relevance.score,
            self.literary_fit.score,
            self.empathy_helpfulness.score,
            self.proactive_engagement.score
        ]
        return round(sum(scores) / len(scores), 2)

    def to_dict(self) -> dict:
        return asdict(self)

    def __str__(self) -> str:
        bar = lambda s: "█" * s + "░" * (5 - s)
        lines = [
            "┌─────────────────────────────────────────────────────┐",
            "│              🔍 ForkLens Evaluation Report           │",
            "├─────────────────────────────────────────────────────┤",
            f"│  Emotion Accuracy     [{bar(self.emotion_accuracy.score)}] {self.emotion_accuracy.score}/5",
            f"│  Retrieval Relevance  [{bar(self.retrieval_relevance.score)}] {self.retrieval_relevance.score}/5",
            f"│  Literary Fit         [{bar(self.literary_fit.score)}] {self.literary_fit.score}/5",
            f"│  Empathy & Help       [{bar(self.empathy_helpfulness.score)}] {self.empathy_helpfulness.score}/5",
            f"│  Proactive Engage     [{bar(self.proactive_engagement.score)}] {self.proactive_engagement.score}/5",
            "├─────────────────────────────────────────────────────┤",
            f"│  Average Score: {self.average_score}/5.0",
            f"│  Verdict:       {self.overall_verdict.upper()}",
            "├─────────────────────────────────────────────────────┤",
            f"│  💡 Fix: {self.suggested_fix}",
            "└─────────────────────────────────────────────────────┘",
        ]
        return "\n".join(lines)


# ── Core evaluation function ──────────────────────────────────────────────────

def evaluate(
    user_query: str,
    bert_emotion: str,
    bert_score: float,
    retrieved_passages: str,
    llm_response: str,
) -> EvaluationResult:
    """
    Send all inputs to the LLM judge and return a structured EvaluationResult.

    Args:
        user_query:          The user's raw input / dilemma.
        bert_emotion:        E.g. "confusion"
        bert_score:          E.g. 0.91
        retrieved_passages:  The literary passages string used.
        llm_response:        The final response shown to the user.

    Returns:
        EvaluationResult dataclass with per-dimension scores and verdict.

    Raises:
        ValueError: If the LLM returns invalid or non-parseable JSON.
    """
    log("🔍 Starting evaluation...")

    judge_prompt = get_judge_prompt(
        user_message=user_query,
        bert_emotion=bert_emotion,
        bert_score=bert_score,
        retrieved_passages=retrieved_passages,
        llm_response=llm_response
    )

    try:
        active_client = groq_client if groq_client else client
        model_name = JUDGE_MODEL if groq_client else "meta-llama/Llama-3.3-70B-Instruct"
        provider = "Groq" if groq_client else "HuggingFace"

        log(f"⚖️  Judge model: {model_name} via {provider}")
        
        kwargs = {}
        if groq_client:
            kwargs["response_format"] = {"type": "json_object"}

        resp = active_client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": judge_prompt},
            ],
            temperature=0.1,
            **kwargs
        )
        raw = resp.choices[0].message.content.strip()
    except Exception as exc:
        raise RuntimeError(f"LLM judge call failed: {exc}") from exc

    # Extract JSON even if the model wraps it in markdown fences
    json_match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not json_match:
        raise ValueError(f"No JSON object found in judge response:\n{raw}")

    try:
        data = json.loads(json_match.group())
    except json.JSONDecodeError as exc:
        raise ValueError(f"Failed to parse judge JSON: {exc}\nRaw:\n{raw}") from exc

    try:
        result = EvaluationResult(
            emotion_accuracy=DimensionScore(**data["emotion_accuracy"]),
            retrieval_relevance=DimensionScore(**data["retrieval_relevance"]),
            literary_fit=DimensionScore(**data["literary_fit"]),
            empathy_helpfulness=DimensionScore(**data["empathy_helpfulness"]),
            proactive_engagement=DimensionScore(**data["proactive_engagement"]),
            overall_verdict=data["overall_verdict"],
            suggested_fix=data["suggested_fix"],
        )
    except (KeyError, TypeError) as exc:
        raise ValueError(f"Judge JSON has unexpected structure: {exc}\nData: {data}") from exc

    log(f"✅ Evaluation complete — verdict: {result.overall_verdict}, avg: {result.average_score}")
    return result
