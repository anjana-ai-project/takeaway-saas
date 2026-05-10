from app.payment import process_payment


def test_valid_payment_returns_success_status(capfd):
    """A payment with a positive amount and no failure flag must return status='success'."""
    result = process_payment("order-1", 450)
    print(f"\nTesting valid payment status: expected 'success', got '{result['status']}'")
    assert result["status"] == "success", (
        f"Expected status='success' for valid payment, got '{result['status']}'"
    )


def test_simulate_failure_returns_failed_status(capfd):
    """Passing simulate_failure=True must return status='failed' regardless of amount."""
    result = process_payment("order-1", 450, simulate_failure=True)
    print(f"\nTesting simulated failure status: expected 'failed', got '{result['status']}'")
    assert result["status"] == "failed", (
        f"Expected status='failed' with simulate_failure=True, got '{result['status']}'"
    )


def test_amount_zero_returns_failed_status(capfd):
    """A payment with amount=0 must be rejected and return status='failed'."""
    result = process_payment("order-1", 0)
    print(f"\nTesting zero amount status: expected 'failed', got '{result['status']}'")
    assert result["status"] == "failed", (
        f"Expected status='failed' for amount=0, got '{result['status']}'"
    )


def test_negative_amount_returns_failed_status(capfd):
    """A payment with a negative amount must be rejected and return status='failed'."""
    result = process_payment("order-1", -10)
    print(f"\nTesting negative amount status: expected 'failed', got '{result['status']}'")
    assert result["status"] == "failed", (
        f"Expected status='failed' for amount=-10, got '{result['status']}'"
    )


def test_success_response_contains_order_id_and_amount_paid(capfd):
    """A successful payment response must echo back the order_id and amount_paid."""
    result = process_payment("order-abc", 299)
    print(f"\nTesting success response fields: order_id={result.get('order_id')}, amount_paid={result.get('amount_paid')}")
    assert result["order_id"] == "order-abc", (
        f"Expected order_id='order-abc' in response, got '{result.get('order_id')}'"
    )
    assert result["amount_paid"] == 299, (
        f"Expected amount_paid=299, got {result.get('amount_paid')}"
    )


def test_failed_response_contains_message(capfd):
    """A failed payment response must include a non-empty message field."""
    result = process_payment("order-1", 450, simulate_failure=True)
    print(f"\nTesting failure message: got '{result.get('message')}'")
    assert "message" in result, (
        f"Expected 'message' key in failed payment response, got keys: {list(result.keys())}"
    )
    assert result["message"], (
        f"Expected non-empty message in failed payment response, got '{result['message']}'"
    )
