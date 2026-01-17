from fastapi import FastAPI, HTTPException
from accounts import create_account, deposit, withdraw

app = FastAPI()

accounts_db = {}

@app.post("/accounts")
def create_new_account(account_id: str, initial_balance: float):
    try:
        account = create_account(account_id, initial_balance)
        accounts_db[account_id] = account
        return account
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/accounts/{account_id}/deposit")
def deposit_money(account_id: str, amount: float):
    if account_id not in accounts_db:
        raise HTTPException(status_code=404, detail="Account not found")

    try:
        account = deposit(accounts_db[account_id], amount)
        return account
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/accounts/{account_id}/withdraw")
def withdraw_money(account_id: str, amount: float):
    if account_id not in accounts_db:
        raise HTTPException(status_code=404, detail="Account not found")

    try:
        account = withdraw(accounts_db[account_id], amount)
        return account
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
