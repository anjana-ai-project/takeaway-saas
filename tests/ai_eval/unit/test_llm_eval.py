# deepeval==4.0.0  |  openai==2.36.0  |  anthropic==0.100.0
# API facts verified via introspection before writing:
#   LLMTestCase(**kwargs): input, actual_output, context (list), retrieval_context (list)
#   HallucinationMetric / FaithfulnessMetric / AnswerRelevancyMetric / ToxicityMetric
#     -> __init__(threshold, model)  |  .measure(test_case)  |  score on .score
#   GPTModel(model="gpt-4o-mini")
#   pytest-html 4.2.0: extras fixture (function-scoped list), pytest_html.extras.html/text

import os
import re
import sys
import time
import functools

import pytest
import pytest_html
from dotenv import load_dotenv

# Ensure stdout handles UTF-8 on Windows (cp1252 cannot encode ₹)
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
# Module-scoped fixtures — each real API call made exactly once per module
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def summary():
    """Calls generate_order_summary exactly once; shared by AIE001–AIE015."""
    print("\n[FIXTURE:summary] Calling generate_order_summary (1 API call for AIE001-AIE015)...")
    result = generate_order_summary(SAMPLE_ORDER)
    print(f"[FIXTURE:summary] Received: {result[:120]}")
    return result


@pytest.fixture(scope="module")
def multi_run_summaries():
    """Calls generate_order_summary exactly 3 times; shared by AIE021–AIE022."""
    print("\n[FIXTURE:multi_run] Calling generate_order_summary 3 times for AIE021-AIE022...")
    results = [generate_order_summary(SAMPLE_ORDER) for _ in range(3)]
    for i, r in enumerate(results, 1):
        print(f"[FIXTURE:multi_run] Run {i}: {r[:80]}")
    return results


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _trigger_fallback():
    """Call generate_order_summary with an invalid API key to exercise the fallback path."""
    original = os.environ.get("ANTHROPIC_API_KEY", "")
    os.environ["ANTHROPIC_API_KEY"] = "sk-ant-invalid-key-for-testing"
    try:
        return generate_order_summary(SAMPLE_ORDER)
    finally:
        os.environ["ANTHROPIC_API_KEY"] = original


def _eval_card(test_id: str, evaluated: str, expected: str, actual: str,
               extra_rows: str = "") -> str:
    """Return a self-contained HTML card for embedding in the pytest-html report."""
    safe_actual = actual.replace("<", "&lt;").replace(">", "&gt;")[:400]
    return (
        "<div style='font-family:sans-serif;border:1px solid #d0d7de;"
        "border-radius:6px;padding:10px;margin:4px 0;font-size:0.88em'>"
        "<table style='width:100%;border-collapse:collapse'>"
        f"<tr><th style='width:130px;text-align:left;padding:3px 6px;"
        f"background:#f6f8fa;border:1px solid #d0d7de'>Test ID</th>"
        f"<td style='padding:3px 6px;border:1px solid #d0d7de'>"
        f"<strong>{test_id}</strong></td></tr>"
        f"<tr><th style='text-align:left;padding:3px 6px;background:#f6f8fa;"
        f"border:1px solid #d0d7de'>Evaluated</th>"
        f"<td style='padding:3px 6px;border:1px solid #d0d7de'>{evaluated}</td></tr>"
        f"<tr><th style='text-align:left;padding:3px 6px;background:#f6f8fa;"
        f"border:1px solid #d0d7de'>Expected</th>"
        f"<td style='padding:3px 6px;border:1px solid #d0d7de'>"
        f"<code>{expected}</code></td></tr>"
        f"<tr><th style='text-align:left;padding:3px 6px;background:#f6f8fa;"
        f"border:1px solid #d0d7de'>AI Output</th>"
        f"<td style='padding:3px 6px;border:1px solid #d0d7de'>"
        f"<em>{safe_actual}</em></td></tr>"
        f"{extra_rows}"
        "</table></div>"
    )


def _skip_if_openai_quota(fn):
    """Decorator: skip tests that need OpenAI when the account quota is exhausted."""
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
# AIE001 — Summary contains correct order total
# ===========================================================================

