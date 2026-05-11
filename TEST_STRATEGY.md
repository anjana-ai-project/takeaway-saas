# Test Strategy — Takeaway SaaS

## 1. Scope

### What is being tested:
- Menu display and item retrieval
- Order creation and total calculation
- Payment processing (mock) — success and failure paths
- AI-generated order summary — correctness, faithfulness, hallucination, toxicity
- Full user journeys via browser automation
- All API endpoints — request validation, response schema, error handling

### What is NOT being tested:
- Real payment gateway integration — mock only
- Authentication and authorisation — not implemented
- Database layer — in-memory storage only
- Performance and load — not in scope for this assessment
- Cross-browser compatibility — Chromium only

---

## 2. Risk Assessment

A senior QA starts with risk — not code.

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Incorrect order total calculation | Medium | High | Unit tests on calculation logic |
| Invalid menu items accepted in order | Medium | High | Validation unit tests + API tests |
| Payment failure not handled gracefully | Low | High | Explicit failure path tests |
| AI summary hallucinating items | Medium | High | DeepEval hallucination metric |
| API contract breaking between frontend and backend | Medium | High | Playwright API tests on every endpoint |
| Duplicate order IDs | Low | High | UUID4 — documented as gap for production |
| Payment idempotency issues | Medium | High | Documented as gap — not implemented |

---

## 3. Test Levels

### Level 1 — Unit Tests (pytest)
**Purpose:** Test individual functions in complete isolation. No network, no server, no database.

**What is tested:**
- Menu data structure and retrieval functions
- Order total calculation with quantity multiplication
- Order validation — empty items, invalid item IDs
- Payment logic — success, failure, zero amount
- AI summary fallback when API unavailable

**Principles:**
- No network calls
- Fast — entire suite runs in under 1 second
- Deterministic — same input always gives same output
- Claude API mocked in all unit tests

**Coverage goal:** 90%+ on critical business logic. Not chasing 100% blindly.

---

### Level 2 — Integration Tests (pytest + TestClient)
**Purpose:** Test multiple modules working together via HTTP. Verify request/response contracts.

**What is tested:**
- POST /order — valid order, empty order, invalid item ID
- Full flow — create order then process payment
- Full flow — create order then simulate payment failure
- Error responses return correct HTTP status codes

**Principles:**
- Uses FastAPI TestClient — no real server needed
- Tests module boundaries not just individual functions
- Each test is independent — no shared state

---

### Level 3 — API Tests (Playwright request API)
**Purpose:** Validate every endpoint against a running server. Tests HTTP contracts explicitly.

**What is tested:**
- All endpoints: GET /menu, GET /menu/{id}, POST /order, POST /payment, GET /summary
- Status codes for all happy and error paths
- Response schema — correct fields present
- Boundary values — invalid IDs, zero amounts, missing fields

**Principles:**
- No browser — pure HTTP calls
- Fails explicitly if server is not running
- Separate config (playwright.api.config.js) — no auto server start
- All assertions show expected vs actual values

---

### Level 4 — E2E Tests (Playwright — browser)
**Purpose:** Simulate real user behaviour in a real browser. Validates complete user journeys.

**What is tested:**
- Menu browsing and cart management
- UPI payment happy path — full flow to success
- Card payment with simulated failure — failure message and retry
- Cash on delivery flow — different success message
- Validation — UPI format, card number length, expiry format, CVV
- AI summary appearing after successful payment
- Navigation — back buttons, logo reset

**Principles:**
- Real browser (Chromium)
- Fails explicitly if server is not running
- Separate config (playwright.ui.config.js)
- ARRANGE / ACT / ASSERT pattern in every test
- Every assertion has descriptive message showing expected vs actual

---

### Level 5 — AI Evaluation Tests (DeepEval + Custom pytest)
**Purpose:** Evaluate LLM output quality. Treats AI summary as a production component requiring formal evaluation.

**What is tested:**
- Correctness — contains correct total and item names
- Hallucination — does not mention items not in order (DeepEval)
- Faithfulness — all facts grounded in order data (DeepEval)
- Relevance — response is relevant to food order context (DeepEval)
- Toxicity — no harmful content (DeepEval)
- Format — plain text, no JSON, no markdown, English only
- Latency — returns within 15 seconds
- Fallback — graceful degradation when API unavailable
- Consistency — same order produces relevant output across 3 runs
- Coverage analyzer — actionable output scored by GPT-4o-mini as judge

**Judge model:** GPT-4o-mini (OpenAI) — deliberately different from generator model (Claude) to avoid self-evaluation bias.

