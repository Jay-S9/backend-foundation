from fastapi import FastAPI, HTTPException, Header
from typing import Optional
from fastapi.security import APIKeyHeader
from fastapi import Security

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


# -------------------------
# API Key Authentication
# -------------------------
API_KEY_ROLES = {
    "internal-service-key-123": "service",
    "admin-key-456": "admin"
}

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

def authenticate(api_key: str):
    role = API_KEY_ROLES.get(api_key)
    if not role:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return role

def authorize(role: str, action: str):
    permissions = {
        "service": {"deposit"},
        "admin": {"deposit", "withdraw"}
    }

    allowed_actions = permissions.get(role, set())

    if action not in allowed_actions:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: insufficient permissions"
        )

@app.on_event("startup")
def startup():
    init_db()


# -------------------------
# Account Creation
# -------------------------
@app.post("/accounts")
def create_new_account(
    payload: CreateAccountRequest,
    api_key: str = Security(api_key_header)
):
    authenticate(api_key)

    account = create_account_service(
        payload.account_id,
        payload.initial_balance
    )
    insert_account(account)
    return account

        

# -------------------------
# Deposit (Idempotent)
# -------------------------
@app.post("/accounts/{account_id}/deposit")
def deposit_money(
    account_id: str,
    payload: DepositRequest,
    api_key: str = Security(api_key_header)
):
    role = authenticate(api_key)
    authorize(role, "deposit")

    if idempotency_exists(payload.idempotency_key):
        raise HTTPException(status_code=409, detail="Duplicate request detected")

    account = get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    account = deposit_service(account, payload.amount)
    update_balance(account_id, account["balance"])
    insert_transaction_log(
        account_id,
        "DEPOSIT",
        payload.amount,
        account["balance"]
    )
    store_idempotency_key(payload.idempotency_key, account_id, "DEPOSIT")

    return account

# -------------------------
# Withdraw
# -------------------------
@app.post("/accounts/{account_id}/withdraw")
def withdraw_money(
    account_id: str,
    payload: WithdrawRequest,
    api_key: str = Security(api_key_header)
):
    role = authenticate(api_key)
    authorize(role, "withdraw")

    account = get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    account = withdraw_service(account, payload.amount)
    update_balance(account_id, account["balance"])
    insert_transaction_log(
        account_id,
        "WITHDRAW",
        payload.amount,
        account["balance"]
    )

    return account
