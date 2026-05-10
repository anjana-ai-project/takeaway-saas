import uuid
from app.menu import get_item_by_id

_orders = []


# Creates a new order from a list of {item_id, quantity} dicts.
# Raises ValueError if items is empty or any item_id does not exist in the menu.
# Returns the saved order dict with a generated order_id, resolved items, total, and status="pending".
def create_order(items: list) -> dict:
    if not items:
        raise ValueError("Order must contain at least one item")

    resolved_items = []
    total = 0

    for entry in items:
        item_id = entry.get("item_id")
        quantity = entry.get("quantity", 1)

        menu_item = get_item_by_id(item_id)
        if menu_item is None:
            raise ValueError(f"Menu item with id {item_id} not found")

        line_total = menu_item["price"] * quantity
        total += line_total
        resolved_items.append({
            "item_id": item_id,
            "name": menu_item["name"],
            "price": menu_item["price"],
            "quantity": quantity,
            "line_total": line_total,
        })

    order = {
        "order_id": str(uuid.uuid4()),
        "items": resolved_items,
        "total": total,
        "status": "pending",
    }
    _orders.append(order)
    return order


# Returns the order matching order_id, or None if not found.
def get_order(order_id: str) -> dict | None:
    return next((o for o in _orders if o["order_id"] == order_id), None)
