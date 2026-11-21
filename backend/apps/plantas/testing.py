"""Small ASGI test client without an HTTP server dependency."""

import json
from asgiref.testing import ApplicationCommunicator


class WebsocketCommunicator(ApplicationCommunicator):
    def __init__(self, application, path, headers=None):
        super().__init__(
            application,
            {
                "type": "websocket",
                "path": path,
                "raw_path": path.encode(),
                "query_string": b"",
                "headers": headers or [],
                "subprotocols": [],
                "scheme": "ws",
                "server": ("localhost", 80),
                "client": ("127.0.0.1", 1234),
            },
        )

    async def connect(self):
        await self.send_input({"type": "websocket.connect"})
        response = await self.receive_output(timeout=2)
        return response["type"] == "websocket.accept", response.get("code")

    async def receive_json_from(self):
        response = await self.receive_output(timeout=2)
        assert response["type"] == "websocket.send"
        return json.loads(response["text"])

    async def disconnect(self):
        await self.send_input({"type": "websocket.disconnect", "code": 1000})
        await self.wait(timeout=2)
