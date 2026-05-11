import pytest
from starlette.testclient import TestClient
from app.main import app

# Test Data Factories
# These factory functions create reusable, isolated test data.
# Each test gets fresh data — no shared state between tests.
# Pattern: create_<type>_<variant>_payload()


def create_valid_order_payload(item_id=1, quantity=1):
    """Factory: creates a minimal valid order payload."""
    return {"items": [{"item_id": item_id, "quantity": quantity}]}


def create_multi_item_order_payload():
    """Factory: creates a valid order with multiple different items."""
    return {"items": [
        {"item_id": 1, "quantity": 1},
        {"item_id": 2, "quantity": 2},
        {"item_id": 3, "quantity": 1},
    ]}


def create_invalid_order_payload(item_id=999):
    """Factory: creates an order with an invalid item_id."""
    return {"items": [{"item_id": item_id, "quantity": 1}]}


def create_empty_order_payload():
    """Factory: creates an order with empty items list."""
    return {"items": []}


def create_valid_payment_payload(order_id="test-order-001", amount=199, simulate_failure=False):
    """Factory: creates a valid payment payload."""
    return {
        "order_id": order_id,
        "amount": amount,
        "simulate_failure": simulate_failure,
    }


def create_failure_payment_payload(order_id="test-order-001", amount=199):
    """Factory: creates a payment payload with simulate_failure=True."""
    return {
        "order_id": order_id,
        "amount": amount,
        "simulate_failure": True,
    }


def create_zero_amount_payment_payload(order_id="test-order-001"):
    """Factory: creates a payment payload with zero amount."""
    return {
        "order_id": order_id,
        "amount": 0,
        "simulate_failure": False,
    }


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
