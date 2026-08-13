"""Lab 04 — observe the session event lifecycle.

Logs every event the session emits, in order, so you can see what actually
arrives and in what sequence rather than guessing from the type names.
"""

from copilot import CopilotClient, SessionEvent, SessionEventType

from sdk_labs import model_picker
from sdk_labs._common import IdleWaiter, trim


async def run(requested_model_id: str | None) -> int:
    print("== Lab 04: events ==\n")

    async with CopilotClient() as client:
        model_id = await model_picker.pick(client, requested_model_id)
        if model_id is None:
            return 1

        session = await client.create_session(model=model_id, streaming=True)

        async with session:
            waiter = IdleWaiter()
            counters = {"order": 0, "deltas": 0}

            def on_event(evt: SessionEvent) -> None:
                # Deltas arrive in a flood; count them instead of printing each one.
                if evt.type is SessionEventType.ASSISTANT_MESSAGE_DELTA:
                    counters["deltas"] += 1
                    return

                counters["order"] += 1
                # Unlike C#, the event type is a value on the event rather than
                # a subclass, so this prints evt.type instead of a class name.
                print(f"{counters['order']:3d}. {evt.type.value}")

                if evt.type is SessionEventType.ASSISTANT_MESSAGE:
                    print(f"     content: {trim(evt.data.content)}")
                    print(f"     (preceded by {counters['deltas']} delta events)")
                elif evt.type is SessionEventType.SESSION_ERROR:
                    print(f"     ERROR: {evt.data.message}")

                waiter.handle(evt)

            session.on(on_event)

            print("Prompt: Name two retail KPIs. One line each.\n")
            await session.send("Name two retail KPIs. One line each.")

            await waiter.wait()

            print(f"\nTotal delta events: {counters['deltas']}")

    return 0
