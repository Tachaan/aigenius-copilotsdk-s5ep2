"""Tests for the read-only retail MCP server.

Mirrors ``tests/AgentHQDemo.Tests/RetailToolsTests.cs`` in the .NET track.

These cover the tool surface the model sees. The point of the server is that it
is the security boundary, so the read-only guarantee is tested too.
"""

import sqlite3
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from mcp.server.mcpserver import MCPServer
from sqlalchemy import Engine, text
from sqlalchemy.exc import OperationalError
from sqlmodel import Session

from app.models import CustomerSegment, Transaction
from mcp_server.server import build_server, create_read_only_engine


@pytest.fixture(name="server")
def server_fixture(engine: Engine) -> MCPServer:
    """Builds the server over the in-memory test database, pre-seeded."""
    now = datetime.now(UTC)
    with Session(engine) as session:
        session.add_all(
            [
                Transaction(
                    customer_id="C001",
                    amount=100.0,
                    product_category="Grocery",
                    store_id="S001",
                    timestamp=now - timedelta(days=3),
                ),
                Transaction(
                    customer_id="C001",
                    amount=250.0,
                    product_category="Fashion",
                    store_id="S002",
                    timestamp=now - timedelta(days=1),
                ),
                Transaction(
                    customer_id="C002",
                    amount=20.0,
                    product_category="Grocery",
                    store_id="S001",
                    timestamp=now - timedelta(days=2),
                ),
            ]
        )
        session.add(
            CustomerSegment(
                name="High Value",
                description="Top spenders",
                customer_count=10,
                avg_monthly_spend=500,
                retention_rate=0.9,
            )
        )
        session.commit()

    return build_server(engine)


async def call(server: MCPServer, name: str, **arguments: Any) -> Any:
    """Calls a tool and unwraps the payload.

    A tool returning a list is wrapped by the SDK as ``{"result": [...]}``,
    whereas a dict comes back as-is.
    """
    result = await server.call_tool(name, arguments)
    content = result.structured_content
    if isinstance(content, dict) and set(content) == {"result"}:
        return content["result"]
    return content


async def test_exposes_the_expected_tools(server: MCPServer):
    names = {t.name for t in await server.list_tools()}
    assert names == {
        "list_transactions",
        "get_transaction",
        "list_segments",
        "get_customer_summary",
        "predict_segment",
    }


async def test_every_tool_is_marked_read_only(server: MCPServer):
    # The annotation is what tells a host it is safe to auto-approve, so a tool
    # gaining a side effect must not silently keep the read-only hint.
    for tool in await server.list_tools():
        assert tool.annotations is not None, tool.name
        assert tool.annotations.read_only_hint is True, tool.name


async def test_list_transactions_filters_by_customer(server: MCPServer):
    rows = await call(server, "list_transactions", customer_id="C001")

    assert len(rows) == 2
    assert {r["customerId"] for r in rows} == {"C001"}


async def test_list_transactions_returns_newest_first(server: MCPServer):
    rows = await call(server, "list_transactions", customer_id="C001")

    assert [r["amount"] for r in rows] == [250.0, 100.0]


async def test_list_transactions_caps_the_limit(server: MCPServer):
    # Guards the context window: a huge limit must not return a huge result.
    rows = await call(server, "list_transactions", limit=10_000)

    assert len(rows) == 3


async def test_get_transaction_returns_none_when_missing(server: MCPServer):
    assert await call(server, "get_transaction", transaction_id=9999) is None


async def test_list_segments_returns_seeded_segments(server: MCPServer):
    rows = await call(server, "list_segments")

    assert len(rows) == 1
    assert rows[0]["name"] == "High Value"
    assert rows[0]["retentionRate"] == 0.9


async def test_customer_summary_aggregates_spend(server: MCPServer):
    summary = await call(server, "get_customer_summary", customer_id="C001")

    assert summary["transactionCount"] == 2
    assert summary["totalSpend"] == 350.0
    assert summary["averageSpend"] == 175.0
    assert summary["categories"] == ["Fashion", "Grocery"]


async def test_customer_summary_handles_unknown_customer(server: MCPServer):
    summary = await call(server, "get_customer_summary", customer_id="NOPE")

    assert summary["transactionCount"] == 0
    assert summary["totalSpend"] == 0
    assert summary["categories"] == []


async def test_predict_segment_matches_the_api_logic(server: MCPServer):
    prediction = await call(server, "predict_segment", customer_id="C002")

    # C002 has a single 20.00 purchase, so the service's "At Risk" branch wins.
    assert prediction["customerId"] == "C002"
    assert prediction["predictedSegment"] == "At Risk"


async def test_read_only_engine_rejects_writes():
    """The security guarantee: writes fail at the driver, not by convention."""
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "retail.db"
        connection = sqlite3.connect(db_path)
        connection.execute("CREATE TABLE probe (id INTEGER)")
        connection.commit()
        connection.close()

        engine = create_read_only_engine(db_path)
        try:
            with Session(engine) as session:
                # The row reads back fine, so the connection genuinely works...
                assert session.exec(text("SELECT count(*) FROM probe")).one()[0] == 0

                # ...but SQLite itself refuses the write.
                with pytest.raises(OperationalError, match="readonly"):
                    session.exec(text("INSERT INTO probe (id) VALUES (1)"))
        finally:
            engine.dispose()


async def test_missing_database_is_reported_clearly():
    with tempfile.TemporaryDirectory() as tmp:
        with pytest.raises(FileNotFoundError, match="Retail database not found"):
            create_read_only_engine(Path(tmp) / "absent.db")
