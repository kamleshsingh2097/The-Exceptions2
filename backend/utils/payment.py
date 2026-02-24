def simulate_payment(card_number: str, amount: float) -> tuple[bool, str]:
    """
    Simulate card payment for demo flows.
    Returns (is_successful, message).
    """
    if amount <= 0:
        return False, "failed: invalid amount"

    normalized = (card_number or "").replace(" ", "").replace("-", "")
    if not normalized.isdigit() or not (13 <= len(normalized) <= 19):
        return False, "failed: invalid card number"

    # Deterministic failure path for testing rejected payments.
    if normalized.endswith("0000"):
        return False, "failed: card declined"

    return True, "successful"