def test_AIE001_summary_contains_correct_total(summary, extras):
    print(f"[AIE001] Checking total | Expected: 199 or ₹199 in summary | Actual: {summary[:100]}")
    extras.append(pytest_html.extras.html(
        _eval_card("AIE001", "Summary contains correct order total",
                   "contains '199' or '₹199'", summary)
    ))
    assert "199" in summary or "₹199" in summary, \
        "Summary must contain the correct total amount ₹199"


# ===========================================================================
# AIE002 — Summary mentions all ordered item names
# ===========================================================================

def test_AIE002_summary_mentions_all_ordered_items(summary, extras):
    print(f"[AIE002] Checking item names | Expected: 'Burger' or 'Classic Beef Burger' | Actual: {summary[:100]}")
    extras.append(pytest_html.extras.html(
        _eval_card("AIE002", "Summary mentions ordered item names",
                   "contains 'Burger' or 'Classic Beef Burger'", summary)
    ))
    assert "Burger" in summary or "Classic Beef Burger" in summary, \
        "Summary must mention every item that was ordered"


# ===========================================================================
# AIE003 — Summary does not hallucinate unordered items (DeepEval judge)
# ===========================================================================

@_skip_if_openai_quota
def test_AIE003_summary_does_not_hallucinate_unordered_items(summary, extras):
    print(f"[AIE003] Checking hallucination | Context: order dict | Actual: {summary[:100]}")
    test_case = LLMTestCase(
        input="Generate order confirmation",
        actual_output=summary,
        context=[str(SAMPLE_ORDER)],
    )
    metric = HallucinationMetric(threshold=0.5, model=judge_model)
    metric.measure(test_case)
    score = metric.score
    reason = getattr(metric, "reason", "n/a")
    print(f"[AIE003] Hallucination score: {score} | Reason: {reason}")
    extras.append(pytest_html.extras.html(
        _eval_card("AIE003", "No hallucination of unordered items (DeepEval)",
                   "HallucinationMetric score ≤ 0.5", summary,
                   extra_rows=(
                       f"<tr><th style='text-align:left;padding:3px 6px;background:#f6f8fa;"
                       f"border:1px solid #d0d7de'>Judge Score</th>"
                       f"<td style='padding:3px 6px;border:1px solid #d0d7de'>"
                       f"{score:.3f} — {reason}</td></tr>"
                   ))
    ))
    assert score <= 0.5, "Summary must not mention items not in the order"


# ===========================================================================
# AIE004 — Summary does not invent prices
# ===========================================================================

def test_AIE004_summary_does_not_invent_prices(summary, extras):
    print(f"[AIE004] Checking invented prices | Expected only 199 | Actual: {summary[:100]}")
    numbers = re.findall(r"\b\d+\b", summary)
    non_order_prices = [n for n in numbers if int(n) > 10 and int(n) != 199]
    extras.append(pytest_html.extras.html(
        _eval_card("AIE004", "Summary does not invent prices",
                   "no numbers other than 1 or 199", summary,
                   extra_rows=(
                       f"<tr><th style='text-align:left;padding:3px 6px;background:#f6f8fa;"
                       f"border:1px solid #d0d7de'>Numbers found</th>"
                       f"<td style='padding:3px 6px;border:1px solid #d0d7de'>"
                       f"{numbers}</td></tr>"
                   ))
    ))
    assert len(non_order_prices) == 0, \
        f"Summary must not contain invented price values. Found: {non_order_prices}"


# ===========================================================================
# AIE005 — Faithfulness to order data (DeepEval judge)
# ===========================================================================

@_skip_if_openai_quota
def test_AIE005_faithfulness_to_order_data(summary, extras):
    print(f"[AIE005] Checking faithfulness | Retrieval context: order dict | Actual: {summary[:100]}")
    test_case = LLMTestCase(
        input="Generate order confirmation",
        actual_output=summary,
        retrieval_context=[str(SAMPLE_ORDER)],
    )
    metric = FaithfulnessMetric(threshold=0.7, model=judge_model)
    metric.measure(test_case)
    score = metric.score
    reason = getattr(metric, "reason", "n/a")
    print(f"[AIE005] Faithfulness score: {score} | Reason: {reason}")
    extras.append(pytest_html.extras.html(
        _eval_card("AIE005", "Faithfulness to order data (DeepEval)",
                   "FaithfulnessMetric score ≥ 0.7", summary,
                   extra_rows=(
                       f"<tr><th style='text-align:left;padding:3px 6px;background:#f6f8fa;"
                       f"border:1px solid #d0d7de'>Judge Score</th>"
                       f"<td style='padding:3px 6px;border:1px solid #d0d7de'>"
                       f"{score:.3f} — {reason}</td></tr>"
                   ))
    ))
    assert score >= 0.7, "Summary must be faithful to the order data"


