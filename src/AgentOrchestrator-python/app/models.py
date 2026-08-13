"""Retail domain models.

Mirrors ``AgentHQDemo.Api/Models`` from the .NET version.

Two Python-specific details are worth knowing:

1. **Validation is split in two.** The .NET model carries
   ``[Required]``/``[StringLength]``/``[Range]`` annotations that ASP.NET Core
   checks via ``ModelState``. SQLModel skips validation on ``table=True``
   classes, so the validated fields live on ``TransactionBase`` (what FastAPI
   checks on the request body and what the validation tests exercise) and
   ``Transaction`` inherits them for persistence.

2. **JSON stays camelCase.** ``System.Text.Json`` emits ``customerId`` by
   default. These models keep Python's snake_case internally but serialize
   through a camelCase alias generator, so the HTTP contract matches the .NET
   API and the labs' ``curl`` examples work unchanged against either stack.
"""

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict
from pydantic import Field as PydanticField
from pydantic.alias_generators import to_camel
from sqlmodel import Field, SQLModel

#: Serialize as camelCase but still accept snake_case when constructing in Python.
CAMEL_CONFIG = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class TransactionBase(SQLModel):
    """Validated fields for a retail purchase transaction."""

    model_config = CAMEL_CONFIG

    customer_id: str = Field(min_length=1, max_length=100)
    amount: float = Field(ge=0.01, le=1_000_000)
    product_category: str = Field(min_length=1, max_length=50)
    store_id: str = Field(min_length=1, max_length=50)


class Transaction(TransactionBase, table=True):
    """A retail purchase transaction."""

    id: int | None = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    is_flagged: bool = False


class TransactionCreate(TransactionBase):
    """Request body for creating a transaction.

    FastAPI validates this automatically and returns HTTP 422 on failure, which
    is what ``ModelState.IsValid`` does in the .NET ``TransactionsController``.
    """


class CustomerSegment(SQLModel, table=True):
    """A customer segment grouping for analytics."""

    model_config = CAMEL_CONFIG

    id: int | None = Field(default=None, primary_key=True)
    name: str = ""
    description: str = ""
    customer_count: int = 0
    avg_monthly_spend: float = 0
    retention_rate: float = 0


class SegmentPrediction(BaseModel):
    """Prediction result for customer segment classification."""

    model_config = CAMEL_CONFIG

    customer_id: str
    predicted_segment: str
    confidence: float
    top_features: list[str] = PydanticField(default_factory=list)
