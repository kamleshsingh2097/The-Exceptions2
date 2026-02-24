import time


def simulate_payment(card_number: str, amount: float):
    time.sleep(2)
    if card_number.endswith("000"):
        return False, "Declined"
    return True, "Success"
