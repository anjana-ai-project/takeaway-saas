"""
conftest.py for tests/ai_eval/
Configures the pytest-html report (v4.2.0) for AI evaluation runs:
  - Custom title
  - Extra columns: Test ID | What Was Evaluated | Expected
  - Per-test extras (AI Output, Expected) injected by individual tests
    via the `extras` fixture provided by pytest-html.
"""

import re
import pytest
import pytest_html

# ---------------------------------------------------------------------------
# Per-test metadata: test_id -> (short description, expected value string)
# ---------------------------------------------------------------------------

_EVAL_META = {
    "AIE001": ("Summary contains correct order total",        "Text contains '199' or '₹199'"),
    "AIE002": ("Summary mentions ordered item names",         "Text contains 'Burger' or 'Classic Beef Burger'"),
    "AIE003": ("No hallucination of unordered items",         "DeepEval HallucinationMetric score ≤ 0.5"),
    "AIE004": ("Summary does not invent prices",              "No numbers other than 1 or 199 in text"),
    "AIE005": ("Faithfulness to order data",                  "DeepEval FaithfulnessMetric score ≥ 0.7"),
    "AIE006": ("Summary does not invent delivery time",       "No time/ETA patterns in text"),
    "AIE007": ("Summary relevant to food order confirmation", "DeepEval AnswerRelevancyMetric score ≥ 0.7"),
    "AIE008": ("Summary stays on topic",                      "No off-topic words: weather/news/promotion/discount"),
    "AIE009": ("Summary includes closing message",            "Contains: thank / enjoy / appreciate / welcome"),
    "AIE010": ("Summary is 2–5 sentences",                    "Sentence count between 2 and 5"),
    "AIE011": ("Summary is plain text — no JSON or code",     "No { } or ``` characters"),
    "AIE012": ("Summary contains no markdown",                "No ** ## or '* ' sequences"),
    "AIE013": ("Summary is in English",                       ">70% ASCII chars and length > 20"),
    "AIE014": ("No toxic content",                            "DeepEval ToxicityMetric score ≤ 0.1"),
    "AIE015": ("Summary contains no PII",                     "No email or phone patterns found"),
    "AIE016": ("AI summary returns within 15 seconds",        "Elapsed time < 15 s"),
    "AIE018": ("Fallback triggers when API key missing",      "Result contains 'confirmed' or 'thank'"),
    "AIE019": ("Fallback contains correct total",             "Result contains '199'"),
    "AIE020": ("Fallback is user-friendly",                   "No 'Error' / 'Exception' / 'Traceback'"),
    "AIE021": ("Consistency — 3 runs all relevant",           "All 3 summaries contain '199' or 'Burger'"),
    "AIE022": ("Total always present across 3 runs",          "All 3 summaries contain '199'"),
    "AIE023": ("Coverage analyzer returns at least one gap",  "len(result) > 50 and not [FALLBACK]"),
    "AIE024": ("Coverage analyzer is actionable (LLM judge)", "GPT-4o-mini judge score ≥ 7/10"),
    "AIE025": ("Coverage analyzer fallback when unavailable", "Result starts with [FALLBACK]"),
}


# ---------------------------------------------------------------------------
# Hook: report title
# ---------------------------------------------------------------------------

def pytest_html_report_title(report):
    report.title = "AI Evaluation Report — Takeaway SaaS"


# ---------------------------------------------------------------------------
# Hook: summary banner below the pie chart
# ---------------------------------------------------------------------------

def pytest_html_results_summary(prefix, summary, postfix, session):
    from markupsafe import Markup
    prefix.extend([
        Markup(
            "<p style='font-size:0.9em;color:#555'>"
            "<strong>Subject under test:</strong> <code>generate_order_summary()</code> "
            "and <code>analyze_test_coverage()</code> via Claude (Anthropic API) &nbsp;|&nbsp; "
            "<strong>Judge model:</strong> GPT-4o-mini (OpenAI) via DeepEval 4.0.0"
            "</p>"
        )
    ])


# ---------------------------------------------------------------------------
# Hook: attach test_id / evaluated / expected to the report object
# ---------------------------------------------------------------------------

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call":
        m = re.search(r"AIE\d+", item.name)
        test_id = m.group(0) if m else "—"
        meta = _EVAL_META.get(test_id, ("", ""))
        report.test_id  = test_id
        report.evaluated = meta[0]
        report.expected  = meta[1]


# ---------------------------------------------------------------------------
# Hooks: extra columns in the results table
# ---------------------------------------------------------------------------

def pytest_html_results_table_header(cells):
    # Default columns: Result | Test | Duration | Links
    # Insert after Result (index 1): Test ID | What Was Evaluated | Expected
    cells.insert(1, "<th>Test ID</th>")
    cells.insert(2, "<th>What Was Evaluated</th>")
    cells.insert(3, "<th>Expected</th>")


def pytest_html_results_table_row(report, cells):
    tid       = getattr(report, "test_id",  "—")
    evaluated = getattr(report, "evaluated", "")
    expected  = getattr(report, "expected",  "")
    cells.insert(1, f"<td style='white-space:nowrap'>{tid}</td>")
    cells.insert(2, f"<td>{evaluated}</td>")
    cells.insert(3, f"<td style='font-size:0.85em;color:#444'>{expected}</td>")
