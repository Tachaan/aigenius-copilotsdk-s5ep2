"""Service for retail transaction analytics and customer segmentation.

Contains intentional issues for code review demonstrations. These mirror the
four deliberate smells in the .NET ``RetailAnalyticsService`` so the code-review
and agent labs produce the same findings in both languages. Do not "fix" them
without reading docs/labs/ first.
"""

from datetime import UTC, datetime, timedelta

from sqlmodel import Session, select

from app.models import CustomerSegment, SegmentPrediction, Transaction


class RetailAnalyticsService:
    def __init__(self, db: Session) -> None:
        self._db = db

    async def get_transactions_with_segments(self) -> list[dict]:
        """Returns all transactions with segment info.

        BUG: N+1 query — loops through each transaction to look up segment.
        """
        transactions = list(self._db.exec(select(Transaction)).all())
        results: list[dict] = []

        for txn in transactions:
            # N+1: querying segments for every single transaction
            segment = await self.predict_segment(txn.customer_id)
            results.append(
                {
                    "id": txn.id,
                    "customerId": txn.customer_id,
                    "amount": txn.amount,
                    "productCategory": txn.product_category,
                    "storeId": txn.store_id,
                    "timestamp": txn.timestamp,
                    "isFlagged": txn.is_flagged,
                    "predictedSegment": segment.predicted_segment,
                }
            )

        return results

    async def get_transactions(self) -> list[Transaction]:
        return list(self._db.exec(select(Transaction)).all())

    async def get_transaction(self, transaction_id: int) -> Transaction:
        """Returns a single transaction by ID.

        BUG: Missing null check — returns None without proper handling.
        """
        # Missing null check: will return None if not found
        return self._db.get(Transaction, transaction_id)

    async def add_transaction(self, transaction: Transaction) -> Transaction:
        """Adds a new transaction.

        BUG: No input validation — allows negative amounts and empty customer IDs.
        """
        # No validation: negative amounts and empty customer_id are allowed
        transaction.timestamp = datetime.now(UTC)
        self._db.add(transaction)
        self._db.commit()
        self._db.refresh(transaction)
        return transaction

    async def delete_transaction(self, transaction_id: int) -> bool:
        txn = self._db.get(Transaction, transaction_id)
        if txn is None:
            return False
        self._db.delete(txn)
        self._db.commit()
        return True

    async def get_segments(self) -> list[CustomerSegment]:
        return list(self._db.exec(select(CustomerSegment)).all())

    async def get_segment(self, segment_id: int) -> CustomerSegment | None:
        return self._db.get(CustomerSegment, segment_id)

    async def predict_segment(self, customer_id: str) -> SegmentPrediction:
        """Predicts which segment a customer belongs to based on spending.

        BUG: Hardcoded magic number threshold (1000).
        """
        transactions = list(
            self._db.exec(select(Transaction).where(Transaction.customer_id == customer_id)).all()
        )

        if len(transactions) == 0:
            return SegmentPrediction(
                customer_id=customer_id,
                predicted_segment="New",
                confidence=0.5,
                top_features=["no_history"],
            )

        total_spend = sum(t.amount for t in transactions)
        avg_spend = total_spend / len(transactions)
        frequency = len(transactions)

        # BUG: Hardcoded magic number — should be configurable
        if total_spend > 1000:
            return SegmentPrediction(
                customer_id=customer_id,
                predicted_segment="High Value",
                confidence=0.89,
                top_features=["high_total_spend", "multi_category", f"total_{total_spend:.0f}"],
            )

        if frequency >= 3:
            return SegmentPrediction(
                customer_id=customer_id,
                predicted_segment="Regular",
                confidence=0.75,
                top_features=[
                    "frequent_purchases",
                    f"frequency_{frequency}",
                    f"avg_{avg_spend:.0f}",
                ],
            )

        if avg_spend < 50:
            return SegmentPrediction(
                customer_id=customer_id,
                predicted_segment="At Risk",
                confidence=0.62,
                top_features=["low_avg_spend", f"avg_{avg_spend:.0f}", f"total_{total_spend:.0f}"],
            )

        return SegmentPrediction(
            customer_id=customer_id,
            predicted_segment="Regular",
            confidence=0.55,
            top_features=["moderate_activity", f"total_{total_spend:.0f}"],
        )

    async def seed_data(self) -> None:
        """Seeds the database with sample retail data."""
        if self._db.exec(select(Transaction)).first() is not None:
            return

        now = datetime.now(UTC)
        self._db.add_all(
            [
                Transaction(
                    customer_id="C001",
                    amount=245.50,
                    product_category="Grocery",
                    store_id="S001",
                    timestamp=now - timedelta(days=30),
                ),
                Transaction(
                    customer_id="C001",
                    amount=89.99,
                    product_category="Electronics",
                    store_id="S002",
                    timestamp=now - timedelta(days=25),
                ),
                Transaction(
                    customer_id="C002",
                    amount=32.00,
                    product_category="Grocery",
                    store_id="S001",
                    timestamp=now - timedelta(days=20),
                ),
                Transaction(
                    customer_id="C002",
                    amount=15.50,
                    product_category="Health",
                    store_id="S003",
                    timestamp=now - timedelta(days=18),
                ),
                Transaction(
                    customer_id="C003",
                    amount=1250.00,
                    product_category="Electronics",
                    store_id="S002",
                    timestamp=now - timedelta(days=15),
                ),
                Transaction(
                    customer_id="C003",
                    amount=450.00,
                    product_category="Fashion",
                    store_id="S004",
                    timestamp=now - timedelta(days=10),
                ),
                Transaction(
                    customer_id="C004",
                    amount=12.99,
                    product_category="Grocery",
                    store_id="S001",
                    timestamp=now - timedelta(days=8),
                ),
                Transaction(
                    customer_id="C004",
                    amount=8.50,
                    product_category="Grocery",
                    store_id="S001",
                    timestamp=now - timedelta(days=5),
                ),
                Transaction(
                    customer_id="C005",
                    amount=675.00,
                    product_category="Electronics",
                    store_id="S002",
                    timestamp=now - timedelta(days=3),
                ),
                Transaction(
                    customer_id="C005",
                    amount=320.00,
                    product_category="Fashion",
                    store_id="S004",
                    timestamp=now - timedelta(days=1),
                ),
            ]
        )

        self._db.add_all(
            [
                CustomerSegment(
                    name="High Value",
                    description="Top 10% spenders with strong loyalty indicators",
                    customer_count=150,
                    avg_monthly_spend=850,
                    retention_rate=0.92,
                ),
                CustomerSegment(
                    name="Regular",
                    description="Consistent monthly shoppers across categories",
                    customer_count=3200,
                    avg_monthly_spend=180,
                    retention_rate=0.78,
                ),
                CustomerSegment(
                    name="At Risk",
                    description="Declining purchase frequency over past 90 days",
                    customer_count=890,
                    avg_monthly_spend=95,
                    retention_rate=0.45,
                ),
                CustomerSegment(
                    name="New",
                    description="Joined within the last 90 days",
                    customer_count=420,
                    avg_monthly_spend=120,
                    retention_rate=0.65,
                ),
            ]
        )

        self._db.commit()
