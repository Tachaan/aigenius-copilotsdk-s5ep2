"""Validation tests for the Transaction model.

Mirrors ``tests/AgentHQDemo.Tests/TransactionValidationTests.cs``. Where .NET
uses ``Validator.TryValidateObject`` against data annotations, Python validates
the Pydantic model and inspects ``ValidationError`` entries.
"""

import pytest
from pydantic import ValidationError

from app.models import TransactionCreate


def validate_model(**kwargs) -> list[str]:
    """Returns the field names that failed validation, or [] when valid."""
    try:
        TransactionCreate(**kwargs)
    except ValidationError as exc:
        return [str(err["loc"][0]) for err in exc.errors()]
    return []


VALID = {
    "customer_id": "C001",
    "amount": 100.50,
    "product_category": "Electronics",
    "store_id": "S001",
}


def test_valid_transaction_passes_validation() -> None:
    assert validate_model(**VALID) == []


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("customer_id", ""),
        ("amount", -10.00),
        ("amount", 0),
        ("amount", 1_000_001),
        ("product_category", ""),
        ("store_id", ""),
        ("customer_id", "A" * 101),
        ("product_category", "A" * 51),
    ],
    ids=[
        "empty_customer_id",
        "negative_amount",
        "zero_amount",
        "amount_too_high",
        "empty_product_category",
        "empty_store_id",
        "too_long_customer_id",
        "too_long_product_category",
    ],
)
def test_invalid_transaction_fails_validation(field: str, value: object) -> None:
    errors = validate_model(**{**VALID, field: value})

    assert errors != []
    assert field in errors
