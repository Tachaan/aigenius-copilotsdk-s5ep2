"""FastAPI application entry point.

Mirrors ``AgentHQDemo.Api/Program.cs``. One difference: this single app serves
both the API and the chat UI on port 5070, where the .NET version splits them
across the API (5050) and a Blazor WebAssembly host (5051).
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session

from app.database import create_db_and_tables, engine
from app.routers import chat, segments, transactions
from app.services.copilot_chat import CopilotChatService
from app.services.retail_analytics import RetailAnalyticsService

logging.basicConfig(level=logging.INFO)

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Seed database on startup
    create_db_and_tables()
    with Session(engine) as session:
        await RetailAnalyticsService(session).seed_data()

    # The Copilot client is a singleton for the app's lifetime, matching the
    # .NET AddSingleton<CopilotChatService> registration. It connects lazily on
    # first use so the API still starts without a Copilot CLI present.
    app.state.chat_service = CopilotChatService()

    yield

    await app.state.chat_service.close()


app = FastAPI(
    title="AgentHQDemo API (Python)",
    description="Python version of the AI Genius S5E2 Copilot SDK learning series",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(transactions.router)
app.include_router(segments.router)

# Mounted last so it does not shadow the /api routes above.
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
