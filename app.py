from fastapi import FastAPI, HTTPException
from accounts import create_account, deposit, withdraw
from database import get_connection, init_db

app = FastAPI()


@app.on_event("startup")
def startup():
    init_db()


@app.post("/accounts")
def create_new_account(account_id: str, initial_balance: float):
    try:
        account = create_account(account_id, initial_balance)

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO accounts (account_id, balance, status) VALUES (?, ?, ?)",
            (account["account_id"], account["balance"], account["status"])
        )

        conn.commit()
        conn.close()

        return account

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=400, detail="Account already exists")


@app.post("/accounts/{account_id}/deposit")
def deposit_money(account_id: str, amount: float, idempotency_key: str):
    conn = get_connection()
    cursor = conn.cursor()

    # 🔐 STEP 1: IDEMPOTENCY CHECK
    cursor.execute(
        "SELECT key FROM idempotency_keys WHERE key = ?",
        (idempotency_key,)
    )

    if cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=409,
            detail="Duplicate request detected"
        )

    cursor.execute(
        "SELECT account_id, balance, status FROM accounts WHERE account_id = ?",
        (account_id,)
    )
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Account not found")

    account = {
        "account_id": row[0],
        "balance": row[1],
        "status": row[2]
    }

    try:
        account = deposit(account, amount)

        # update balance
        cursor.execute(
            "UPDATE accounts SET balance = ? WHERE account_id = ?",
            (account["balance"], account_id)
        )

        # 🧾 LOG SUCCESSFUL DEPOSIT
        cursor.execute(
            """
            INSERT INTO transaction_logs (account_id, action, amount, balance_after)
            VALUES (?, ?, ?, ?)
            """,
            (account_id, "DEPOSIT", amount, account["balance"])
        )

        # 🔐 STEP 2: STORE IDEMPOTENCY KEY
        cursor.execute(
            """
            INSERT INTO idempotency_keys (key, account_id, action)
            VALUES (?, ?, ?)
            """,
            (idempotency_key, account_id, "DEPOSIT")
        )

        conn.commit()
        conn.close()

        return account

    except ValueError as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/accounts/{account_id}/withdraw")
def withdraw_money(account_id: str, amount: float):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT account_id, balance, status FROM accounts WHERE account_id = ?",
        (account_id,)
    )
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Account not found")

    account = {
        "account_id": row[0],
        "balance": row[1],
        "status": row[2]
    }

    try:
        account = withdraw(account, amount)

        cursor.execute(
            "UPDATE accounts SET balance = ? WHERE account_id = ?",
            (account["balance"], account_id)
        )

        cursor.execute(
            """
            INSERT INTO transaction_logs (account_id, action, amount, balance_after)
            VALUES (?, ?, ?, ?)
            """,
            (account_id, "WITHDRAW", amount, account["balance"])
        )

        conn.commit()
        conn.close()

        return account

    except ValueError as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/accounts/{account_id}/logs")
def get_transaction_logs(account_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT action, amount, balance_after, timestamp
        FROM transaction_logs
        WHERE account_id = ?
        ORDER BY timestamp
        """,
        (account_id,)
    )

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="No logs found for this account")

    return [
        {
            "action": row[0],
            "amount": row[1],
            "balance_after": row[2],
            "timestamp": row[3]
        }
        for row in rows
    ]
