"""
scripts/evaluate.py
===================
CLI runner for the ForkLens LLM-as-Judge evaluator.

Usage:
    python scripts/evaluate.py                    # run built-in sample cases
    python scripts/evaluate.py --json             # also dump full JSON output
    python scripts/evaluate.py --case 2           # run only sample case #2

Sample cases cover a range of scenarios to stress-test all 5 dimensions.
"""

import argparse
import json
import sys
import os

# Allow running from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from forklens.evaluator import evaluate, EvaluationResult


# ── Sample test cases ─────────────────────────────────────────────────────────

SAMPLE_CASES = [
    {
        "id": 1,
        "label": "Career crossroads — fear of leaving stability",
        "user_query": (
            "I've been offered my dream job but it means leaving the stable career "
            "I've built over 10 years. I'm terrified of making the wrong choice and "
            "losing everything I worked so hard for."
        ),
        "bert_emotion": "fear",
        "bert_score": 0.88,
        "retrieved_passages": [
            (
                "Raskolnikov stood at the crossroads of his life, knowing that one step forward "
                "would destroy the carefully constructed image of himself he had maintained. "
                "He closed his eyes and stepped — not from courage, but from the realisation "
                "that standing still was its own kind of ruin. (Crime and Punishment)"
            ),
            (
                "Dorothea Brooke had mapped out her life according to a vision of greatness; "
                "yet the true choice before her was not between ambition and comfort, "
                "but between the life she had planned and the life that was actually calling her. "
                "(Middlemarch)"
            ),
        ],
        "llm_response": (
            "It sounds like you're standing before a vast, open sea, terrified that stepping off "
            "the shore means losing the ground you've fought so hard to claim. 🌊\n\n"
            "What you're describing reminds me of Dorothea Brooke in *Middlemarch* — standing "
            "at the edge of a life that felt too safe for her real purpose. She spent years "
            "convinced that duty and stability were her only path, but George Eliot shows us "
            "that the most frightening choices are often the only ones that let us truly live.\n\n"
            "What feels most frightening about saying yes to this new horizon?"
        ),
    },
    {
        "id": 2,
        "label": "Grief and loss — struggling after bereavement",
        "user_query": (
            "My mother passed away three months ago. Everyone expects me to be 'over it' "
            "by now but I still can't get out of bed some mornings. I feel completely alone."
        ),
        "bert_emotion": "sadness",
        "bert_score": 0.93,
        "retrieved_passages": [
            (
                "Captain Ahab's obsession with the whale consumed every tender thing in him; "
                "grief transformed to rage, loss weaponised into destruction. "
                "(Moby-Dick — thematic mismatch)"
            ),
        ],
        "llm_response": (
            "I'm so sorry you're carrying such a heavy weight right now. Three months is "
            "barely a heartbeat in the long landscape of grief.\n\n"
            "Tell me more about what those quiet mornings feel like when you're alone with your thoughts?"
        ),
    },
    {
        "id": 3,
        "label": "Betrayal by a close friend",
        "user_query": (
            "My best friend of 15 years betrayed my trust by sharing something deeply personal. "
            "I feel humiliated and I don't know whether to forgive or walk away forever."
        ),
        "bert_emotion": "betrayal",
        "bert_score": 0.91,
        "retrieved_passages": [
            (
                "Prospero in The Tempest was betrayed by his own brother and cast out. "
                "For years his power was devoted to the possibility of revenge. But he "
                "finally chose virtue over vengeance, finding that mercy freed him "
                "far more than revenge ever could. (The Tempest)"
            ),
        ],
        "llm_response": (
            "That sense of betrayal is a unique kind of razor-sharp pain, especially from "
            "someone who has walked beside you for over a decade. ⚔️\n\n"
            "Prospero in *The Tempest* felt that same sting from those he called family, "
            "spending years hollowing himself out with thoughts of what he was owed. "
            "But Shakespeare shows us that he only found peace when he realized that "
            "carrying the fire of revenge was burning him far more than the original act.\n\n"
            "As you think about your friend, do you feel that same fire burning within you, "
            "or is there a part of you that's already looking for the exit?"
        ),
    },
]


# ── CLI helpers ───────────────────────────────────────────────────────────────

def run_case(case: dict, dump_json: bool = False) -> EvaluationResult:
    print(f"\n{'═' * 60}")
    print(f"  Case #{case['id']}: {case['label']}")
    print(f"{'═' * 60}")
    print(f"\n📝 User query: {case['user_query'][:120]}...")
    print(f"🎭 BERT emotion: {case['bert_emotion']} (confidence: {case['bert_score']})")
    
    # Format passages as a string block for the judge
    passages_block = "\n\n".join(
        f"[{i + 1}] {p.strip()}" for i, p in enumerate(case['retrieved_passages'])
    )

    print("\n⏳ Sending to judge...\n")

    result = evaluate(
        user_query=case["user_query"],
        bert_emotion=case["bert_emotion"],
        bert_score=case["bert_score"],
        retrieved_passages=passages_block,
        llm_response=case["llm_response"],
    )

    print(result)

    if dump_json:
        print("\n📄 Raw JSON output:")
        print(json.dumps(result.to_dict(), indent=2))

    return result


def main():
    parser = argparse.ArgumentParser(
        description="ForkLens LLM-as-Judge evaluation runner"
    )
    parser.add_argument(
        "--case", type=int, default=None,
        help="Run only a specific case by ID (1, 2, or 3). Omit to run all."
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Also print the full JSON evaluation output."
    )
    args = parser.parse_args()

    cases_to_run = (
        [c for c in SAMPLE_CASES if c["id"] == args.case]
        if args.case
        else SAMPLE_CASES
    )

    if not cases_to_run:
        print(f"❌ No case found with ID {args.case}. Valid IDs: 1, 2, 3")
        sys.exit(1)

    results = []
    for case in cases_to_run:
        try:
            result = run_case(case, dump_json=args.json)
            results.append((case["label"], result))
        except Exception as e:
            print(f"❌ Error running case #{case['id']}: {e}")

    if len(results) > 1:
        print(f"\n{'═' * 60}")
        print("  📊 Summary")
        print(f"{'═' * 60}")
        for label, r in results:
            verdict_icon = {"good": "✅", "needs_improvement": "⚠️", "poor": "❌"}.get(
                r.overall_verdict, "❓"
            )
            print(f"  {verdict_icon} [{r.average_score}/5.0] {label}")
        print()


if __name__ == "__main__":
    main()