# ===========================================================================
# AIE006 — Summary does not invent delivery time
# ===========================================================================

def test_AIE006_summary_does_not_invent_delivery_time(summary, extras):
    print(f"[AIE006] Checking delivery time invention | Actual: {summary[:100]}")
    patterns = [r"\d+\s*minutes?", r"\d+\s*hours?", r"\bETA\b", r"30 min", r"1 hour"]
    found_patterns = [p for p in patterns if re.search(p, summary, re.IGNORECASE)]
    extras.append(pytest_html.extras.html(
        _eval_card("AIE006", "Summary does not invent delivery time",
                   "no time/ETA patterns in text", summary,
                   extra_rows=(
                       f"<tr><th style='text-align:left;padding:3px 6px;background:#f6f8fa;"
                       f"border:1px solid #d0d7de'>Patterns checked</th>"
                       f"<td style='padding:3px 6px;border:1px solid #d0d7de'>"
                       f"minutes / hours / ETA / '30 min' / '1 hour'</td></tr>"
                   ))
    ))
    assert len(found_patterns) == 0, \
        f"Summary must not mention a delivery time. Found patterns: {found_patterns}"


# ===========================================================================
# AIE007 — Summary is relevant to food order confirmation (DeepEval judge)
# ===========================================================================

@_skip_if_openai_quota
def test_AIE007_summary_relevant_to_food_order_confirmation(summary, extras):
    print(f"[AIE007] Checking relevancy | Input: food order confirmation | Actual: {summary[:100]}")
    test_case = LLMTestCase(
        input="Generate order confirmation for food order",
        actual_output=summary,
    )
    metric = AnswerRelevancyMetric(threshold=0.7, model=judge_model)
    metric.measure(test_case)
    score = metric.score
    reason = getattr(metric, "reason", "n/a")
    print(f"[AIE007] Relevancy score: {score} | Reason: {reason}")
    extras.append(pytest_html.extras.html(
        _eval_card("AIE007", "Summary relevant to food order confirmation (DeepEval)",
                   "AnswerRelevancyMetric score ≥ 0.7", summary,
                   extra_rows=(
                       f"<tr><th style='text-align:left;padding:3px 6px;background:#f6f8fa;"
                       f"border:1px solid #d0d7de'>Judge Score</th>"
                       f"<td style='padding:3px 6px;border:1px solid #d0d7de'>"
                       f"{score:.3f} — {reason}</td></tr>"
                   ))
    ))
    assert score >= 0.7, "Summary must be relevant to food order confirmation"


# ===========================================================================
# AIE008 — Summary stays on topic
# ===========================================================================

def test_AIE008_summary_stays_on_topic(summary, extras):
    print(f"[AIE008] Checking off-topic content | Actual: {summary[:100]}")
    off_topic_words = ["weather", "news", "promotion", "discount"]
    found = [w for w in off_topic_words if w.lower() in summary.lower()]
    extras.append(pytest_html.extras.html(
        _eval_card("AIE008", "Summary stays on topic",
                   "no off-topic words: weather / news / promotion / discount", summary,
                   extra_rows=(
                       f"<tr><th style='text-align:left;padding:3px 6px;background:#f6f8fa;"
                       f"border:1px solid #d0d7de'>Off-topic found</th>"
                       f"<td style='padding:3px 6px;border:1px solid #d0d7de'>"
                       f"{found if found else 'none'}</td></tr>"
                   ))
    ))
    assert len(found) == 0, \
        f"Summary must not contain content unrelated to the order. Found: {found}"


# ===========================================================================
# AIE009 — Summary includes closing message
# ===========================================================================

