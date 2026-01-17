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

from models.requests import (
    CreateAccountRequest,
    DepositRequest,
    WithdrawRequest
)

from database import init_db

app = FastAPI()


@app.on_event("startup")
def startup():
    init_db()


# -------------------------
# Account Creation
# -------------------------
@app.post("/accounts")
def create_new_account(payload: CreateAccountRequest):
    try:
        account = create_account_service(
            payload.account_id,
            payload.initial_balance
        )
        insert_account(account)
        return account
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# -------------------------
# Deposit (Idempotent)
# -------------------------
@app.post("/accounts/{account_id}/deposit")
def deposit_money(account_id: str, payload: DepositRequest):
    if idempotency_exists(payload.idempotency_key):
        raise HTTPException(
            status_code=409,
            detail="Duplicate request detected"
        )

    account = get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    try:
        account = deposit_service(account, payload.amount)
        update_balance(account_id, account["balance"])
        insert_transaction_log(
            account_id,
            "DEPOSIT",
            payload.amount,
            account["balance"]
        )
        store_idempotency_key(
            payload.idempotency_key,
            account_id,
            "DEPOSIT"
        )
        return account
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# -------------------------
# Withdraw
# -------------------------
@app.post("/accounts/{account_id}/withdraw")
def withdraw_money(account_id: str, payload: WithdrawRequest):
    account = get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    try:
        account = withdraw_service(account, payload.amount)
        update_balance(account_id, account["balance"])
        insert_transaction_log(
            account_id,
            "WITHDRAW",
            payload.amount,
            account["balance"]
        )
        return account
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
