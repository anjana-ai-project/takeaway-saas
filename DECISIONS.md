# Architectural & Testing Decisions

## 1. FastAPI over Django or Flask
- **Decision:** Used FastAPI as the backend framework
- **Why:** FastAPI is lightweight, modern, and has built-in request validation and auto-generated API docs at /docs. Ideal for a focused SaaS demo.
- **Trade-off:** Less opinionated than Django — requires manual structure discipline.

## 2. In-memory storage over a database
- **Decision:** Orders and payments stored in Python lists/dicts, not a database
- **Why:** Keeps implementation simple and focused on test quality, which is the primary evaluation criteria. No migration scripts or DB setup needed.
- **Trade-off:** Data is lost when server restarts. Not suitable for production.

## 3. Playwright for both API and E2E testing
- **Decision:** Used Playwright for both API-level tests and full browser E2E tests
- **Why:** One tool for two test layers reduces complexity. Playwright supports HTTP requests directly without a browser, making it ideal for API testing alongside UI testing.
- **Trade-off:** Jest or Supertest would be more conventional for pure API testing in a Node environment.

## 4. Business logic separated from routes
- **Decision:** All business logic lives in module files (menu.py, order.py, payment.py). FastAPI routes only call functions and return responses.
- **Why:** Enables unit testing of pure functions without spinning up the server. This is a deliberate testability design decision.
- **Trade-off:** Slightly more files to maintain.

## 5. Payment failure triggered by checkbox
- **Decision:** Added a "Simulate payment failure" checkbox instead of random failure logic
- **Why:** Makes both success and failure paths fully controllable and deterministic in automated tests. Random failure would make tests flaky.
- **Trade-off:** Less realistic than actual gateway integration, but appropriate for a mock system.

## 6. AI summary fallback when API fails
- **Decision:** If Claude API call fails, return a hardcoded fallback message instead of an error
- **Why:** Keeps the user experience intact even when the AI component is unavailable. Graceful degradation is a production-readiness principle.
- **Trade-off:** User may not know the summary is a fallback, not AI-generated.

## 7. Mock Claude API in unit tests
- **Decision:** Claude API calls are mocked in all unit tests
- **Why:** Real API calls in tests are slow, cost money, and introduce external dependencies that can cause flaky tests. Tests should be deterministic and fast.
- **Trade-off:** Mocks may not catch real API contract changes — mitigated by integration tests.

## 8. Python + FastAPI over Node.js + TypeScript + Express
- **Decision:** Used Python + FastAPI instead of the suggested Node.js stack
- **Why:** Python aligns with AI/ML engineering teams where this role operates. FastAPI has excellent async support, built-in request validation via Pydantic, and auto-generated API docs. pytest is mature and widely used for API testing.
- **Trade-off:** Node.js + TypeScript is more common in traditional SaaS backends. However, the testing principles — unit, integration, E2E, CI/CD — are identical regardless of language.