def test_AIE009_summary_includes_closing_message(summary, extras):
    print(f"[AIE009] Checking closing message | Actual: {summary[:100]}")
    closing_words = ["thank", "enjoy", "appreciate", "welcome"]
    found = [w for w in closing_words if w.lower() in summary.lower()]
    extras.append(pytest_html.extras.html(
        _eval_card("AIE009", "Summary includes closing message",
                   "contains: thank / enjoy / appreciate / welcome", summary,
                   extra_rows=(
                       f"<tr><th style='text-align:left;padding:3px 6px;background:#f6f8fa;"
                       f"border:1px solid #d0d7de'>Closing words found</th>"
                       f"<td style='padding:3px 6px;border:1px solid #d0d7de'>"
                       f"{found}</td></tr>"
                   ))
    ))
    assert len(found) > 0, "Summary must include a friendly closing message"


# ===========================================================================
# AIE010 — Summary is 2 to 5 sentences
# ===========================================================================

def test_AIE010_summary_is_2_to_5_sentences(summary, extras):
    print(f"[AIE010] Checking sentence count | Actual: {summary[:100]}")
    parts = re.split(r"(?<=[.!?])\s+", summary.strip())
    count = len([p for p in parts if p.strip()])
    print(f"[AIE010] Sentence count: {count}")
    extras.append(pytest_html.extras.html(
        _eval_card("AIE010", "Summary is 2–5 sentences",
                   "sentence count between 2 and 5", summary,
                   extra_rows=(
                       f"<tr><th style='text-align:left;padding:3px 6px;background:#f6f8fa;"
                       f"border:1px solid #d0d7de'>Sentence count</th>"
                       f"<td style='padding:3px 6px;border:1px solid #d0d7de'>"
                       f"{count}</td></tr>"
                   ))
    ))
    assert 2 <= count <= 5, \
        f"Summary length should be between 2 and 5 sentences. Got: {count}"


# ===========================================================================
# AIE011 — Summary is plain text, no JSON or code
# ===========================================================================

def test_AIE011_summary_is_plain_text_no_json_or_code(summary, extras):
    print(f"[AIE011] Checking for JSON/code | Actual: {summary[:100]}")
    violations = [c for c in ["{", "}", "```"] if c in summary]
    extras.append(pytest_html.extras.html(
        _eval_card("AIE011", "Summary is plain text — no JSON or code",
                   "no { } or ``` in text", summary,
                   extra_rows=(
                       f"<tr><th style='text-align:left;padding:3px 6px;background:#f6f8fa;"
                       f"border:1px solid #d0d7de'>Violations found</th>"
                       f"<td style='padding:3px 6px;border:1px solid #d0d7de'>"
                       f"{violations if violations else 'none'}</td></tr>"
                   ))
    ))
    assert "{" not in summary, "Summary must be plain readable text not JSON or code"
    assert "}" not in summary, "Summary must be plain readable text not JSON or code"
    assert "```" not in summary, "Summary must be plain readable text not JSON or code"


# ===========================================================================
# AIE012 — Summary contains no markdown
# ===========================================================================

def test_AIE012_summary_contains_no_markdown(summary, extras):
    print(f"[AIE012] Checking for markdown | Actual: {summary[:100]}")
    violations = [m for m in ["**", "##", "* "] if m in summary]
    extras.append(pytest_html.extras.html(
        _eval_card("AIE012", "Summary contains no markdown",
                   "no ** ## or '* ' sequences", summary,
                   extra_rows=(
                       f"<tr><th style='text-align:left;padding:3px 6px;background:#f6f8fa;"
                       f"border:1px solid #d0d7de'>Violations found</th>"
                       f"<td style='padding:3px 6px;border:1px solid #d0d7de'>"
                       f"{violations if violations else 'none'}</td></tr>"
                   ))
    ))
    assert "**" not in summary, "Summary must not contain markdown formatting"
    assert "##" not in summary, "Summary must not contain markdown formatting"
    assert "* " not in summary, "Summary must not contain markdown formatting"


# ===========================================================================
# AIE013 — Summary is in English
# ===========================================================================

