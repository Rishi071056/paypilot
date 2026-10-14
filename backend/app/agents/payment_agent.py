
from decimal import Decimal
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PaymentRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    sender_country: str = Field(min_length=2, max_length=2)
    recipient_country: str = Field(min_length=2, max_length=2)
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    currency: str = Field(min_length=3, max_length=3)

    payment_type: Literal[
        "business_purchase",
        "vendor_payout",
        "personal_transfer",
    ]

    recipient_id: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=500)

    @field_validator("sender_country", "recipient_country")
    @classmethod
    def validate_country(cls, value: str) -> str:
        value = value.upper()
        if not value.isascii() or not value.isalpha():
            raise ValueError("Country must be a two-letter code")
        return value

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str) -> str:
        value = value.upper()
        if not value.isascii() or not value.isalpha():
            raise ValueError("Currency must be a three-letter code")
        return value


class PaymentProposal(BaseModel):
    payment_id: str
    status: Literal["proposed", "blocked"]
    request: PaymentRequest
    requires_approval: bool = True
    execution_allowed: bool = False
    explanation: str


def propose_payment(request: PaymentRequest) -> PaymentProposal:
    return PaymentProposal(
        payment_id=f"proposal-{uuid4()}",
        status="proposed",
        request=request,
        requires_approval=True,
        execution_allowed=False,
        explanation=(
            "Request passed structural validation. "
            "Capability, risk and policy checks are still required."
        ),
    )
