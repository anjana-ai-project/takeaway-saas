# Processes a payment for an order. Returns a success or failure dict.
# Pass simulate_failure=True to test decline behaviour without a real payment gateway.
def process_payment(order_id: str, amount: float, simulate_failure: bool = False) -> dict:
    if simulate_failure:
        return {"status": "failed", "message": "Payment declined. Please try again."}
    if amount <= 0:
        return {"status": "failed", "message": "Invalid amount"}
    return {
        "status": "success",
        "message": "Payment successful!",
        "order_id": order_id,
        "amount_paid": amount,
    }
