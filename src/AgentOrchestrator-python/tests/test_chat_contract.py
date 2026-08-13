"""Contract tests for the chat request payload.

These exist because of a real bug: the browser UI posted ``{"message": ...}``
while :class:`~app.routers.chat.ChatRequest` declares ``prompt``. Pydantic
ignores unknown keys by default, so the request succeeded, the prompt arrived
empty, and the model answered with a generic greeting. Nothing failed loudly.

The UI is static JavaScript, so the only way to keep it honest is to assert the
field name it sends is the field name the model actually reads.
"""

import json
import re
from pathlib import Path

from app.routers.chat import ChatRequest

APP_JS = Path(__file__).resolve().parents[1] / "app" / "static" / "app.js"


def test_chat_request_reads_prompt_not_message():
    """``prompt`` is the field; ``message`` must not silently become one."""
    parsed = ChatRequest.model_validate({"prompt": "hello"})
    assert parsed.prompt == "hello"

    # The bug in miniature: an unknown key is dropped rather than rejected.
    assert ChatRequest.model_validate({"message": "hello"}).prompt is None


def test_chat_request_accepts_camel_case_alias():
    """The API speaks camelCase on the wire, matching the .NET contract."""
    parsed = ChatRequest.model_validate({"prompt": "hi", "systemMessage": "be brief"})
    assert parsed.system_message == "be brief"


def test_web_ui_posts_the_field_the_api_reads():
    """Guards the exact regression: app.js must post ``prompt``."""
    source = APP_JS.read_text(encoding="utf-8")

    bodies = re.findall(r"body:\s*JSON\.stringify\((\{.*?\})\)", source, re.S)
    assert bodies, "no JSON.stringify request body found in app.js"

    for body in bodies:
        keys = set(re.findall(r"(\w+)\s*:", body)) | set(
            re.findall(r"\{\s*(\w+)\s*[,}]", body)  # shorthand, e.g. { prompt, model }
        )
        assert "message" not in keys, (
            f"app.js posts 'message', but ChatRequest declares 'prompt'. "
            f"Pydantic drops the unknown key and the model receives nothing. Body: {body}"
        )
        assert "prompt" in keys, f"app.js request body is missing 'prompt'. Body: {body}"

        unknown = keys - set(ChatRequest.model_fields) - {"systemMessage"}
        assert not unknown, f"app.js sends field(s) the API ignores: {sorted(unknown)}"


def test_sse_frames_are_parseable_json():
    """Documents the SSE wire format the labs teach: ``data: {json}`` then ``[DONE]``."""
    frame = f"data: {json.dumps({'content': 'streaming works'})}\n\n"
    assert frame.startswith("data: ")
    assert json.loads(frame[len("data: ") :].strip()) == {"content": "streaming works"}
