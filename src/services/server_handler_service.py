from __future__ import annotations

import logging
import socket
import threading
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

from PySide6.QtCore import QObject, Signal, Slot

from src.models.api_response import ApiResponse
from src.models.print_request import PrintRequest


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ApiEndpoint:
    display_url: str
    host: str
    port: int
    path: str


class ServerHandlerService(QObject):
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
            logger.info("API server start requested while already running at %s", self._url)
            return
        try:
            endpoint = self._parse_endpoint(url)
            self._assert_port_available(endpoint.host, endpoint.port)
            app = self._create_app(endpoint.path)
            self._server = self._create_uvicorn_server(app, endpoint.host, endpoint.port)
        except Exception as exc:
            logger.exception("Failed to start API server for url=%s", url)
            self.failed.emit(f"Kh\u00f4ng th\u1ec3 kh\u1edfi \u0111\u1ed9ng m\u00e1y ch\u1ee7 API: {exc}")
            return

        self._url = endpoint.display_url
        self._running = True
        logger.info(
            "Starting API server at %s (host=%s, port=%s, path=%s)",
            endpoint.display_url,
            endpoint.host,
            endpoint.port,
            endpoint.path,
        )
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
                logger.info("API server stop requested while not running")
                return
            server = self._server
            thread = self._thread
            self._running = False
            if server is not None:
                server.should_exit = True
            logger.info("Stopping API server at %s", self._url)
        if thread is not None and thread.is_alive():
            thread.join(timeout=3)
        self._server = None
        self._thread = None
        logger.info("API server stopped")
        self.stopped.emit()

    def request_stop(self) -> None:
        self.stop()

    def _run_server(self) -> None:
        try:
            if self._server is not None:
                logger.info("API server thread started")
                self._server.run()
        except Exception as exc:
            self._running = False
            logger.exception("API server stopped unexpectedly")
            self.failed.emit(f"M\u00e1y ch\u1ee7 API d\u1eebng b\u1ea5t th\u01b0\u1eddng: {exc}")
        finally:
            self._running = False
            logger.info("API server thread finished")

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
            logger.info("Health check request processed")
            return PlainTextResponse("San sang")

        @app.options(path)
        async def preflight() -> Response:
            return Response(status_code=204)

        @app.post(path)
        async def print_labels(body: Any = Body(...)) -> JSONResponse:
            try:
                print_request = self._parse_print_request(body)
                logger.info(
                    "Print request accepted with %s label(s)",
                    len(print_request.labels),
                )
                self.print_request_received.emit(print_request)
                self.request_processed.emit("200 OK", True)
                return JSONResponse(
                    ApiResponse(
                        success=True,
                        message="Da nhan lenh in",
                    ).to_dict()
                )
            except Exception as exc:
                logger.exception("Print request rejected")
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
        logger.debug("Parsed print request with %s label(s)", len(print_request.labels))
        if not print_request.labels:
            raise ValueError("Request body ph\u1ea3i c\u00f3 \u00edt nh\u1ea5t m\u1ed9t tem.")
        for index, label in enumerate(print_request.labels):
            if not isinstance(label, dict):
                raise ValueError(f"Tem t\u1ea1i index {index} ph\u1ea3i l\u00e0 object.")
            for key, value in label.items():
                if not isinstance(key, str):
                    raise ValueError(f"Tem t\u1ea1i index {index} c\u00f3 t\u00ean field kh\u00f4ng ph\u1ea3i string.")
                if value is not None and not isinstance(value, (str, dict, list)):
                    label[key] = str(value)
        return print_request

    def _parse_endpoint(self, url: str) -> ApiEndpoint:
        normalized_url = (url or "").strip()
        if not normalized_url:
            raise ValueError("URL API \u0111ang tr\u1ed1ng.")
        if not normalized_url.endswith("/"):
            normalized_url += "/"
        parsed = urlparse(normalized_url)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError("URL API ph\u1ea3i b\u1eaft \u0111\u1ea7u b\u1eb1ng http:// ho\u1eb7c https://.")
        if parsed.scheme == "https":
            raise ValueError("M\u00e1y ch\u1ee7 API local ch\u01b0a h\u1ed7 tr\u1ee3 HTTPS.")
        if not parsed.hostname:
            raise ValueError("URL API ph\u1ea3i c\u00f3 host.")
        if parsed.port is None:
            raise ValueError("URL API ph\u1ea3i c\u00f3 port.")

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
                raise ValueError(f"Port {port} kh\u00f4ng kh\u1ea3 d\u1ee5ng tr\u00ean {host}.") from exc
