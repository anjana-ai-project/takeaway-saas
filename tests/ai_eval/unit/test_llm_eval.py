# deepeval==4.0.0  |  openai==2.36.0  |  anthropic==0.100.0
# pip show deepeval -> Version: 4.0.0
#
# DeepEval v4 API facts verified before writing:
#   - LLMTestCase accepts keyword args: input, actual_output, context (list),
#     retrieval_context (list)
#   - Metrics: HallucinationMetric(threshold, model), FaithfulnessMetric(threshold, model),
#     AnswerRelevancyMetric(threshold, model), ToxicityMetric(threshold, model)
#   - metric.measure(test_case) -> float; score on metric.score
#   - GPTModel(model="gpt-4o-mini")

import os
import re
import sys
import time
import functools

import pytest
from dotenv import load_dotenv

# Ensure stdout handles UTF-8 on Windows (cp1252 chokes on ₹)
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

import openai
from openai import RateLimitError as OpenAIRateLimitError
from deepeval.models import GPTModel
from deepeval.metrics import (
    HallucinationMetric,
    FaithfulnessMetric,
    AnswerRelevancyMetric,
    ToxicityMetric,
)
from deepeval.test_case import LLMTestCase

from app.ai_summary import generate_order_summary, analyze_test_coverage

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SAMPLE_ORDER = {
    "order_id": "test-001",
    "items": [{"item_id": 1, "name": "Classic Beef Burger", "quantity": 1, "price": 199}],
    "total": 199,
    "status": "pending",
}

SAMPLE_PYTEST_OUTPUT = """
FAILED tests/unit/test_order.py::test_create_order_with_invalid_item - AssertionError
PASSED tests/unit/test_order.py::test_create_order_success
PASSED tests/unit/test_payment.py::test_payment_success
1 failed, 2 passed in 1.23s
"""

judge_model = GPTModel(model="gpt-4o-mini")

# ---------------------------------------------------------------------------
# Module-scoped fixtures — each real API call made exactly once per test run
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def summary():
    """Call generate_order_summary exactly once; shared by AIE001-AIE015."""
    print("\n[FIXTURE:summary] Calling generate_order_summary (1 API call for AIE001-AIE015)...")
    result = generate_order_summary(SAMPLE_ORDER)
    print(f"[FIXTURE:summary] Received: {result[:120]}")
    return result


@pytest.fixture(scope="module")
def multi_run_summaries():
    """Call generate_order_summary exactly 3 times; shared by AIE021-AIE022."""
    print("\n[FIXTURE:multi_run] Calling generate_order_summary 3 times for AIE021-AIE022...")
    results = [generate_order_summary(SAMPLE_ORDER) for _ in range(3)]
    for i, r in enumerate(results, 1):
        print(f"[FIXTURE:multi_run] Run {i}: {r[:80]}")
    return results


# ---------------------------------------------------------------------------
# Helper: trigger the fallback by using an invalid API key
# ---------------------------------------------------------------------------

def _trigger_fallback():
    original = os.environ.get("ANTHROPIC_API_KEY", "")
    os.environ["ANTHROPIC_API_KEY"] = "sk-ant-invalid-key-for-testing"
    try:
        return generate_order_summary(SAMPLE_ORDER)
    finally:
        os.environ["ANTHROPIC_API_KEY"] = original


# ---------------------------------------------------------------------------
# Decorator: skip OpenAI-dependent tests gracefully when quota is exceeded
# ---------------------------------------------------------------------------

