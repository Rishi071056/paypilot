from typing import Annotated

from fastapi import FastAPI, Header, HTTPException

from app.agents.payment_agent import PaymentProposal, PaymentRequest
from app.services.idempotency import IdempotencyConflict, idempotency_store


app = FastAPI(
    title="PayPilot API",
    description="Universal AI Payment & Commerce Agent",
    version="0.2.0",
)


@app.get("/")
async def root():
    return {
        "name": "PayPilot",
        "message": "Universal AI Payment & Commerce Agent",
        "version": "0.2.0",
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "paypilot-api",
    }


@app.post(
    "/api/v1/payments/proposals",
    response_model=PaymentProposal,
)
async def create_payment_proposal(
    request: PaymentRequest,
    idempotency_key: Annotated[
        str,
        Header(
            alias="Idempotency-Key",
            min_length=1,
            max_length=128,
        ),
    ],
) -> PaymentProposal:
    try:
        return idempotency_store.get_or_create(idempotency_key, request)
    except IdempotencyConflict as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc
