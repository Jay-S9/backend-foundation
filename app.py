from fastapi import FastAPI
from models.account_state import AccountState
from fastapi.security import APIKeyHeader
from services.account_state_service import transition_account_state
from repositories.account_repo import update_state
from database import get_transaction_connection
from repositories.account_repo import apply_deposit_transaction
from fastapi import Security
from models.errors import (
    unauthorized,
    forbidden,
    not_found,
    conflict,
    bad_request
)

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
        unauthorized()
    return role

def authorize(role: str, action: str):
    permissions = {
        "service": {"deposit"},
        "admin": {"deposit", "withdraw"}
    }

    if action not in permissions.get(role, set()):
        forbidden(action)

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

    try:
        account = create_account_service(
            payload.account_id,
            payload.initial_balance
        )
    except ValueError as e:
        bad_request(str(e))

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
        conflict("Duplicate request detected")

    account = get_account(account_id)
    if not account:
        not_found("Account")

    conn = get_transaction_connection()

    try:
        updated_account = deposit_service(account, payload.amount)

        apply_deposit_transaction(
            conn,
            account_id,
            payload.amount,
            updated_account["balance"],
            payload.idempotency_key
        )

        conn.commit()
        return updated_account

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

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
        not_found("Account")

    try:
        account = withdraw_service(account, payload.amount)
    except ValueError as e:
        bad_request(str(e))

    update_balance(account_id, account["balance"])
    insert_transaction_log(
        account_id,
        "WITHDRAW",
        payload.amount,
        account["balance"]
    )

    return account

@app.post("/accounts/{account_id}/freeze")
def freeze_account(
    account_id: str,
    api_key: str = Security(api_key_header)
):
    role = authenticate(api_key)
    authorize(role, "withdraw")  # admin-only

    account = get_account(account_id)
    if not account:
        not_found("Account")

    try:
        account = transition_account_state(
            account,
            AccountState.FROZEN.value
        )
    except ValueError as e:
        bad_request(str(e))

    update_state(account_id, account["state"])
    return account

@app.post("/accounts/{account_id}/unfreeze")
def unfreeze_account(
    account_id: str,
    api_key: str = Security(api_key_header)
):
    role = authenticate(api_key)
    authorize(role, "withdraw")  # admin-only

    account = get_account(account_id)
    if not account:
        not_found("Account")

    try:
        account = transition_account_state(
            account,
            AccountState.ACTIVE.value
        )
    except ValueError as e:
        bad_request(str(e))

    update_state(account_id, account["state"])
    return account
