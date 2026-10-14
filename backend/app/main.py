
from fastapi import FastAPI

from app.agents.payment_agent import (
    PaymentRequest,
    PaymentProposal,
    propose_payment,
)

app = FastAPI(
    title="PayPilot API",
    description="Universal AI Payment & Commerce Agent",
    version="0.1.0",
)


@app.get("/")
async def root():
    return {
        "name": "PayPilot",
        "message": "Universal AI Payment & Commerce Agent",
        "version": "0.1.0",
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
) -> PaymentProposal:
    return propose_payment(request)

