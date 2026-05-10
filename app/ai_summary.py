import os
import anthropic
from dotenv import load_dotenv

load_dotenv()


def analyze_test_coverage(pytest_output: str) -> str:
    """Uses Claude to analyze pytest output and suggest coverage gaps. Falls back gracefully."""
    prompt = (
        "You are a QA engineer reviewing pytest output for a food takeaway SaaS application. "
        "Analyze the following test output and identify specific gaps in test coverage. "
        "Be concrete and actionable — name the exact scenarios, edge cases, or code paths that are untested. "
        "Return a numbered list of at least 3 specific coverage gaps.\n\n"
        f"Pytest output:\n{pytest_output}"
    )

    last_error = None
    for attempt in range(2):
        try:
            client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text
        except Exception as e:
            last_error = e
            print(f"Coverage analyzer error (attempt {attempt + 1}): {e}")

    return (
        "[FALLBACK] Coverage analysis service is temporarily unavailable. "
        "Manual gaps to check: empty order handling, payment failures, invalid menu items."
    )


def generate_order_summary(order: dict) -> str:
    """Calls Claude to produce a friendly order confirmation. Falls back to a plain message on any error."""
    items_desc = ", ".join(
        f"{i['name']} x{i['quantity']}" for i in order.get("items", [])
    )
    total = order.get("total", 0)
    order_id = order.get("order_id", "")

    prompt = (
        f"A customer just placed a takeaway order (ID: {order_id}). "
        f"Items ordered: {items_desc}. Total: ₹{total}. "
        "Write a friendly 2-3 sentence order confirmation summary mentioning the item names, "
        "the total amount in INR, and end with a warm closing."
    )

    try:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text
    except Exception as e:
        print(f"AI Summary error: {e}")
        print(f"Order details sent: order_id={order_id}, total={total}, items={items_desc}")
        return f"Your order has been confirmed. Total: ₹{total}. Thank you for ordering!"
