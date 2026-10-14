"""Development-only idempotency storage.

This in-memory implementation is for local development and tests.
Replace it with a durable shared store before production use.
"""

import hashlib
import json
from threading import Lock

from app.agents.payment_agent import (
    PaymentProposal,
    PaymentRequest,
    propose_payment,
)


class IdempotencyConflict(Exception):
    """Raised when a key is reused with a different request."""


class InMemoryIdempotencyStore:
    def __init__(self) -> None:
        self._records: dict[str, tuple[str, PaymentProposal]] = {}
        self._lock = Lock()

    @staticmethod
    def _fingerprint(request: PaymentRequest) -> str:
        payload = request.model_dump(mode="json")
        canonical = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def get_or_create(
        self,
        key: str,
        request: PaymentRequest,
    ) -> PaymentProposal:
        fingerprint = self._fingerprint(request)

        with self._lock:
            existing = self._records.get(key)

            if existing is not None:
                saved_fingerprint, saved_proposal = existing

                if saved_fingerprint != fingerprint:
                    raise IdempotencyConflict(
                        "This Idempotency-Key was already used "
                        "with a different payment request."
                    )

                return saved_proposal

            proposal = propose_payment(request)
            self._records[key] = (fingerprint, proposal)
            return proposal


# Temporary local-development store; data disappears on restart.
idempotency_store = InMemoryIdempotencyStore()
