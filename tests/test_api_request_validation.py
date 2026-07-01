from __future__ import annotations

import asyncio
import json

from src.core.errors import PrintRequestError
from src.services.server_handler_service import ServerHandlerService


def post_json(app, body: object | str):
    if isinstance(body, str):
        payload = body.encode("utf-8")
    else:
        payload = json.dumps(body).encode("utf-8")

    async def call_app():
        messages = []
        request_sent = False

        async def receive():
            nonlocal request_sent
            if request_sent:
                return {"type": "http.disconnect"}
            request_sent = True
            return {"type": "http.request", "body": payload, "more_body": False}

        async def send(message):
            messages.append(message)

        await app(
            {
                "type": "http",
                "asgi": {"version": "3.0"},
                "method": "POST",
                "path": "/print/",
                "raw_path": b"/print/",
                "query_string": b"",
                "headers": [(b"content-type", b"application/json")],
                "client": ("127.0.0.1", 12345),
                "server": ("testserver", 80),
                "scheme": "http",
            },
            receive,
            send,
        )
        return messages

    messages = asyncio.run(call_app())
    start = next(message for message in messages if message["type"] == "http.response.start")
    body_bytes = b"".join(
        message.get("body", b"")
        for message in messages
        if message["type"] == "http.response.body"
    )
    return start["status"], json.loads(body_bytes.decode("utf-8"))


def test_api_rejects_malformed_json():
    service = ServerHandlerService()
    app = service._create_app("/print/")
    processed = []

    service.request_processed.connect(
        lambda status, success: processed.append((status, success))
    )

    status_code, response_body = post_json(app, "{")

    assert status_code == 400
    assert response_body["success"] is False
    assert processed == [("400 Bad Request", False)]


def test_api_rejects_non_array_labels():
    service = ServerHandlerService()
    app = service._create_app("/print/")
    received = []

    service.print_request_received.connect(received.append)

    status_code, response_body = post_json(app, {"labels": {"remarks": "Mau_02"}})

    assert status_code == 400
    assert response_body["success"] is False
    assert received == []


def test_api_rejects_unknown_remarks_before_emitting_print_request():
    def validate_request(request):
        raise PrintRequestError("Tem tại index 0 phải có remarks là Mau_01 hoặc Mau_02.")

    service = ServerHandlerService(request_validator=validate_request)
    app = service._create_app("/print/")
    received = []

    service.print_request_received.connect(received.append)

    status_code, response_body = post_json(app, [{"remarks": "Mau_99"}])

    assert status_code == 400
    assert response_body == {
        "success": False,
        "message": "Tem tại index 0 phải có remarks là Mau_01 hoặc Mau_02.",
    }
    assert received == []


def test_api_accepts_valid_request_after_validator_passes():
    service = ServerHandlerService(request_validator=lambda request: None)
    app = service._create_app("/print/")
    received = []

    service.print_request_received.connect(received.append)

    status_code, response_body = post_json(app, [{"remarks": "Mau_02"}])

    assert status_code == 200
    assert response_body == {"success": True, "message": "Da nhan lenh in"}
    assert len(received) == 1
    assert received[0].labels == [{"remarks": "Mau_02"}]
