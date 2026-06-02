from __future__ import annotations

import socket
import threading
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

from PySide6.QtCore import QObject, Signal, Slot

from src.models.api_response import ApiResponse
from src.models.print_request import PrintRequest


@dataclass(frozen=True)
class ApiEndpoint:
    display_url: str
    host: str
    port: int
    path: str


class ApiServerService(QObject):
    """Local FastAPI server that exposes the print endpoint."""

    started = Signal(str)
    stopped = Signal()
    failed = Signal(str)
    request_processed = Signal(str, bool)
    print_request_received = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self._running = False
        self._url = ""
        self._server: Any | None = None
        self._thread: threading.Thread | None = None
        self._stop_lock = threading.Lock()

    @Slot(str)
    def start(self, url: str) -> None:
        if self._running:
            return
        try:
            endpoint = self._parse_endpoint(url)
            self._assert_port_available(endpoint.host, endpoint.port)
            app = self._create_app(endpoint.path)
            self._server = self._create_uvicorn_server(app, endpoint.host, endpoint.port)
        except Exception as exc:
            self.failed.emit(f"Could not start API server: {exc}")
            return

        self._url = endpoint.display_url
        self._running = True
        self._thread = threading.Thread(
            target=self._run_server,
            name="iwms-printer-api",
            daemon=True,
        )
        self._thread.start()
        self.started.emit(endpoint.display_url)

    @Slot()
    def stop(self) -> None:
        with self._stop_lock:
            if not self._running:
                return
            server = self._server
            thread = self._thread
            self._running = False
            if server is not None:
                server.should_exit = True
        if thread is not None and thread.is_alive():
            thread.join(timeout=3)
        self._server = None
        self._thread = None
        self.stopped.emit()

    def request_stop(self) -> None:
        self.stop()

    def _run_server(self) -> None:
        try:
            if self._server is not None:
                self._server.run()
        except Exception as exc:
            self._running = False
            self.failed.emit(f"API server stopped unexpectedly: {exc}")
        finally:
            self._running = False

    def _create_app(self, path: str) -> Any:
        from fastapi import Body, FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.responses import JSONResponse, PlainTextResponse, Response

        app = FastAPI(title="iWMS Printer API", docs_url=None, redoc_url=None)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["POST", "OPTIONS"],
            allow_headers=["Content-Type"],
        )

        @app.get(path)
        async def health_check() -> PlainTextResponse:
            return PlainTextResponse("Welcome")

        @app.options(path)
        async def preflight() -> Response:
            return Response(status_code=204)

        @app.post(path)
        async def print_labels(body: Any = Body(...)) -> JSONResponse:
            try:
                print_request = self._parse_print_request(body)
                self.print_request_received.emit(print_request)
                self.request_processed.emit("200 OK", True)
                return JSONResponse(
                    ApiResponse(
                        success=True,
                        message="Print job accepted",
                    ).to_dict()
                )
            except Exception as exc:
                self.request_processed.emit("400 Bad Request", False)
                return JSONResponse(
                    ApiResponse(success=False, message=str(exc)).to_dict(),
                    status_code=400,
                )

        return app

    def _create_uvicorn_server(self, app: Any, host: str, port: int) -> Any:
        import uvicorn

        config = uvicorn.Config(
            app,
            host=host,
            port=port,
            log_level="warning",
            access_log=False,
        )
        return uvicorn.Server(config)

    def _parse_print_request(self, body: Any) -> PrintRequest:
        print_request = PrintRequest.from_compatible_body(body)
        if not print_request.labels:
            raise ValueError("Request body must contain at least one label.")
        for index, label in enumerate(print_request.labels):
            if not isinstance(label, dict):
                raise ValueError(f"Label at index {index} must be an object.")
            for key, value in label.items():
                if not isinstance(key, str):
                    raise ValueError(f"Label at index {index} has a non-string field name.")
                if value is not None and not isinstance(value, str):
                    label[key] = str(value)
        return print_request

    def _parse_endpoint(self, url: str) -> ApiEndpoint:
        normalized_url = (url or "").strip()
        if not normalized_url:
            raise ValueError("API URL is empty.")
        if not normalized_url.endswith("/"):
            normalized_url += "/"
        parsed = urlparse(normalized_url)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError("API URL must start with http:// or https://.")
        if parsed.scheme == "https":
            raise ValueError("HTTPS is not supported by the local API server yet.")
        if not parsed.hostname:
            raise ValueError("API URL must include a host.")
        if parsed.port is None:
            raise ValueError("API URL must include a port.")

        host = parsed.hostname
        bind_host = "0.0.0.0" if host in {"+", "*"} else host
        path = parsed.path or "/"
        if not path.startswith("/"):
            path = f"/{path}"
        return ApiEndpoint(
            display_url=normalized_url,
            host=bind_host,
            port=parsed.port,
            path=path,
        )

    def _assert_port_available(self, host: str, port: int) -> None:
        check_host = "127.0.0.1" if host in {"0.0.0.0", "localhost"} else host
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                probe.bind((check_host, port))
            except OSError as exc:
                raise ValueError(f"Port {port} is not available on {host}.") from exc
