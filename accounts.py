from models.account_state import AccountState

def create_account(account_id: str, initial_balance: float):
    if not account_id:
        raise ValueError("Account ID cannot be empty")

    if initial_balance < 0:
        raise ValueError("Initial balance cannot be negative")

    return {
        "account_id": account_id,
        "balance": initial_balance,
        "state": AccountState.ACTIVE.value
    }

def deposit(account: dict, amount: float):
    if amount <= 0:
        raise ValueError("Deposit amount must be positive")

    account["balance"] += amount
    return account


def withdraw(account: dict, amount: float):
    if amount <= 0:
        raise ValueError("Withdrawal amount must be positive")

    if amount > account["balance"]:
        raise ValueError("Insufficient funds")

    account["balance"] -= amount
    return account


