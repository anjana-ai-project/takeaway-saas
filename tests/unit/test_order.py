import pytest
from app.order import create_order


def test_valid_order_returns_correct_total(capfd):
    """A single item order must compute total as item price × quantity."""
    order = create_order([{"item_id": 1, "quantity": 1}])
    expected = 199
    print(f"\nTesting order total: expected {expected}, got {order['total']}")
    assert order["total"] == expected, (
        f"Expected total={expected} for item_id=1 qty=1, got {order['total']}"
    )


def test_quantity_multiplied_in_total(capfd):
    """Total must equal unit price multiplied by quantity for a single item."""
    order = create_order([{"item_id": 1, "quantity": 3}])
    expected = 199 * 3
    print(f"\nTesting quantity multiplication: expected {expected}, got {order['total']}")
    assert order["total"] == expected, (
        f"Expected total={expected} for item_id=1 qty=3, got {order['total']}"
    )


def test_multiple_items_summed_in_total(capfd):
    """Total must be the sum of each item's line total when multiple items are ordered."""
    order = create_order([{"item_id": 1, "quantity": 1}, {"item_id": 4, "quantity": 2}])
    expected = 199 + 89 * 2
    print(f"\nTesting multi-item total: expected {expected}, got {order['total']}")
    assert order["total"] == expected, (
        f"Expected total={expected} for items [id=1 qty=1, id=4 qty=2], got {order['total']}"
    )


def test_empty_items_raises_value_error(capfd):
    """create_order() must raise ValueError immediately when items list is empty."""
    print("\nTesting empty items list raises ValueError")
    with pytest.raises(ValueError, match="at least one item"):
        create_order([])


def test_invalid_item_id_raises_value_error(capfd):
    """create_order() must raise ValueError when an item_id is not in the menu."""
    print("\nTesting invalid item_id=9999 raises ValueError")
    with pytest.raises(ValueError, match="not found"):
        create_order([{"item_id": 9999, "quantity": 1}])


def test_order_has_required_fields(capfd):
    """A created order dict must contain order_id, items, total, and status."""
    order = create_order([{"item_id": 2, "quantity": 1}])
    required = {"order_id", "items", "total", "status"}
    missing = required - order.keys()
    print(f"\nChecking order fields: required={required}, missing={missing or 'none'}")
    assert not missing, (
        f"Order is missing required fields: {missing}. Got keys: {set(order.keys())}"
    )


def test_status_is_pending_on_creation(capfd):
    """A newly created order must have status='pending' before any payment."""
    order = create_order([{"item_id": 3, "quantity": 1}])
    print(f"\nTesting initial status: expected 'pending', got '{order['status']}'")
    assert order["status"] == "pending", (
        f"Expected status='pending' on new order, got '{order['status']}'"
    )