def test_AIE013_summary_is_in_english(summary, extras):
    print(f"[AIE013] Checking language | Actual: {summary[:100]}")
    ascii_ratio = sum(1 for c in summary if ord(c) < 128) / max(len(summary), 1)
    extras.append(pytest_html.extras.html(
        _eval_card("AIE013", "Summary is in English",
                   ">70% ASCII chars and length > 20", summary,
                   extra_rows=(
                       f"<tr><th style='text-align:left;padding:3px 6px;background:#f6f8fa;"
                       f"border:1px solid #d0d7de'>ASCII ratio</th>"
                       f"<td style='padding:3px 6px;border:1px solid #d0d7de'>"
                       f"{ascii_ratio:.1%} | length: {len(summary)}</td></tr>"
                   ))
    ))
    assert ascii_ratio > 0.7, "Summary must be written in English"
    assert len(summary) > 20, "Summary must be written in English"


# ===========================================================================
# AIE014 — Summary contains no toxic content (DeepEval judge)
# ===========================================================================

@_skip_if_openai_quota
def test_AIE014_summary_contains_no_toxic_content(summary, extras):
    print(f"[AIE014] Checking toxicity | Actual: {summary[:100]}")
    test_case = LLMTestCase(
        input="Generate order confirmation for food order",
        actual_output=summary,
    )
    metric = ToxicityMetric(threshold=0.1, model=judge_model)
    metric.measure(test_case)
    score = metric.score
    reason = getattr(metric, "reason", "n/a")
    print(f"[AIE014] Toxicity score: {score} | Reason: {reason}")
    extras.append(pytest_html.extras.html(
        _eval_card("AIE014", "No toxic content (DeepEval)",
                   "ToxicityMetric score ≤ 0.1", summary,
                   extra_rows=(
                       f"<tr><th style='text-align:left;padding:3px 6px;background:#f6f8fa;"
                       f"border:1px solid #d0d7de'>Judge Score</th>"
                       f"<td style='padding:3px 6px;border:1px solid #d0d7de'>"
                       f"{score:.3f} — {reason}</td></tr>"
                   ))
    ))
    assert score <= 0.1, "Summary must be free of toxic or inappropriate content"


# ===========================================================================
# AIE015 — Summary contains no PII
# ===========================================================================

def test_AIE015_summary_contains_no_pii(summary, extras):
    print(f"[AIE015] Checking PII | Actual: {summary[:100]}")
    email_pat = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
    phone_pat = r"\b(\+?\d[\d\s\-().]{7,}\d)\b"
    email_found = re.search(email_pat, summary)
    phone_found = re.search(phone_pat, summary)
    extras.append(pytest_html.extras.html(
        _eval_card("AIE015", "Summary contains no PII",
                   "no email or phone patterns", summary,
                   extra_rows=(
                       f"<tr><th style='text-align:left;padding:3px 6px;background:#f6f8fa;"
                       f"border:1px solid #d0d7de'>PII found</th>"
                       f"<td style='padding:3px 6px;border:1px solid #d0d7de'>"
                       f"email: {email_found.group() if email_found else 'none'} | "
                       f"phone: {phone_found.group() if phone_found else 'none'}"
                       f"</td></tr>"
                   ))
    ))
    assert not email_found, "Summary must not contain personally identifiable information (email)"
    assert not phone_found, "Summary must not contain personally identifiable information (phone)"


# ===========================================================================
# AIE016 — AI summary returns within 15 seconds
# ===========================================================================

def test_AIE016_ai_summary_returns_within_15_seconds(extras):
    print(f"[AIE016] Checking response time | Expected: < 15 seconds")
    start = time.time()
    result = generate_order_summary(SAMPLE_ORDER)
    elapsed = time.time() - start
    print(f"[AIE016] Elapsed: {elapsed:.2f}s | Summary: {result[:80]}")
    extras.append(pytest_html.extras.html(
        _eval_card("AIE016", "AI summary returns within 15 seconds",
                   "elapsed < 15 s", result,
                   extra_rows=(
                       f"<tr><th style='text-align:left;padding:3px 6px;background:#f6f8fa;"
                       f"border:1px solid #d0d7de'>Elapsed time</th>"
                       f"<td style='padding:3px 6px;border:1px solid #d0d7de'>"
                       f"{elapsed:.2f} s</td></tr>"
                   ))
    ))
    assert elapsed < 15, \
        f"AI summary must return within 15 seconds. Took: {elapsed:.2f}s"


# ===========================================================================
# AIE018 — Fallback triggers when API key missing
# ===========================================================================

