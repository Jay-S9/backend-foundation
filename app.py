from fastapi import FastAPI, HTTPException
from services.account_service import (
    create_account_service,
    deposit_service,
    withdraw_service
)
from repositories.account_repo import (
    insert_account,
    get_account,
    update_balance,
    insert_transaction_log,
    idempotency_exists,
    store_idempotency_key
)
from database import init_db

app = FastAPI()


@app.on_event("startup")
def startup():
    init_db()


@app.post("/accounts")
def create_new_account(account_id: str, initial_balance: float):
    try:
        account = create_account_service(account_id, initial_balance)
        insert_account(account)
        return account
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/accounts/{account_id}/deposit")
def deposit_money(account_id: str, amount: float, idempotency_key: str):
    if idempotency_exists(idempotency_key):
        raise HTTPException(status_code=409, detail="Duplicate request detected")

    account = get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    try:
        account = deposit_service(account, amount)
        update_balance(account_id, account["balance"])
        insert_transaction_log(account_id, "DEPOSIT", amount, account["balance"])
        store_idempotency_key(idempotency_key, account_id, "DEPOSIT")
        return account
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/accounts/{account_id}/withdraw")
def withdraw_money(account_id: str, amount: float):
    account = get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    try:
        account = withdraw_service(account, amount)
        update_balance(account_id, account["balance"])
        insert_transaction_log(account_id, "WITHDRAW", amount, account["balance"])
        return account
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

