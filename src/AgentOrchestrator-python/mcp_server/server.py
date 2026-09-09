"""Read-only MCP server over the retail SQLite database.

Why this exists
---------------
``CopilotChatService`` used to send prompts to the model with no access to the
application's own data, so the chat could not answer questions like "who are my
highest-spending customers?". This server closes that gap by exposing a small
set of **read-only** domain tools over ``retail.db``.

Two deliberate design choices are worth calling out for the labs:

1. **Least privilege at the connection, not just in code.** The engine opens
   SQLite with ``mode=ro``, so a write is rejected by the driver itself. Even a
   prompt-injected instruction to modify data cannot succeed.

2. **Domain tools, not raw SQL.** The model gets ``get_customer_summary``, not
   ``run_query``. The tool surface is the security boundary, so there is no
   arbitrary-SQL escape hatch to reason about.

The REST API keeps its direct EF-Core-style access through
``RetailAnalyticsService`` — MCP is for the *model*, not for the application
talking to its own database.

Mirrors ``AgentHQDemo.McpServer/RetailTools.cs`` in the .NET track.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations
from sqlalchemy import Engine
from sqlmodel import Session, create_engine, select

from app.models import CustomerSegment, Transaction
from app.services.retail_analytics import RetailAnalyticsService

#: Same on-disk file the API writes through ``app.database``. Overridable so the
#: server can be pointed at a test fixture.
DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "retail.db"

#: Cap on rows returned by a single call, so a broad question cannot pull the
#: whole table into the model's context window.
MAX_LIMIT = 200

READ_ONLY = ToolAnnotations(read_only_hint=True, destructive_hint=False, open_world_hint=False)


def database_path() -> Path:
    """Resolves the database file, honouring the RETAIL_DB_PATH override."""
    override = os.environ.get("RETAIL_DB_PATH")
    return Path(override).expanduser().resolve() if override else DEFAULT_DB_PATH


def create_read_only_engine(db_path: Path | None = None) -> Engine:
    """Creates an engine that physically cannot write.

    ``mode=ro`` is enforced by SQLite, so this is a stronger guarantee than
    simply not writing any INSERT statements in the tool bodies.
    """
    path = db_path or database_path()
    if not path.exists():
        raise FileNotFoundError(
            f"Retail database not found at {path}. Start the API once "
            "(uv run uvicorn app.main:app --port 5070) to create and seed it."
        )

    # The uri=true form is what lets SQLite honour the mode=ro flag.
    return create_engine("sqlite:///file:" + str(path) + "?mode=ro&uri=true")


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _transaction_json(txn: Transaction) -> dict[str, Any]:
    """Shapes a row the same way the REST API does, so the model sees one contract."""
    return {
        "id": txn.id,
        "customerId": txn.customer_id,
        "amount": txn.amount,
        "productCategory": txn.product_category,
        "storeId": txn.store_id,
        "timestamp": _iso(txn.timestamp),
        "isFlagged": txn.is_flagged,
    }


def _segment_json(segment: CustomerSegment) -> dict[str, Any]:
    return {
        "id": segment.id,
        "name": segment.name,
        "description": segment.description,
        "customerCount": segment.customer_count,
        "avgMonthlySpend": segment.avg_monthly_spend,
        "retentionRate": segment.retention_rate,
    }


def build_server(engine: Engine | None = None) -> MCPServer:
    """Builds the MCP server. The engine is injectable so tests can supply a fixture."""
    db_engine = engine or create_read_only_engine()

    server = MCPServer(
        name="retail-analytics",
        instructions=(
            "Read-only access to the retail analytics database. Use these tools to "
            "answer questions about real transactions, customer segments and "
            "spending behaviour instead of guessing. All tools are read-only."
        ),
    )

    @server.tool(
        description="Lists retail transactions, most recent first. "
        "Optionally filter to a single customer.",
        annotations=READ_ONLY,
    )
    def list_transactions(customer_id: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        capped = max(1, min(limit, MAX_LIMIT))
        with Session(db_engine) as session:
            statement = select(Transaction)
            if customer_id:
                statement = statement.where(Transaction.customer_id == customer_id)
            statement = statement.order_by(Transaction.timestamp.desc()).limit(capped)
            return [_transaction_json(t) for t in session.exec(statement).all()]

    @server.tool(
        description="Gets a single retail transaction by its numeric id.",
        annotations=READ_ONLY,
    )
    def get_transaction(transaction_id: int) -> dict[str, Any] | None:
        with Session(db_engine) as session:
            txn = session.get(Transaction, transaction_id)
            return _transaction_json(txn) if txn else None

    @server.tool(
        description="Lists the customer segments with their size, average monthly "
        "spend and retention rate.",
        annotations=READ_ONLY,
    )
    def list_segments() -> list[dict[str, Any]]:
        with Session(db_engine) as session:
            return [_segment_json(s) for s in session.exec(select(CustomerSegment)).all()]

    @server.tool(
        description="Summarises one customer's spending: total, average, transaction "
        "count and the categories they buy from.",
        annotations=READ_ONLY,
    )
    def get_customer_summary(customer_id: str) -> dict[str, Any]:
        with Session(db_engine) as session:
            rows = list(
                session.exec(
                    select(Transaction).where(Transaction.customer_id == customer_id)
                ).all()
            )

        if not rows:
            return {
                "customerId": customer_id,
                "transactionCount": 0,
                "totalSpend": 0.0,
                "averageSpend": 0.0,
                "categories": [],
                "firstPurchase": None,
                "lastPurchase": None,
            }

        total = sum(r.amount for r in rows)
        timestamps = [r.timestamp for r in rows if r.timestamp]
        return {
            "customerId": customer_id,
            "transactionCount": len(rows),
            "totalSpend": round(total, 2),
            "averageSpend": round(total / len(rows), 2),
            "categories": sorted({r.product_category for r in rows}),
            "firstPurchase": _iso(min(timestamps)) if timestamps else None,
            "lastPurchase": _iso(max(timestamps)) if timestamps else None,
        }

    @server.tool(
        description="Predicts which segment a customer belongs to, with a confidence "
        "score and the features behind the call.",
        annotations=READ_ONLY,
    )
    async def predict_segment(customer_id: str) -> dict[str, Any]:
        # Reuses the API's own scoring logic rather than reimplementing it, so the
        # chat and the REST endpoint can never disagree about a customer.
        with Session(db_engine) as session:
            prediction = await RetailAnalyticsService(session).predict_segment(customer_id)
        return prediction.model_dump(by_alias=True)

    return server