def _skip_if_openai_quota(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except OpenAIRateLimitError as e:
            pytest.skip(f"OpenAI quota exceeded — add billing credits to run. ({e})")
        except Exception as e:
            if "insufficient_quota" in str(e) or "429" in str(e):
                pytest.skip(f"OpenAI quota exceeded — add billing credits to run. ({e})")
            raise
    return wrapper


# ===========================================================================
# AIE001 - Summary contains correct order total
# ===========================================================================

def test_AIE001_summary_contains_correct_total(summary):
    print(f"[AIE001] Checking total | Expected: 199 or Rs.199 in summary | Actual summary: {summary[:100]}")
    assert "199" in summary or "₹199" in summary, \
        "Summary must contain the correct total amount ₹199"


# ===========================================================================
# AIE002 - Summary mentions all ordered item names
# ===========================================================================

def test_AIE002_summary_mentions_all_ordered_items(summary):
    print(f"[AIE002] Checking item names | Expected: 'Burger' or 'Classic Beef Burger' | Actual summary: {summary[:100]}")
    assert "Burger" in summary or "Classic Beef Burger" in summary, \
        "Summary must mention every item that was ordered"


# ===========================================================================
# AIE003 - Summary does not hallucinate unordered items (DeepEval judge)
# ===========================================================================

@_skip_if_openai_quota
def test_AIE003_summary_does_not_hallucinate_unordered_items(summary):
    print(f"[AIE003] Checking hallucination | Context: order dict | Actual summary: {summary[:100]}")
    test_case = LLMTestCase(
        input="Generate order confirmation",
        actual_output=summary,
        context=[str(SAMPLE_ORDER)],
    )
    metric = HallucinationMetric(threshold=0.5, model=judge_model)
    metric.measure(test_case)
    print(f"[AIE003] Hallucination score: {metric.score} | Reason: {getattr(metric, 'reason', 'n/a')}")
    assert metric.score <= 0.5, "Summary must not mention items not in the order"


# ===========================================================================
# AIE004 - Summary does not invent prices
# ===========================================================================

def test_AIE004_summary_does_not_invent_prices(summary):
    print(f"[AIE004] Checking invented prices | Expected only 199 | Actual summary: {summary[:100]}")
    numbers = re.findall(r"\b\d+\b", summary)
    # Allow 1 (quantity) and 199 (price); flag anything >10 that isn't 199
    non_order_prices = [n for n in numbers if int(n) > 10 and int(n) != 199]
    assert len(non_order_prices) == 0, \
        f"Summary must not contain invented price values. Found suspicious numbers: {non_order_prices}"


# ===========================================================================
# AIE005 - Faithfulness to order data (DeepEval judge)
# ===========================================================================

@_skip_if_openai_quota
def test_AIE005_faithfulness_to_order_data(summary):
    print(f"[AIE005] Checking faithfulness | Retrieval context: order dict | Actual summary: {summary[:100]}")
    test_case = LLMTestCase(
        input="Generate order confirmation",
        actual_output=summary,
        retrieval_context=[str(SAMPLE_ORDER)],
    )
    metric = FaithfulnessMetric(threshold=0.7, model=judge_model)
    metric.measure(test_case)
    print(f"[AIE005] Faithfulness score: {metric.score} | Reason: {getattr(metric, 'reason', 'n/a')}")
    assert metric.score >= 0.7, "Summary must be faithful to the order data"


# ===========================================================================
# AIE006 - Summary does not invent delivery time
# ===========================================================================

def test_AIE006_summary_does_not_invent_delivery_time(summary):
    print(f"[AIE006] Checking delivery time invention | Actual summary: {summary[:100]}")
    patterns = [r"\d+\s*minutes?", r"\d+\s*hours?", r"\bETA\b", r"30 min", r"1 hour"]
    for pattern in patterns:
        assert not re.search(pattern, summary, re.IGNORECASE), \
            f"Summary must not mention a delivery time not in the order. Found pattern: '{pattern}'"


# ===========================================================================
# AIE007 - Summary is relevant to food order confirmation (DeepEval judge)
# ===========================================================================

@_skip_if_openai_quota
def test_AIE007_summary_relevant_to_food_order_confirmation(summary):
    print(f"[AIE007] Checking relevancy | Input: food order confirmation | Actual summary: {summary[:100]}")
    test_case = LLMTestCase(
        input="Generate order confirmation for food order",
        actual_output=summary,
    )
    metric = AnswerRelevancyMetric(threshold=0.7, model=judge_model)
    metric.measure(test_case)
    print(f"[AIE007] Relevancy score: {metric.score} | Reason: {getattr(metric, 'reason', 'n/a')}")
    assert metric.score >= 0.7, "Summary must be relevant to food order confirmation"


# ===========================================================================
# AIE008 - Summary stays on topic
# ===========================================================================

def test_AIE008_summary_stays_on_topic(summary):
    print(f"[AIE008] Checking off-topic content | Actual summary: {summary[:100]}")
    off_topic_words = ["weather", "news", "promotion", "discount"]
    found = [w for w in off_topic_words if w.lower() in summary.lower()]
    assert len(found) == 0, \
        f"Summary must not contain content unrelated to the order. Found: {found}"


# ===========================================================================
# AIE009 - Summary includes closing message
# ===========================================================================

def test_AIE009_summary_includes_closing_message(summary):
    print(f"[AIE009] Checking closing message | Expected: thank/enjoy/appreciate/welcome | Actual summary: {summary[:100]}")
    closing_words = ["thank", "enjoy", "appreciate", "welcome"]
    found = any(w.lower() in summary.lower() for w in closing_words)
    assert found, "Summary must include a friendly closing message"


# ===========================================================================
# AIE010 - Summary is 2 to 5 sentences
# ===========================================================================

def test_AIE010_summary_is_2_to_5_sentences(summary):
    print(f"[AIE010] Checking sentence count | Expected: 2-5 sentences | Actual summary: {summary[:100]}")
    parts = re.split(r"(?<=[.!?])\s+", summary.strip())
    count = len([p for p in parts if p.strip()])
    print(f"[AIE010] Sentence count: {count}")
    # Allow 2-5 to tolerate LLM non-determinism; catches empty or runaway responses
    assert 2 <= count <= 5, \
        f"Summary length should be between 2 and 5 sentences. Got: {count}"


# ===========================================================================
# AIE011 - Summary is plain text, no JSON or code
# ===========================================================================

def test_AIE011_summary_is_plain_text_no_json_or_code(summary):
    print(f"[AIE011] Checking for JSON/code | Actual summary: {summary[:100]}")
    assert "{" not in summary, "Summary must be plain readable text not JSON or code"
    assert "}" not in summary, "Summary must be plain readable text not JSON or code"
    assert "```" not in summary, "Summary must be plain readable text not JSON or code"


# ===========================================================================
# AIE012 - Summary contains no markdown
# ===========================================================================

def test_AIE012_summary_contains_no_markdown(summary):
    print(f"[AIE012] Checking for markdown | Actual summary: {summary[:100]}")
    assert "**" not in summary, "Summary must not contain markdown formatting"
    assert "##" not in summary, "Summary must not contain markdown formatting"
    assert "* " not in summary, "Summary must not contain markdown formatting"


# ===========================================================================
# AIE013 - Summary is in English
# ===========================================================================

def test_AIE013_summary_is_in_english(summary):
    print(f"[AIE013] Checking language | Actual summary: {summary[:100]}")
    ascii_chars = sum(1 for c in summary if ord(c) < 128)
    assert ascii_chars / max(len(summary), 1) > 0.7, \
        "Summary must be written in English"
    assert len(summary) > 20, "Summary must be written in English"


# ===========================================================================
# AIE014 - Summary contains no toxic content (DeepEval judge)
# ===========================================================================

@_skip_if_openai_quota
def test_AIE014_summary_contains_no_toxic_content(summary):
    print(f"[AIE014] Checking toxicity | Actual summary: {summary[:100]}")
    test_case = LLMTestCase(
        input="Generate order confirmation for food order",
        actual_output=summary,
    )
    metric = ToxicityMetric(threshold=0.1, model=judge_model)
    metric.measure(test_case)
    print(f"[AIE014] Toxicity score: {metric.score} | Reason: {getattr(metric, 'reason', 'n/a')}")
    assert metric.score <= 0.1, "Summary must be free of toxic or inappropriate content"


# ===========================================================================
# AIE015 - Summary contains no PII
# ===========================================================================

def test_AIE015_summary_contains_no_pii(summary):
    print(f"[AIE015] Checking PII | Actual summary: {summary[:100]}")
    email_pattern = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
    phone_pattern = r"\b(\+?\d[\d\s\-().]{7,}\d)\b"
    assert not re.search(email_pattern, summary), \
        "Summary must not contain personally identifiable information (email found)"
    assert not re.search(phone_pattern, summary), \
        "Summary must not contain personally identifiable information (phone found)"


# ===========================================================================
# AIE016 - AI summary returns within 15 seconds
# ===========================================================================

def test_AIE016_ai_summary_returns_within_15_seconds():
    print(f"[AIE016] Checking response time | Expected: < 15 seconds")
    start = time.time()
    result = generate_order_summary(SAMPLE_ORDER)
    elapsed = time.time() - start
    print(f"[AIE016] Elapsed: {elapsed:.2f}s | Summary: {result[:80]}")
    assert elapsed < 15, \
        f"AI summary must return within 15 seconds. Took: {elapsed:.2f}s"


# ===========================================================================
# AIE018 - Fallback triggers when API key missing
# ===========================================================================

def test_AIE018_fallback_triggers_when_api_key_missing():
    print(f"[AIE018] Checking fallback on bad API key | Expected: graceful fallback message")
    result = _trigger_fallback()
    safe = result.encode("ascii", "replace").decode()
    print(f"[AIE018] Fallback result: {safe[:100]}")
    assert "confirmed" in result.lower() or "thank" in result.lower(), \
        "System must return fallback gracefully when API key is invalid"


# ===========================================================================
# AIE019 - Fallback contains correct total
# ===========================================================================

def test_AIE019_fallback_contains_correct_total():
    print(f"[AIE019] Checking fallback total | Expected: '199' in fallback")
    result = _trigger_fallback()
    safe = result.encode("ascii", "replace").decode()
    print(f"[AIE019] Fallback result: {safe[:100]}")
    assert "199" in result, "Fallback message must contain the correct order total"


# ===========================================================================
# AIE020 - Fallback is user friendly
# ===========================================================================

def test_AIE020_fallback_is_user_friendly():
    print(f"[AIE020] Checking fallback is user-friendly | Must not expose errors")
    result = _trigger_fallback()
    safe = result.encode("ascii", "replace").decode()
    print(f"[AIE020] Fallback result: {safe[:100]}")
    assert "Error" not in result, "Fallback must not expose internal error messages"
    assert "Exception" not in result, "Fallback must not expose internal error messages"
    assert "Traceback" not in result, "Fallback must not expose internal error messages"


# ===========================================================================
# AIE021 - Consistency check — same order 3 runs all relevant
# ===========================================================================

def test_AIE021_consistency_same_order_3_runs_all_relevant(multi_run_summaries):
    print(f"[AIE021] Checking consistency across 3 runs | Expected: all contain '199' or 'Burger'")
    for i, s in enumerate(multi_run_summaries, 1):
        print(f"[AIE021] Run {i}: {s[:80]}")
        assert "199" in s or "Burger" in s, \
            f"AI summary must consistently produce relevant output. Run {i} failed: {s[:100]}"


# ===========================================================================
# AIE022 - Total always present across 3 runs
# ===========================================================================

def test_AIE022_total_always_present_across_3_runs(multi_run_summaries):
    print(f"[AIE022] Checking total '199' in all 3 runs")
    for i, s in enumerate(multi_run_summaries, 1):
        print(f"[AIE022] Run {i}: {s[:80]}")
        assert "199" in s, \
            f"Total amount must appear consistently in every run. Run {i} missing total: {s[:100]}"


# ===========================================================================
# AIE023 - Coverage analyzer returns at least one gap
# ===========================================================================

def test_AIE023_coverage_analyzer_returns_at_least_one_gap():
    print(f"[AIE023] Checking coverage analyzer returns meaningful output")
    result = analyze_test_coverage(SAMPLE_PYTEST_OUTPUT)
    print(f"[AIE023] Coverage result length: {len(result)} | Preview: {result[:100]}")
    assert len(result) > 50, "Coverage analyzer must identify at least one gap"
    assert not result.startswith("[FALLBACK]"), \
        "Coverage analyzer must identify at least one gap (got fallback instead of real analysis)"


# ===========================================================================
# AIE024 - Coverage analyzer is actionable — LLM as judge (GPT-4o-mini)
# ===========================================================================

@_skip_if_openai_quota
def test_AIE024_coverage_analyzer_is_actionable_llm_as_judge():
    print(f"[AIE024] Checking coverage analyzer actionability via GPT-4o-mini judge")
    analysis = analyze_test_coverage(SAMPLE_PYTEST_OUTPUT)
    print(f"[AIE024] Analysis preview: {analysis[:120]}")

    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": (
                    "Rate this test coverage analysis from 1-10 for being specific and actionable. "
                    "Return only a number.\n\n"
                    f"Analysis:\n{analysis}"
                ),
            }
        ],
        max_tokens=10,
    )
    score_text = response.choices[0].message.content.strip()
    print(f"[AIE024] Judge score: {score_text}")
    match = re.search(r"\d+", score_text)
    assert match, f"Judge returned non-numeric response: {score_text}"
    score = int(match.group())
    assert score >= 7, \
        f"Coverage analyzer output must be specific and actionable. Judge score: {score}/10"


# ===========================================================================
# AIE025 - Coverage analyzer fallback when API unavailable
# ===========================================================================

def test_AIE025_coverage_analyzer_fallback_when_api_unavailable():
    print(f"[AIE025] Checking coverage analyzer fallback on bad API key")
    original = os.environ.get("ANTHROPIC_API_KEY", "")
    os.environ["ANTHROPIC_API_KEY"] = "sk-ant-invalid-key-for-testing"
    try:
        result = analyze_test_coverage(SAMPLE_PYTEST_OUTPUT)
    finally:
        os.environ["ANTHROPIC_API_KEY"] = original
    print(f"[AIE025] Fallback result: {result[:100]}")
    assert result and len(result) > 0, \
        "Coverage analyzer must degrade gracefully when API unavailable"
    assert "Exception" not in result and "Traceback" not in result, \
        "Coverage analyzer must not expose internal errors in fallback"
    assert result.startswith("[FALLBACK]"), \
        "Coverage analyzer fallback must return the [FALLBACK]-prefixed message"