def test_AIE018_fallback_triggers_when_api_key_missing(extras):
    print(f"[AIE018] Checking fallback on bad API key | Expected: graceful fallback message")
    result = _trigger_fallback()
    safe = result.encode("ascii", "replace").decode()
    print(f"[AIE018] Fallback result: {safe[:100]}")
    extras.append(pytest_html.extras.html(
        _eval_card("AIE018", "Fallback triggers when API key missing",
                   "contains 'confirmed' or 'thank'", result)
    ))
    assert "confirmed" in result.lower() or "thank" in result.lower(), \
        "System must return fallback gracefully when API key is invalid"


# ===========================================================================
# AIE019 — Fallback contains correct total
# ===========================================================================

def test_AIE019_fallback_contains_correct_total(extras):
    print(f"[AIE019] Checking fallback total | Expected: '199' in fallback")
    result = _trigger_fallback()
    safe = result.encode("ascii", "replace").decode()
    print(f"[AIE019] Fallback result: {safe[:100]}")
    extras.append(pytest_html.extras.html(
        _eval_card("AIE019", "Fallback contains correct total",
                   "contains '199'", result)
    ))
    assert "199" in result, "Fallback message must contain the correct order total"


# ===========================================================================
# AIE020 — Fallback is user-friendly
# ===========================================================================

def test_AIE020_fallback_is_user_friendly(extras):
    print(f"[AIE020] Checking fallback is user-friendly | Must not expose errors")
    result = _trigger_fallback()
    safe = result.encode("ascii", "replace").decode()
    print(f"[AIE020] Fallback result: {safe[:100]}")
    bad_terms = [t for t in ["Error", "Exception", "Traceback"] if t in result]
    extras.append(pytest_html.extras.html(
        _eval_card("AIE020", "Fallback is user-friendly",
                   "no 'Error' / 'Exception' / 'Traceback'", result,
                   extra_rows=(
                       f"<tr><th style='text-align:left;padding:3px 6px;background:#f6f8fa;"
                       f"border:1px solid #d0d7de'>Bad terms found</th>"
                       f"<td style='padding:3px 6px;border:1px solid #d0d7de'>"
                       f"{bad_terms if bad_terms else 'none'}</td></tr>"
                   ))
    ))
    assert "Error" not in result, "Fallback must not expose internal error messages"
    assert "Exception" not in result, "Fallback must not expose internal error messages"
    assert "Traceback" not in result, "Fallback must not expose internal error messages"


# ===========================================================================
# AIE021 — Consistency: same order 3 runs all relevant
# ===========================================================================

def test_AIE021_consistency_same_order_3_runs_all_relevant(multi_run_summaries, extras):
    print(f"[AIE021] Checking consistency across 3 runs | Expected: all contain '199' or 'Burger'")
    rows = ""
    for i, s in enumerate(multi_run_summaries, 1):
        print(f"[AIE021] Run {i}: {s[:80]}")
        safe_s = s.replace("<", "&lt;").replace(">", "&gt;")[:200]
        rows += (
            f"<tr><th style='text-align:left;padding:3px 6px;background:#f6f8fa;"
            f"border:1px solid #d0d7de'>Run {i}</th>"
            f"<td style='padding:3px 6px;border:1px solid #d0d7de'><em>{safe_s}</em></td></tr>"
        )
    extras.append(pytest_html.extras.html(
        _eval_card("AIE021", "Consistency — 3 runs all relevant",
                   "all 3 contain '199' or 'Burger'",
                   f"3 separate calls made — see rows below", extra_rows=rows)
    ))
    for i, s in enumerate(multi_run_summaries, 1):
        assert "199" in s or "Burger" in s, \
            f"AI summary must consistently produce relevant output. Run {i} failed: {s[:100]}"


# ===========================================================================
# AIE022 — Total always present across 3 runs
# ===========================================================================

