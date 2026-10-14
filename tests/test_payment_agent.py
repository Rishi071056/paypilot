
import sys
from pathlib import Path

# Make the backend app importable during tests.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

import pytest
from pydantic import ValidationError

from app.agents.payment_agent import PaymentRequest, propose_payment


def make_request(**overrides):
    data = {
        "sender_country": "IN",
        "recipient_country": "AU",
        "amount": "100.00",
        "currency": "AUD",
        "payment_type": "business_purchase",
        "recipient_id": "vendor-demo",
    }
    data.update(overrides)
    return PaymentRequest(**data)


def test_valid_request_creates_proposal():
    request = make_request()
    proposal = propose_payment(request)

    assert proposal.status == "proposed"
    assert proposal.request.amount == request.amount
    assert proposal.execution_allowed is False
    assert proposal.requires_approval is True


def test_country_and_currency_are_normalized():
    request = make_request(
        sender_country="in",
        recipient_country="au",
        currency="aud",
    )

    assert request.sender_country == "IN"
    assert request.recipient_country == "AU"
    assert request.currency == "AUD"


@pytest.mark.parametrize("amount", ["0", "-10", "not-a-number"])
def test_invalid_amount_is_rejected(amount):
    with pytest.raises(ValidationError):
        make_request(amount=amount)


def test_invalid_country_format_is_rejected():
    with pytest.raises(ValidationError):
        make_request(sender_country="IND")


def test_invalid_payment_type_is_rejected():
    with pytest.raises(ValidationError):
        make_request(payment_type="unknown")


def test_each_proposal_gets_a_unique_id():
    request = make_request()

    first = propose_payment(request)
    second = propose_payment(request)

    assert first.payment_id != second.payment_id
