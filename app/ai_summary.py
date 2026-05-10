import os
import anthropic
from dotenv import load_dotenv

load_dotenv()


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
