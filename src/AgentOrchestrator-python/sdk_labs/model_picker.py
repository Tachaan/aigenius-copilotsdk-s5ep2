"""Chooses a model from the caller's account instead of assuming every reader
has access to the same preview model.

Mirrors ``samples/SdkLabs/ModelPicker.cs``.
"""

from copilot import CopilotClient, ModelInfo

PREFERRED_MODEL_IDS = [
    "claude-haiku-4.5",
    "gpt-5-mini",
    "gpt-5.4-mini",
    "gpt-5",
    "gpt-4.1",
]


async def pick(client: CopilotClient, requested_model_id: str | None) -> str | None:
    models: list[ModelInfo]

    try:
        models = list(await client.list_models())
    except Exception as ex:  # noqa: BLE001 - any listing failure is non-fatal here
        if requested_model_id:
            print(f"Could not list available models to validate '{requested_model_id}': {ex}")
            print(f"Using requested model without validation: {requested_model_id}")
            print(f"Model: {requested_model_id}")
            return requested_model_id

        print(f"Could not list available models: {ex}")
        print("Pass --model <id> to choose a model explicitly, or try again later.")
        return None

    if not models:
        if requested_model_id:
            print(
                "No available models were returned; using the requested model without validation."
            )
            print(f"Model: {requested_model_id}")
            return requested_model_id

        print("No available models were returned for this account.")
        print("Pass --model <id> to choose a model explicitly, or check your Copilot access.")
        return None

    available = [m for m in models if m.id]

    if requested_model_id:
        requested = next(
            (m for m in available if m.id.casefold() == requested_model_id.casefold()), None
        )
        if requested is not None:
            print(f"Model: {requested.id}")
            return requested.id

    selected = next(
        (
            m
            for preferred in PREFERRED_MODEL_IDS
            for m in available
            if m.id.casefold() == preferred.casefold()
        ),
        None,
    ) or next((m for m in available if m.id.casefold() != "auto"), None)

    if selected is None:
        print(
            "Only the automatic model selector was returned; "
            "choose a concrete model with --model <id>."
        )
        return None

    if requested_model_id:
        print(
            f"Requested model '{requested_model_id}' is unavailable; using '{selected.id}' instead."
        )
    elif selected.id.casefold() != PREFERRED_MODEL_IDS[0].casefold():
        print(
            f"Preferred model '{PREFERRED_MODEL_IDS[0]}' is unavailable; "
            f"using '{selected.id}' instead."
        )

    print(f"Model: {selected.id}")
    return selected.id
