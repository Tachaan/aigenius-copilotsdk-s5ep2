"""Tests for RetailAnalyticsService.

Mirrors ``tests/AgentHQDemo.Tests/RetailAnalyticsServiceTests.cs``.
"""

from app.models import Transaction
from app.services.retail_analytics import RetailAnalyticsService


async def test_seed_data_creates_10_transactions(service: RetailAnalyticsService) -> None:
    await service.seed_data()

    transactions = await service.get_transactions()
    assert len(transactions) == 10


async def test_seed_data_creates_4_segments(service: RetailAnalyticsService) -> None:
    await service.seed_data()

    segments = await service.get_segments()
    assert len(segments) == 4
    assert any(s.name == "High Value" for s in segments)
    assert any(s.name == "At Risk" for s in segments)


async def test_add_transaction_persists_to_database(service: RetailAnalyticsService) -> None:
    txn = Transaction(
        customer_id="C099",
        amount=100,
        product_category="Grocery",
        store_id="S001",
    )

    created = await service.add_transaction(txn)

    assert created.id is not None
    assert created.id > 0
    retrieved = await service.get_transaction(created.id)
    assert retrieved.customer_id == "C099"


async def test_predict_segment_high_spender_returns_high_value(
    service: RetailAnalyticsService,
) -> None:
    await service.seed_data()

    prediction = await service.predict_segment("C003")

    assert prediction.predicted_segment == "High Value"
    assert prediction.confidence > 0.5


async def test_predict_segment_unknown_customer_returns_new(
    service: RetailAnalyticsService,
) -> None:
    prediction = await service.predict_segment("C999")

    assert prediction.predicted_segment == "New"
