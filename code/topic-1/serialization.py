"""Topic 1 — how Python types serialize to JSON on the way out.

JSON has no datetime, UUID, or Decimal type — yet you return them from handlers and they
come out as sensible values. This demo shows what FastAPI/Pydantic do:
  - datetime  -> ISO 8601 string
  - UUID      -> string
  - Decimal   -> STRING (Pydantic v2 keeps it a string to preserve exact precision!)
  - Enum      -> its value
  - set       -> list

Run it:   uvicorn serialization:app --reload
Tests:    pytest test_serialization.py -v
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Topic 1 — Serialization")


class Currency(str, Enum):
    usd = "USD"
    eur = "EUR"


class Invoice(BaseModel):
    id: UUID
    created_at: datetime
    amount: Decimal
    currency: Currency
    tags: set[str]


@app.get("/invoice", response_model=Invoice)
async def get_invoice():
    # We return native Python types; FastAPI serializes them to JSON-friendly values.
    return Invoice(
        id=UUID("12345678-1234-5678-1234-567812345678"),
        created_at=datetime(2026, 7, 24, 12, 30, 0),
        amount=Decimal("19.99"),
        currency=Currency.usd,
        tags={"paid"},
    )