**Run manually only** — not in CI pipeline. Results committed to reports/ folder.

---

## 4. Test Data Strategy

All test data is externalized and driven by data files — not hardcoded in test files.

**Python tests:** Factory functions in `tests/conftest.py`
```python
create_valid_order_payload()
create_invalid_order_payload()
create_empty_order_payload()
create_valid_payment_payload()
create_failure_payment_payload()
```

**Playwright tests:** Factory functions in `tests/e2e/helpers/test-data.js` reading from `tests/e2e/helpers/test-data.json`
```javascript
createValidUPIPayment()
createValidCardPayment()
createValidOrderPayload()
createFailurePaymentPayload()
```

**Principles:**
- Each test gets fresh isolated data — no shared state
- Data values defined once in JSON — change in one place reflects everywhere
- Factory functions named clearly: `create<Type><Variant>()`

---

## 5. AI Usage in Testing

### Claude used for test case generation:
Prompt used:
> "You are a senior QA engineer. Given this Python function, generate comprehensive pytest test cases covering happy path, edge cases, boundary values, and error scenarios."

**What Claude identified that I had not initially considered:**
- Quantity of zero in an order line item
- Item ID as string instead of integer
- Payment amount as negative number
- Empty string UPI ID passing empty check but failing format validation

Every AI-generated test case was critically reviewed and validated before inclusion. This reflects how I would govern AI-assisted testing in production.

### AI in the application:
- Claude API generates personalised order summary after every successful payment
- AI test coverage analyzer endpoint identifies untested scenarios from pytest output
- LLM output formally evaluated using DeepEval with independent judge model

---

## 6. Coverage Goals

| Test Layer | Coverage Goal | Rationale |
|---|---|---|
| Unit — business logic | 90%+ | Critical calculation and validation logic must be exhaustively tested |
| Integration — API endpoints | 100% of endpoints | Every endpoint must have at least one happy path and one error path test |
| E2E — user journeys | Critical paths only | Menu→Order→Payment success and failure — high value, not exhaustive |
| AI eval — LLM output | All defined parameters | Correctness, faithfulness, hallucination, toxicity, format, latency, fallback |

**Principle:** Don't chase 100% coverage blindly. Focus on risk and business value.

---

## 7. CI/CD Strategy

**Pipeline:** GitHub Actions — triggers on every push to main and every pull request.

**Job 1 — Backend Tests (parallel):**
- Python 3.11
- Install dependencies
- Run pytest tests/unit and tests/integration
- Fails build if any test fails

**Job 2 — Playwright Tests (parallel):**
- Node 18 + Python 3.11
- Install Playwright + Chromium
- Start FastAPI server via webServer config
- Run all UI and API Playwright tests
- Upload HTML report as artifact

**Both jobs run in parallel** — faster feedback on every push.

**AI eval tests excluded from CI** — run manually, cost money, results committed to reports/ folder.

**Principle:** Fail fast. A failing test blocks the merge. Quality is a gate not an afterthought.

---

## 8. What is Not Tested and Why

| Gap | Reason | Production Fix |
|---|---|---|
| Real payment gateway | Mock only — no gateway credentials | Integrate Razorpay with contract tests |
| Authentication | Not implemented | JWT auth with authorisation test scenarios |
| Database layer | In-memory storage | PostgreSQL with data layer tests and migration tests |
| Rate limiting | Not implemented | API gateway rate limiting with load tests |
| Payment idempotency | Not implemented | Idempotency keys with duplicate payment tests |
| Performance/load | Out of scope | Locust load tests validating concurrent order handling |
| Cross-browser | Chromium only | Add Firefox and WebKit to Playwright config |
| Observability | No logging/metrics | Structured logging with log assertion tests |
| Contract testing | Out of scope | Pact for frontend-backend contract validation |
| Visual regression | Out of scope | Playwright screenshots with visual comparison |

---

## 9. Future Test Additions

In priority order for a production system:

1. **Contract testing (Pact)** — validate API contracts between frontend and backend
2. **Load testing (Locust)** — validate concurrent order handling and payment processing
3. **Authentication tests** — JWT token validation, role-based access control
4. **Database tests** — data persistence, migration scripts, transaction integrity
5. **Visual regression** — screenshot comparison for UI changes
6. **Testcontainers** — real PostgreSQL in integration tests instead of in-memory
7. **Idempotency tests** — duplicate payment prevention
8. **Rate limiting tests** — API abuse prevention validation
9. **Observability tests** — log output validation for key business events
10. **Cross-browser tests** — Firefox and WebKit coverage