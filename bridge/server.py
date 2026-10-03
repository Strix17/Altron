"""Lightweight standard-library WebSocket bridge server for Altron UI."""

from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import struct
import threading
from collections.abc import Callable
from typing import Any

WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


class BridgeServer:
    """Zero-dependency local WebSocket bridge connecting Python Altron to the modern UI."""

    def __init__(
        self,
        on_submit_text: Callable[[str], None],
        on_listen_mic: Callable[[], None],
        host: str = "127.0.0.1",
        port: int = 8765,
    ) -> None:
        self.on_submit_text = on_submit_text
        self.on_listen_mic = on_listen_mic
        self.host = host
        self.port = port
        self.clients: set[asyncio.StreamWriter] = set()
        self.loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Start the bridge server in a background daemon thread."""
        self._thread = threading.Thread(target=self._run_event_loop, daemon=True, name="Altron-Bridge")
        self._thread.start()

    def _run_event_loop(self) -> None:
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._start_server())
        self.loop.run_forever()

    async def _start_server(self) -> None:
        server = await asyncio.start_server(self._handle_client, self.host, self.port)
        print(f"[ALTRON BRIDGE] Listening on ws://{self.host}:{self.port}")

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            # 1. Read HTTP Upgrade Request
            request = await reader.read(4096)
            headers = request.decode("utf-8", errors="ignore")

            key = None
            for line in headers.split("\r\n"):
                if line.lower().startswith("sec-websocket-key:"):
                    key = line.split(":", 1)[1].strip()
                    break

            if not key:
                writer.close()
                await writer.wait_closed()
                return

            # 2. Complete WebSocket Handshake
            accept_key = base64.b64encode(hashlib.sha1((key + WS_GUID).encode("utf-8")).digest()).decode("utf-8")
            response = (
                "HTTP/1.1 101 Switching Protocols\r\n"
                "Upgrade: websocket\r\n"
                "Connection: Upgrade\r\n"
                f"Sec-WebSocket-Accept: {accept_key}\r\n\r\n"
            )
            writer.write(response.encode("utf-8"))
            await writer.drain()

            self.clients.add(writer)

            # 3. Read Incoming Frames
            while True:
                data = await reader.read(2)
                if not data or len(data) < 2:
                    break

                byte1, byte2 = data[0], data[1]
                opcode = byte1 & 0x0F
                masked = (byte2 & 0x80) != 0
                payload_len = byte2 & 0x7F

                if opcode == 8:  # Close frame
                    break

                if payload_len == 126:
                    extended = await reader.read(2)
                    payload_len = struct.unpack(">H", extended)[0]
                elif payload_len == 127:
                    extended = await reader.read(8)
                    payload_len = struct.unpack(">Q", extended)[0]

                mask_key = await reader.read(4) if masked else b""
                raw_payload = await reader.read(payload_len)

                if masked:
                    unmasked = bytes(b ^ mask_key[i % 4] for i, b in enumerate(raw_payload))
                else:
                    unmasked = raw_payload

                if opcode == 1:  # Text frame
                    text = unmasked.decode("utf-8", errors="ignore")
                    self._dispatch_client_message(text)

        except Exception as e:
            print(f"[BRIDGE] Client connection error: {e}")
        finally:
            self.clients.discard(writer)
            writer.close()

    def _dispatch_client_message(self, message_text: str) -> None:
        try:
            msg = json.loads(message_text)
            msg_type = msg.get("type")
            if msg_type == "submit_text":
                self.on_submit_text(msg.get("text", ""))
            elif msg_type == "listen_mic":
                self.on_listen_mic()
        except Exception as e:
            print(f"[BRIDGE] Error dispatching client message: {e}")

    def broadcast(self, message: dict[str, Any]) -> None:
        """Thread-safe broadcast to all connected UI webviews."""
        if not self.loop or not self.clients:
            return

        payload = json.dumps(message).encode("utf-8")
        frame = self._encode_frame(payload)

        def _send() -> None:
            for writer in list(self.clients):
                try:
                    writer.write(frame)
                    asyncio.create_task(writer.drain())
                except Exception:
                    self.clients.discard(writer)

        self.loop.call_soon_threadsafe(_send)

    @staticmethod
    def _encode_frame(payload: bytes) -> bytes:
        length = len(payload)
        if length <= 125:
            header = struct.pack(">BB", 0x81, length)
        elif length <= 65535:
            header = struct.pack(">BBH", 0x81, 126, length)
        else:
            header = struct.pack(">BBQ", 0x81, 127, length)
        return header + payload
