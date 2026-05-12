# Input Boundary Analysis

Every input point in the system, what is validated, what is trusted, 
and what is an accepted risk.

---

## UI → API Boundary

| Input | Validated At | How | Trusted? | Risk if Bypassed |
|---|---|---|---|---|
| Menu item selection | Client + Server | Server looks up item_id in menu — price always taken from server | Server validates item_id exists | Client cannot manipulate price |
| Quantity | Server (Pydantic) | Must be integer >= 1 — rejects negative, zero, decimal, string | Not trusted from client | Accepted — enforced at schema level |
| Payment method selection | Client only | UPI/Card/COD selection | Trusted | Low — payment is mock only |
| UPI ID format | Client only | @ symbol check in JavaScript | Not validated server side | Accepted risk — UPI ID not used in backend |
| Card number/expiry/CVV | Client only | Format check in JavaScript | Not validated server side | Accepted risk — payment is mock only |
| Simulate failure flag | Server | Boolean accepted as-is | Trusted | Intentional — test mechanism |

---

## API → Payment Boundary

| Input | Validated At | How | Trusted? | Risk if Bypassed |
|---|---|---|---|---|
| order_id | Server | Checked for empty/None — rejects blank | Not trusted | Returns failed if missing |
| amount | Server | Must be > 0 — rejects zero and negative | Not trusted | Returns failed if invalid |
| simulate_failure | Server | Boolean — accepted as-is | Trusted | Intentional test mechanism |
| Duplicate payment | Server | order_id tracked in memory set | Not trusted | Returns failed if already processed |

---

## API → Data Store Boundary

| Input | Validated At | How | Trusted? | Risk if Bypassed |
|---|---|---|---|---|
| item_id in order | Server | Checked against menu list | Not trusted | Returns 400 if not found |
| quantity | Server (Pydantic + business logic) | Integer >= 1 enforced at two layers | Not trusted | Rejected at schema level before business logic |
| Order total | Server only | Calculated from menu prices — never accepted from client | N/A | Client cannot manipulate total |
| order_id generation | Server only | UUID4 generated server side | N/A | Client cannot specify order ID |

---

## Explicitly Accepted Risks

These are known gaps that are acceptable for this assessment scope 
but would require mitigation in production:

| Risk | Why Accepted | Production Fix |
|---|---|---|
| No authentication | Out of scope — any caller can read menu and place orders | JWT authentication with role-based access |
| UPI/Card details not validated server side | Payment is mock — no real gateway | Real gateway validates payment details |
| No rate limiting | Out of scope | API gateway rate limiting per IP/key |
| Duplicate payment prevention is in-memory | Server restart clears the set | Persistent store (Redis/DB) for idempotency keys |
| No HTTPS enforcement | Render provides HTTPS — not enforced in code | Force HTTPS redirect in production |
| simulate_failure flag exposed in API | Intentional test mechanism | Remove or restrict to test environments only |
| No input sanitisation for XSS | No user-generated content stored or rendered server side | Add sanitisation if user content is persisted |
| order_id in payment not verified against existing orders | Payment accepts any order_id string | Verify order_id exists before processing payment |

---

## What the Server Always Calculates — Never Trusts from Client

- Item prices — always looked up from menu by item_id
- Order total — always calculated server side
- Order ID — always generated server side as UUID4
- Order status — always set server side

These values cannot be manipulated by a client regardless of what is sent.