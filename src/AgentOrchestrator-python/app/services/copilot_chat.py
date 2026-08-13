"""Service for managing Copilot chat sessions.

Demonstrates GitHub Copilot SDK integration for the Three Mondays demo.

The interesting difference from the .NET version is streaming. The SDK delivers
events by *calling a handler*, not by exposing an async iterator, so this module
bridges those callbacks into an ``asyncio.Queue`` and drains the queue as an
async generator. .NET does the same thing with ``System.Threading.Channels``.
"""

import asyncio
import logging
from collections.abc import AsyncIterator

from copilot import CopilotClient, SessionEvent, SessionEventType

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "claude-haiku-4.5"

# Sentinel pushed onto the queue when the session goes idle.
_DONE = object()


class CopilotChatService:
    def __init__(self) -> None:
        self._client: CopilotClient | None = None
        self._is_started = False
        self._lock = asyncio.Lock()

    async def ensure_started(self) -> None:
        """Ensures the Copilot client is started. Recreates if connection was lost."""
        async with self._lock:
            if self._is_started and self._client is not None:
                return

            # Reset in case of a previous failed connection
            self._is_started = False
            if self._client is not None:
                try:
                    await self._client.stop()
                except Exception:  # noqa: BLE001 - ignore cleanup errors
                    pass

            self._client = CopilotClient()
            await self._client.start()
            self._is_started = True
            logger.info("Copilot client started")

    async def list_models(self) -> list[tuple[str, str]]:
        """Lists the models the connected Copilot CLI actually offers."""
        await self.ensure_started()

        if self._client is None:
            return []

        models = await self._client.list_models()
        return [(m.id, m.name or m.id) for m in models or [] if m.id]

    async def chat_stream(
        self,
        prompt: str,
        model: str = DEFAULT_MODEL,
        system_message: str | None = None,
    ) -> AsyncIterator[str]:
        """Sends a chat message and streams the response."""
        await self.ensure_started()

        if self._client is None:
            yield "Error: Copilot client not initialized"
            return

        logger.info("Creating session with model: %s", model)

        queue: asyncio.Queue[object] = asyncio.Queue()
        loop = asyncio.get_running_loop()

        async def run_session() -> None:
            try:
                session = await self._client.create_session(
                    model=model,
                    streaming=True,
                    system_message=(
                        {"mode": "append", "content": system_message} if system_message else None
                    ),
                )

                async with session:
                    done: asyncio.Future[None] = loop.create_future()

                    def on_event(evt: SessionEvent) -> None:
                        # Unlike .NET, every event arrives as one SessionEvent
                        # carrying a `type` enum and a `data` payload, so this
                        # dispatches on `evt.type` rather than on subclasses.
                        if evt.type is SessionEventType.ASSISTANT_MESSAGE_DELTA:
                            queue.put_nowait(evt.data.delta_content or "")
                        elif evt.type is SessionEventType.ASSISTANT_MESSAGE:
                            logger.info(
                                "Assistant response complete: %d chars",
                                len(evt.data.content or ""),
                            )
                        elif evt.type is SessionEventType.SESSION_IDLE:
                            if not done.done():
                                done.set_result(None)
                        elif evt.type is SessionEventType.SESSION_ERROR:
                            logger.error("Session error: %s", evt.data.message)
                            if not done.done():
                                done.set_exception(RuntimeError(evt.data.message))

                    session.on(on_event)

                    await session.send(prompt)
                    await done

                queue.put_nowait(_DONE)
            except (ConnectionError, OSError) as ex:
                logger.warning("Copilot connection lost: %s", ex)
                self._is_started = False
                queue.put_nowait(ex)
            except Exception as ex:  # noqa: BLE001 - surfaced to the caller below
                queue.put_nowait(ex)

        task = asyncio.create_task(run_session())

        try:
            while True:
                item = await queue.get()
                if item is _DONE:
                    break
                if isinstance(item, BaseException):
                    raise item
                yield item  # type: ignore[misc]
        finally:
            if not task.done():
                task.cancel()

    async def chat(
        self,
        prompt: str,
        model: str = DEFAULT_MODEL,
        system_message: str | None = None,
    ) -> str:
        """Sends a chat message and returns the complete response."""
        chunks = [chunk async for chunk in self.chat_stream(prompt, model, system_message)]
        return "".join(chunks)

    async def close(self) -> None:
        if self._client is not None:
            await self._client.stop()
            self._client = None
            self._is_started = False
            logger.info("Copilot client stopped")