def test_AIE022_total_always_present_across_3_runs(multi_run_summaries, extras):
    print(f"[AIE022] Checking total '199' in all 3 runs")
    rows = ""
    for i, s in enumerate(multi_run_summaries, 1):
        print(f"[AIE022] Run {i}: {s[:80]}")
        has_total = "✓" if "199" in s else "✗"
        safe_s = s.replace("<", "&lt;").replace(">", "&gt;")[:200]
        rows += (
            f"<tr><th style='text-align:left;padding:3px 6px;background:#f6f8fa;"
            f"border:1px solid #d0d7de'>Run {i} ({has_total})</th>"
            f"<td style='padding:3px 6px;border:1px solid #d0d7de'><em>{safe_s}</em></td></tr>"
        )
    extras.append(pytest_html.extras.html(
        _eval_card("AIE022", "Total always present across 3 runs",
                   "all 3 summaries contain '199'",
                   "3 separate calls made — see rows below", extra_rows=rows)
    ))
    for i, s in enumerate(multi_run_summaries, 1):
        assert "199" in s, \
            f"Total amount must appear consistently. Run {i} missing total: {s[:100]}"


# ===========================================================================
# AIE023 — Coverage analyzer returns at least one gap
# ===========================================================================

def test_AIE023_coverage_analyzer_returns_at_least_one_gap(extras):
    print(f"[AIE023] Checking coverage analyzer returns meaningful output")
    result = analyze_test_coverage(SAMPLE_PYTEST_OUTPUT)
    print(f"[AIE023] Coverage result length: {len(result)} | Preview: {result[:100]}")
    extras.append(pytest_html.extras.html(
        _eval_card("AIE023", "Coverage analyzer returns at least one gap",
                   "len(result) > 50 and not [FALLBACK]", result)
    ))
    assert len(result) > 50, "Coverage analyzer must identify at least one gap"
    assert not result.startswith("[FALLBACK]"), \
        "Coverage analyzer must return real analysis, not the fallback"


# ===========================================================================
# AIE024 — Coverage analyzer is actionable — LLM as judge (GPT-4o-mini)
# ===========================================================================

@_skip_if_openai_quota
def test_AIE024_coverage_analyzer_is_actionable_llm_as_judge(extras):
    print(f"[AIE024] Checking coverage analyzer actionability via GPT-4o-mini judge")
    analysis = analyze_test_coverage(SAMPLE_PYTEST_OUTPUT)
    print(f"[AIE024] Analysis preview: {analysis[:120]}")

    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": (
                "Rate this test coverage analysis from 1-10 for being specific and actionable. "
                "Return only a number.\n\n"
                f"Analysis:\n{analysis}"
            ),
        }],
        max_tokens=10,
    )
    score_text = response.choices[0].message.content.strip()
    print(f"[AIE024] Judge score: {score_text}")
    match = re.search(r"\d+", score_text)
    assert match, f"Judge returned non-numeric response: {score_text}"
    score = int(match.group())
    extras.append(pytest_html.extras.html(
        _eval_card("AIE024", "Coverage analyzer is actionable (GPT-4o-mini judge)",
                   "judge score ≥ 7/10", analysis,
                   extra_rows=(
                       f"<tr><th style='text-align:left;padding:3px 6px;background:#f6f8fa;"
                       f"border:1px solid #d0d7de'>Judge Score</th>"
                       f"<td style='padding:3px 6px;border:1px solid #d0d7de'>"
                       f"{score}/10</td></tr>"
                   ))
    ))
    assert score >= 7, \
        f"Coverage analyzer output must be specific and actionable. Judge score: {score}/10"


# ===========================================================================
# AIE025 — Coverage analyzer fallback when API unavailable
# ===========================================================================

def test_AIE025_coverage_analyzer_fallback_when_api_unavailable(extras):
    print(f"[AIE025] Checking coverage analyzer fallback on bad API key")
    original = os.environ.get("ANTHROPIC_API_KEY", "")
    os.environ["ANTHROPIC_API_KEY"] = "sk-ant-invalid-key-for-testing"
    try:
        result = analyze_test_coverage(SAMPLE_PYTEST_OUTPUT)
    finally:
        os.environ["ANTHROPIC_API_KEY"] = original
    print(f"[AIE025] Fallback result: {result[:100]}")
    extras.append(pytest_html.extras.html(
        _eval_card("AIE025", "Coverage analyzer fallback when API unavailable",
                   "result starts with [FALLBACK]", result)
    ))
    assert result and len(result) > 0, \
        "Coverage analyzer must degrade gracefully when API unavailable"
    assert "Exception" not in result and "Traceback" not in result, \
        "Coverage analyzer must not expose internal errors in fallback"
    assert result.startswith("[FALLBACK]"), \
        "Coverage analyzer fallback must return the [FALLBACK]-prefixed message"
