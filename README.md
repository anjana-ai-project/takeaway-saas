# Takeaway SaaS

A simple food ordering SaaS system built to demonstrate testable architecture, 
automated testing, CI/CD integration, and practical use of AI in quality engineering.

> "Most teams ship AI fast. I make sure it ships right."

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python + FastAPI |
| Unit + Integration Tests | pytest |
| API + E2E Tests | Playwright |
| Frontend | HTML + CSS + Vanilla JavaScript |
| AI Component | Claude API (Anthropic) |
| CI/CD | GitHub Actions |
| Hosting | Render |

---

## How to Run Locally

```bash
# Clone the repo
git clone https://github.com/your-username/takeaway-saas.git
cd takeaway-saas

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Add your API key
# Create .env file and add:
# ANTHROPIC_API_KEY=sk-ant-...

# Start the server
python -m uvicorn app.main:app --reload

# Open frontend
# Visit http://localhost:8000/frontend/index.html
```

---

## API Endpoints

| Method | Endpoint | Description | Sample Request |
|---|---|---|---|
| GET | / | Health check | — |
| GET | /menu | Get all menu items | — |
| GET | /menu/{item_id} | Get single item | — |
| POST | /order | Place an order | `{"items": [{"item_id": 1, "quantity": 2}]}` |
| POST | /payment | Process payment | `{"order_id": "abc", "amount": 450, "simulate_failure": false}` |
| GET | /summary/{order_id} | Get AI order summary | — |
| POST | /analyze-coverage | AI test gap analysis | `{"test_results": "...pytest output..."}` |

---

## Test Strategy

Tests are structured in three layers, each serving a distinct purpose.

**Unit Tests — pytest**
Test individual functions in isolation without starting the server. Cover calculation logic, validation rules, edge cases, and error handling. Fast and deterministic.

**Integration Tests — pytest + TestClient**
Test multiple modules working together via HTTP calls using FastAPI's TestClient. Cover full request/response cycles, error responses, and cross-module flows like order creation followed by payment.

**E2E Tests — Playwright**
Simulate a real user in a real browser. Cover the complete flow from menu browsing to payment result. Two critical paths tested: happy path (successful payment) and failure path (simulated decline). Assertions check exact UI text, button visibility, and order ID display.

**CI/CD — GitHub Actions**
Every push to main triggers the full pipeline: pytest runs first, then Playwright tests run after backend tests pass. Test report uploaded as artifact on every run.

---

## How I Used AI

**AI inside the app:**
Claude API generates a personalised order confirmation summary after every successful payment. If the API is unavailable, a fallback message is returned — graceful degradation by design.

**AI for test coverage analysis:**
A `/analyze-coverage` endpoint accepts pytest output and sends it to Claude, which identifies untested scenarios and coverage gaps. This is a practical example of using AI to govern quality, not just ship features.

**AI for test case generation:**
Claude was used during development to generate initial test cases for all modules. The prompt used was:

> "You are a senior QA engineer. Given this Python function, generate comprehensive pytest test cases covering happy path, edge cases, boundary values, and error scenarios."

Claude identified these scenarios I had not initially considered:
- Quantity of zero in an order line item
- Item ID as a string instead of integer
- Payment amount as a negative number
- Empty string UPI ID passing basic empty check but failing format validation

Each AI-generated test case was critically reviewed and validated before inclusion. This reflects how I would govern AI-assisted testing in production — AI accelerates, human expertise validates.

---

## Risks and Gaps

- No real payment gateway — mock only, does not test actual network failures or bank responses
- No database — in-memory storage means all data lost on server restart
- No authentication or authorisation — any user can access any order
- No load or performance testing — system behaviour under concurrent users unknown
- Test coverage not formally measured — no coverage percentage reported in CI
- E2E tests depend on server running — not fully self-contained in CI without webServer config

---

## Improvements

- Add PostgreSQL with SQLAlchemy — enables data layer tests and migration testing
- Add real payment gateway (Razorpay) with contract tests using Pact
- Add authentication with JWT and write authorisation test scenarios
- Add performance tests with Locust to validate behaviour under load
- Add test coverage reporting (pytest-cov) to CI/CD pipeline
- Add negative UI testing — behaviour when JavaScript is disabled
- Add contract testing between frontend and backend API

---

## Scalability

**Current limitations:**
- Single FastAPI instance — no horizontal scaling
- In-memory data — no shared state across instances
- No caching layer
- No load balancer

**How I would scale this:**
- Move to PostgreSQL for persistent, shared storage
- Add Redis caching for menu data — menu rarely changes
- Containerise with Docker for consistent deployments
- Deploy behind Nginx as load balancer
- Use Kubernetes for auto-scaling based on order volume
- Add Locust performance tests to validate each scaling decision before production release