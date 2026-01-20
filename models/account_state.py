from enum import Enum

class AccountState(str, Enum):
    ACTIVE = "active"
    FROZEN = "frozen"
    CLOSED = "closed"
