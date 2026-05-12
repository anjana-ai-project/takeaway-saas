# Leadership Brief — Takeaway SaaS System

**Prepared for:** Product and Engineering Leadership  
**System:** Takeaway SaaS — Menu, Ordering, and Payment  
**Deployed at:** https://takeaway-saas.onrender.com/frontend/index.html  
**Status:** Assessment submission — not production ready  

---

## What This System Does

A working takeaway ordering system where customers browse a menu, 
add items to a cart, choose a payment method, and receive an 
AI-generated order confirmation. Payment is simulated — no real 
money moves.

---

## What We Are Confident In

These behaviours are enforced in code and verified by automated tests:

**Order integrity:**
- Item prices are always calculated server side from the menu. 
  A client cannot send a manipulated price and have it accepted.
- Order totals are always calculated server side. 
  The client has no influence over what is charged.
- Order IDs are always generated server side as UUIDs. 
  A client cannot specify or predict an order ID.

**Input validation:**
- Negative, zero, decimal, and string quantities are rejected 
  at the API level before any business logic runs. 
  The system returns 422 Unprocessable Entity.
- Invalid menu item IDs are rejected with 400 Bad Request.
- Orders with empty item lists are rejected with 400 Bad Request.
- Payments with missing or empty order IDs are rejected.
- Payments with zero or negative amounts return a failed status.

**Payment protection:**
- The same order cannot be paid twice. A duplicate payment 
  attempt returns a failed status with "Payment already processed 
  for this order." Note: this protection is in-memory only — 
  a server restart clears it. See risks below.

**AI component:**
- The AI order summary has a tested fallback. If the Claude API 
  is unavailable, the system returns a hardcoded confirmation 
  message containing the correct order total. The user experience 
  does not break.
- AI output is formally evaluated for correctness, hallucination, 
  faithfulness, relevance, toxicity, and latency using DeepEval 
  with an independent judge model.

---

## What We Are Not Confident In

These are gaps in the current system. They are documented here 
because shipping without acknowledging them would be worse than 
not shipping at all.

**No authentication:**
Any caller can read the menu, place orders, and process payments 
without identifying themselves. There is no concept of a user, 
session, or tenant. This is the highest risk item for a multi-tenant 
SaaS system.

**No rate limiting:**
The API endpoints are open to unlimited calls. A malicious caller 
could flood the system with requests. No throttling is enforced 
at the application level.

**Payment idempotency is not persistent:**
Duplicate payment prevention works correctly while the server is 
running. A server restart clears the in-memory tracking set. 
In production this would require a persistent store such as Redis 
or a database.

**Payment method details not validated server side:**
UPI ID format and card number validity are only checked in the 
browser. A caller bypassing the UI can send any value to the 
payment endpoint — the mock payment will succeed regardless of 
what payment details were entered.

**No stock or availability:**
There is no concept of an item being sold out or unavailable. 
Any item ID in the menu can be ordered in any quantity at any time.

**Simulate failure flag is exposed in the production API:**
The POST /payment endpoint accepts a simulate_failure boolean 
that anyone can send. This is an intentional test mechanism that 
should be restricted to test environments in production.

**No observability:**
There is no structured logging, metrics, or tracing. If the system 
fails in production, diagnosing the cause would require reading 
raw server logs with no tooling support.

**No data persistence:**
All orders and payments are stored in memory. A server restart 
loses all data. This is intentional for this assessment — production 
would require a database.

---

## Test Coverage Summary

| Layer | Tool | Count | Status |
|---|---|---|---|
| Unit tests | pytest | 34 | All passing |
| Integration tests | pytest | 10+ | All passing |
| API tests | Playwright | 20 | All passing |
| UI E2E tests | Playwright | 34 | All passing |
| AI eval tests | DeepEval + GPT-4o-mini | 25 | 19 passed, 5 skipped (OpenAI quota) |

CI/CD pipeline runs unit, integration, and Playwright tests automatically 
on every push to main. AI eval tests run manually — results committed 
to the reports/ folder.

---

## What Would Need to Change Before Production

In priority order:

1. Authentication and authorisation — JWT or OAuth2
2. Persistent storage — PostgreSQL replacing in-memory
3. Persistent idempotency keys — Redis for payment deduplication
4. Rate limiting — API gateway or middleware
5. Real payment gateway — Razorpay or Stripe with webhook validation
6. Remove simulate_failure from production API
7. Structured logging and monitoring — Datadog or CloudWatch
8. Contract testing — Pact for frontend-backend API contracts
9. Load testing — Locust to validate concurrent order handling
10. Stock management — availability checking before order confirmation

---

## One Sentence Summary

This system demonstrates production-quality test architecture and 
honest risk awareness — it is not production-ready, and this document 
exists precisely to make that clear before anyone assumes otherwise.