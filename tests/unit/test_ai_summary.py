from unittest.mock import MagicMock, patch
from starlette.testclient import TestClient
from app.main import app
from app.ai_summary import generate_order_summary

SAMPLE_ORDER = {
    "order_id": "test-order-123",
    "items": [
        {"name": "Classic Beef Burger", "quantity": 1, "price": 199, "line_total": 199},
        {"name": "Mango Shake", "quantity": 2, "price": 99, "line_total": 198},
    ],
    "total": 397,
    "status": "pending",
}


def _mock_client(summary_text: str):
    """Build a mock anthropic.Anthropic client that returns summary_text."""
    content_block = MagicMock()
    content_block.text = summary_text
    message = MagicMock()
    message.content = [content_block]
    client = MagicMock()
    client.messages.create.return_value = message
    return client


def test_summary_returned_when_api_succeeds(capfd):
    """generate_order_summary() must return the exact text from the Claude API response."""
    expected = "Your order is on its way! Enjoy your Classic Beef Burger."
    print(f"\nTesting API success path: expecting Claude response to pass through unchanged")
    with patch("app.ai_summary.anthropic.Anthropic", return_value=_mock_client(expected)):
        result = generate_order_summary(SAMPLE_ORDER)
    print(f"Expected: '{expected}'\nGot:      '{result}'")
    assert result == expected, (
        f"Expected summary to equal Claude's response.\nExpected: '{expected}'\nGot: '{result}'"
    )


def test_fallback_returned_when_api_fails(capfd):
    """generate_order_summary() must return the fallback string when the API raises any exception."""
    print("\nTesting API failure fallback — patching Anthropic constructor to raise")
    with patch("app.ai_summary.anthropic.Anthropic", side_effect=Exception("network error")):
        result = generate_order_summary(SAMPLE_ORDER)
    print(f"Fallback result: '{result}'")
    assert "confirmed" in result.lower(), (
        f"Expected fallback to contain 'confirmed', got: '{result}'"
    )
    assert "₹" in result, (
        f"Expected fallback to contain the rupee symbol ₹, got: '{result}'"
    )


def test_fallback_contains_correct_total(capfd):
    """Fallback message must include the order total so the customer knows what they owe."""
    print(f"\nTesting fallback includes total: order total is {SAMPLE_ORDER['total']}")
    with patch("app.ai_summary.anthropic.Anthropic", side_effect=Exception("api down")):
        result = generate_order_summary(SAMPLE_ORDER)
    print(f"Fallback result: '{result}'")
    assert str(SAMPLE_ORDER["total"]) in result, (
        f"Expected fallback to contain total='{SAMPLE_ORDER['total']}', got: '{result}'"
    )


def test_summary_endpoint_returns_404_for_invalid_order_id(capfd):
    """GET /summary/{{order_id}} must return 404 when the order_id does not exist."""
    invalid_id = "nonexistent-order-id"
    print(f"\nTesting GET /summary/{invalid_id}: expecting 404")
    client = TestClient(app)
    response = client.get(f"/summary/{invalid_id}")
    print(f"Status: {response.status_code}, Body: {response.json()}")
    assert response.status_code == 404, (
        f"Expected HTTP 404 for unknown order_id='{invalid_id}', got {response.status_code}"
    )
    assert "not found" in response.json()["detail"].lower(), (
        f"Expected 'not found' in error detail, got: '{response.json()['detail']}'"
    )


def test_summary_endpoint_returns_summary_for_valid_order(capfd):
    """GET /summary/{{order_id}} must return the AI-generated summary for a known order."""
    from app.order import create_order
    order = create_order([{"item_id": 1, "quantity": 1}])
    order_id = order["order_id"]
    expected_summary = "Great choice! Your burger is being prepared."
    print(f"\nTesting GET /summary/{order_id}: expecting mocked summary")

    with patch("app.ai_summary.anthropic.Anthropic", return_value=_mock_client(expected_summary)):
        client = TestClient(app)
        response = client.get(f"/summary/{order_id}")

    print(f"Status: {response.status_code}, Summary: '{response.json().get('summary')}'")
    assert response.status_code == 200, (
        f"Expected HTTP 200 for valid order_id='{order_id}', got {response.status_code}"
    )
    assert response.json()["summary"] == expected_summary, (
        f"Expected summary='{expected_summary}', got '{response.json().get('summary')}'"
    )
