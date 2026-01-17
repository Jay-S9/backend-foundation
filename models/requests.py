from pydantic import BaseModel, Field


class CreateAccountRequest(BaseModel):
    account_id: str = Field(..., min_length=1)
    initial_balance: float = Field(..., ge=0)


class DepositRequest(BaseModel):
    amount: float = Field(..., gt=0)
    idempotency_key: str = Field(..., min_length=1)


class WithdrawRequest(BaseModel):
    amount: float = Field(..., gt=0)
