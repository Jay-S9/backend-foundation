from accounts import create_account, deposit, withdraw


def create_account_service(account_id: str, initial_balance: float):
    return create_account(account_id, initial_balance)


def deposit_service(account: dict, amount: float):
    return deposit(account, amount)


def withdraw_service(account: dict, amount: float):
    return withdraw(account, amount)
