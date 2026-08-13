"""Lab 05 — persist and resume a session.

Creates a session with a known id, sends a message, closes it, then resumes the
*same* session. Passing ``--resume <id>`` lets readers prove the same idea from
a second process when the same store is available.
"""

import uuid

from copilot import CopilotClient

from sdk_labs import model_picker
from sdk_labs._common import send_and_print


async def run(requested_model_id: str | None, resume_session_id: str | None) -> int:
    print("== Lab 05: sessions ==\n")

    async with CopilotClient() as client:
        model_id = await model_picker.pick(client, requested_model_id)
        if model_id is None:
            return 1

        if resume_session_id:
            return await _resume_existing(client, resume_session_id, model_id)

        session_id = f"sdklabs-{uuid.uuid4().hex}"[:24]
        print(f"Session id: {session_id}\n")

        # --- First conversation turn -------------------------------------
        print("--- Turn 1 (new session) ---")
        session = await client.create_session(
            session_id=session_id,
            model=model_id,
            streaming=False,
        )
        async with session:
            await send_and_print(
                session,
                "Remember this: my favourite retail segment is 'At Risk'. Reply with just OK.",
            )

        print("\nSession closed.\n")

        # --- Resume the same session -------------------------------------
        print("--- Turn 2 (resumed session) ---")
        resumed = await client.resume_session(session_id, model=model_id, streaming=False)
        async with resumed:
            await send_and_print(resumed, "Which retail segment did I say was my favourite?")

        # --- Inspect stored sessions -------------------------------------
        print("\n--- Session metadata ---")
        metadata = await client.get_session_metadata(session_id)
        print(
            "  (no metadata returned)"
            if metadata is None
            else f"  id={session_id} metadata retrieved"
        )

    return 0


async def _resume_existing(client: CopilotClient, session_id: str, model_id: str) -> int:
    print(f"Session id: {session_id}\n")
    print("--- Resumed existing session ---")

    resumed = await client.resume_session(session_id, model=model_id, streaming=False)
    async with resumed:
        await send_and_print(resumed, "Which retail segment did I say was my favourite?")

    print("\n--- Session metadata ---")
    metadata = await client.get_session_metadata(session_id)
    print(
        "  (no metadata returned)" if metadata is None else f"  id={session_id} metadata retrieved"
    )

    return 0
