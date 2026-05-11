from tests.conftest import (
    create_valid_order_payload,
    create_empty_order_payload,
    create_invalid_order_payload,
    create_zero_amount_payment_payload,
)


def test_post_order_valid_items_returns_200(client):
    """POST /order with valid items must return 200 with a pending order and correct total."""
    payload = create_valid_order_payload(quantity=2)
    expected_total = 199 * 2
    print(f"\nPOST /order with {payload}")
    response = client.post("/order", json=payload)
    data = response.json()
    print(f"Status: {response.status_code}, total={data.get('total')}, status={data.get('status')}")

    assert response.status_code == 200, (
        f"Expected HTTP 200 for valid order, got {response.status_code}"
    )
    assert data["status"] == "pending", (
        f"Expected order status='pending', got '{data['status']}'"
    )
    assert data["total"] == expected_total, (
        f"Expected total={expected_total} for item_id=1 qty=2, got {data['total']}"
    )


def test_post_order_empty_items_returns_400(client):
    """POST /order with an empty items list must return 400 Bad Request."""
    print("\nPOST /order with empty items list")
    response = client.post("/order", json=create_empty_order_payload())
    print(f"Status: {response.status_code}, Body: {response.json()}")
    assert response.status_code == 400, (
        f"Expected HTTP 400 for empty items, got {response.status_code}"
    )


def test_post_order_invalid_item_id_returns_400(client):
    """POST /order with an item_id not in the menu must return 400 Bad Request."""
    payload = create_invalid_order_payload(item_id=9999)
    print(f"\nPOST /order with non-existent item_id=9999: {payload}")
    response = client.post("/order", json=payload)
    print(f"Status: {response.status_code}, Body: {response.json()}")
    assert response.status_code == 400, (
        f"Expected HTTP 400 for unknown item_id=9999, got {response.status_code}"
    )


def test_full_flow_order_then_successful_payment(client):
    """Full flow: placing an order then paying must return status='success' with correct fields."""
    order_payload = create_valid_order_payload(quantity=2)
    print(f"\nStep 1 — POST /order: {order_payload}")
    order_resp = client.post("/order", json=order_payload)
    assert order_resp.status_code == 200, (
        f"Expected HTTP 200 placing order, got {order_resp.status_code}"
    )
    order = order_resp.json()
    print(f"Order created: order_id={order['order_id']}, total={order['total']}")

    pay_payload = {"order_id": order["order_id"], "amount": order["total"]}
    print(f"Step 2 — POST /payment: {pay_payload}")
    pay_resp = client.post("/payment", json=pay_payload)
    result = pay_resp.json()
    print(f"Payment result: status={result.get('status')}, amount_paid={result.get('amount_paid')}")

    assert pay_resp.status_code == 200, (
        f"Expected HTTP 200 for payment, got {pay_resp.status_code}"
    )
    assert result["status"] == "success", (
        f"Expected payment status='success', got '{result['status']}'"
    )
    assert result["order_id"] == order["order_id"], (
        f"Expected order_id='{order['order_id']}' in payment response, got '{result.get('order_id')}'"
    )
    assert result["amount_paid"] == order["total"], (
        f"Expected amount_paid={order['total']}, got {result.get('amount_paid')}"
    )


def test_full_flow_order_then_simulated_payment_failure(client):
    """Full flow: placing an order then simulating failure must return status='failed' with a message."""
    order_payload = create_valid_order_payload(item_id=2)
    print(f"\nStep 1 — POST /order: {order_payload}")
    order_resp = client.post("/order", json=order_payload)
    assert order_resp.status_code == 200, (
        f"Expected HTTP 200 placing order, got {order_resp.status_code}"
    )
    order = order_resp.json()
    print(f"Order created: order_id={order['order_id']}, total={order['total']}")

    pay_payload = {"order_id": order["order_id"], "amount": order["total"], "simulate_failure": True}
    print(f"Step 2 — POST /payment with simulate_failure=True: {pay_payload}")
    pay_resp = client.post("/payment", json=pay_payload)
    result = pay_resp.json()
    print(f"Payment result: status={result.get('status')}, message={result.get('message')}")

    assert pay_resp.status_code == 200, (
        f"Expected HTTP 200 even on simulated failure, got {pay_resp.status_code}"
    )
    assert result["status"] == "failed", (
        f"Expected payment status='failed' with simulate_failure=True, got '{result['status']}'"
    )
    assert "message" in result, (
        f"Expected 'message' key in failed payment response, got keys: {list(result.keys())}"
    )


def test_payment_with_zero_amount_returns_failed_status(client):
    """POST /payment with amount=0 must return status='failed' — zero is not a valid payment."""
    payload = create_zero_amount_payment_payload(order_id="any-id")
    print(f"\nPOST /payment with amount=0: {payload}")
    pay_resp = client.post("/payment", json=payload)
    result = pay_resp.json()
    print(f"Payment result: status={result.get('status')}")
    assert pay_resp.status_code == 200, (
        f"Expected HTTP 200, got {pay_resp.status_code}"
    )
    assert result["status"] == "failed", (
        f"Expected status='failed' for amount=0, got '{result['status']}'"
    )
