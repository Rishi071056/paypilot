import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "backend"),
)

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def make_payload(amount: str = "25.00") -> dict:
    return {
        "sender_country": "US",
        "recipient_country": "GB",
        "amount": amount,
        "currency": "USD",
        "payment_type": "business_purchase",
        "recipient_id": "merchant-123",
        "description": "Test purchase",
    }


def test_same_key_and_payload_returns_same_proposal():
    headers = {"Idempotency-Key": "test-retry-001"}

    first = client.post(
        "/api/v1/payments/proposals",
        headers=headers,
        json=make_payload(),
    )
    second = client.post(
        "/api/v1/payments/proposals",
        headers=headers,
        json=make_payload(),
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()


def test_same_key_with_different_payload_returns_conflict():
    headers = {"Idempotency-Key": "test-conflict-001"}

    first = client.post(
        "/api/v1/payments/proposals",
        headers=headers,
        json=make_payload("25.00"),
    )
    second = client.post(
        "/api/v1/payments/proposals",
        headers=headers,
        json=make_payload("50.00"),
    )

    assert first.status_code == 200
    assert second.status_code == 409


def test_different_keys_create_different_proposals():
    first = client.post(
        "/api/v1/payments/proposals",
        headers={"Idempotency-Key": "test-distinct-001"},
        json=make_payload(),
    )
    second = client.post(
        "/api/v1/payments/proposals",
        headers={"Idempotency-Key": "test-distinct-002"},
        json=make_payload(),
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["payment_id"] != second.json()["payment_id"]


def test_missing_idempotency_key_is_rejected():
    response = client.post(
        "/api/v1/payments/proposals",
        json=make_payload(),
    )

    assert response.status_code == 422
