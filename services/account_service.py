from models.account_state import AccountState
from accounts import create_account


def create_account_service(account_id: str, initial_balance: float):
    return create_account(account_id, initial_balance)


def deposit_service(account: dict, amount: float):
    # 🔒 STATE ENFORCEMENT
    if account["state"] != AccountState.ACTIVE.value:
        raise ValueError("Account is not active")

    if amount <= 0:
        raise ValueError("Deposit amount must be positive")

    account["balance"] += amount
    return account


def withdraw_service(account: dict, amount: float):
    # 🔒 STATE ENFORCEMENT
    if account["state"] != AccountState.ACTIVE.value:
        raise ValueError("Account is not active")

    if amount <= 0:
        raise ValueError("Withdrawal amount must be positive")

    if account["balance"] < amount:
        raise ValueError("Insufficient funds")

    account["balance"] -= amount
    return account
