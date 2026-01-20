from database import get_connection


def insert_account(account: dict):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO accounts (account_id, balance, state) VALUES (?, ?, ?)",
        (account["account_id"], account["balance"], account["state"])
    )

    conn.commit()
    conn.close()


def get_account(account_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT account_id, balance, state FROM accounts WHERE account_id = ?",
        (account_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "account_id": row[0],
        "balance": row[1],
        "state": row[2]
    }


def update_balance(account_id: str, balance: float):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE accounts SET balance = ? WHERE account_id = ?",
        (balance, account_id)
    )

    conn.commit()
    conn.close()


def insert_transaction_log(account_id, action, amount, balance_after):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO transaction_logs (account_id, action, amount, balance_after)
        VALUES (?, ?, ?, ?)
        """,
        (account_id, action, amount, balance_after)
    )

    conn.commit()
    conn.close()


def idempotency_exists(key: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT key FROM idempotency_keys WHERE key = ?",
        (key,)
    )

    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def store_idempotency_key(key: str, account_id: str, action: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO idempotency_keys (key, account_id, action)
        VALUES (?, ?, ?)
        """,
        (key, account_id, action)
    )

    conn.commit()
    conn.close()

def update_state(account_id: str, state: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE accounts SET state = ? WHERE account_id = ?",
        (state, account_id)
    )

    conn.commit()
    conn.close()

def apply_deposit_transaction(
    conn,
    account_id: str,
    amount: float,
    new_balance: float,
    idempotency_key: str
):
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE accounts SET balance = ? WHERE account_id = ?",
        (new_balance, account_id)
    )

    cursor.execute(
        """
        INSERT INTO transaction_logs (account_id, action, amount, balance_after)
        VALUES (?, 'DEPOSIT', ?, ?)
        """,
        (account_id, amount, new_balance)
    )

    cursor.execute(
        """
        INSERT INTO idempotency_keys (key, account_id, action)
        VALUES (?, ?, 'DEPOSIT')
        """,
        (idempotency_key, account_id)
    )
