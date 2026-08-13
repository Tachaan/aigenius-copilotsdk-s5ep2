"""Lab 03 — define a tool the model can call.

Instead of pasting retail context into a system message and hoping the model
uses it, register a real function. The model decides when to call it.
"""

from typing import Annotated

from copilot import (
    CopilotClient,
    PermissionHandler,
    SessionEvent,
    SessionEventType,
    ToolInvocation,
    define_tool,
)
from pydantic import BaseModel, Field

from sdk_labs import model_picker
from sdk_labs._common import IdleWaiter

#: In-memory stand-in for the transaction store.
TRANSACTIONS: list[tuple[str, float, str]] = [
    ("C001", 245.50, "Grocery"),
    ("C001", 89.99, "Electronics"),
    ("C002", 32.00, "Grocery"),
    ("C002", 15.50, "Health"),
    ("C003", 1250.00, "Electronics"),
    ("C003", 450.00, "Fashion"),
    ("C004", 12.99, "Grocery"),
    ("C004", 8.50, "Grocery"),
    ("C005", 675.00, "Electronics"),
    ("C005", 320.00, "Fashion"),
]


class GetCustomerTotalParams(BaseModel):
    """Parameter schema sent to the model.

    Where C# reads ``[Description]`` attributes off the method signature, Python
    describes parameters with a Pydantic model — the field descriptions are what
    the model sees.
    """

    customer_id: Annotated[str, Field(description="Customer identifier, for example C003")]


@define_tool(description="Gets the total amount a given retail customer has spent.")
def get_customer_total(params: GetCustomerTotalParams, _invocation: ToolInvocation) -> str:
    matches = [t for t in TRANSACTIONS if t[0].casefold() == params.customer_id.casefold()]

    if not matches:
        return f"No transactions found for {params.customer_id}."

    total = sum(t[1] for t in matches)
    print(f"  [tool] get_customer_total({params.customer_id}) -> ${total:,.2f}")
    return f"{params.customer_id} has {len(matches)} transactions totalling ${total:,.2f}."


async def run(requested_model_id: str | None) -> int:
    print("== Lab 03: tools ==\n")

    async with CopilotClient() as client:
        model_id = await model_picker.pick(client, requested_model_id)
        if model_id is None:
            return 1

        session = await client.create_session(
            model=model_id,
            streaming=False,
            tools=[get_customer_total],
            # Required in Python, unlike .NET: the runtime asks permission before
            # invoking a custom tool, and with no handler the call is denied and
            # the model reports a permission error instead of an answer.
            on_permission_request=PermissionHandler.approve_all,
        )

        async with session:
            waiter = IdleWaiter()

            def on_event(evt: SessionEvent) -> None:
                if evt.type is SessionEventType.ASSISTANT_MESSAGE:
                    # The first assistant message only carries the tool request,
                    # so its content is empty — skip it.
                    if evt.data.content:
                        print(f"\nAssistant: {evt.data.content}")
                elif evt.type is SessionEventType.SESSION_ERROR:
                    print(f"\nERROR: {evt.data.message}")
                waiter.handle(evt)

            session.on(on_event)

            print("Prompt: How much has customer C003 spent in total?\n")
            await session.send("How much has customer C003 spent in total? Use the available tool.")

            await waiter.wait()

    return 0
