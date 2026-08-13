"""Small helpers shared by the lab samples.

The SDK delivers events by calling a handler, so every sample needs the same
"wait until the session goes idle, but never wait forever" pattern. Keeping it
here means each sample file stays focused on the one idea it teaches.
"""

import asyncio

from copilot import CopilotSession, SessionEvent, SessionEventType

#: Never wait forever: a dropped transport means idle/error may never arrive.
TIMEOUT_SECONDS = 180


class IdleWaiter:
    """Resolves when the session reports idle, or raises on session error."""

    def __init__(self) -> None:
        self._future: asyncio.Future[None] = asyncio.get_event_loop().create_future()

    def handle(self, evt: SessionEvent) -> bool:
        """Returns True when the event was a terminal (idle/error) event."""
        if evt.type is SessionEventType.SESSION_IDLE:
            if not self._future.done():
                self._future.set_result(None)
            return True
        if evt.type is SessionEventType.SESSION_ERROR:
            if not self._future.done():
                self._future.set_exception(RuntimeError(evt.data.message))
            return True
        return False

    async def wait(self) -> None:
        await asyncio.wait_for(self._future, timeout=TIMEOUT_SECONDS)


def trim(text: str | None, limit: int = 80) -> str:
    if not text:
        return "(empty)"
    flat = " ".join(text.splitlines())
    return flat if len(flat) <= limit else flat[:limit] + "…"


def flatten(text: str | None) -> str:
    return " ".join((text or "").splitlines())


async def send_and_print(session: CopilotSession, prompt: str) -> None:
    """Sends a prompt and prints the assistant reply, then waits for idle."""
    waiter = IdleWaiter()

    def on_event(evt: SessionEvent) -> None:
        if evt.type is SessionEventType.ASSISTANT_MESSAGE and evt.data.content:
            print(f"Assistant: {flatten(evt.data.content)}")
        elif evt.type is SessionEventType.SESSION_ERROR:
            print(f"ERROR: {evt.data.message}")
        waiter.handle(evt)

    session.on(on_event)

    print(f"You: {prompt}")
    await session.send(prompt)
    await waiter.wait()
