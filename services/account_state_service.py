from models.account_state import AccountState


ALLOWED_TRANSITIONS = {
    AccountState.ACTIVE.value: {
        AccountState.FROZEN.value,
        AccountState.CLOSED.value
    },
    AccountState.FROZEN.value: {
        AccountState.ACTIVE.value,
        AccountState.CLOSED.value
    },
    AccountState.CLOSED.value: set()
}


def transition_account_state(account: dict, new_state: str):
    current_state = account["state"]

    if new_state not in ALLOWED_TRANSITIONS[current_state]:
        raise ValueError(
            f"Invalid state transition from {current_state} to {new_state}"
        )

    account["state"] = new_state
    return account
