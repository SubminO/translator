import json
from json.decoder import JSONDecodeError
from websockets.server import WebSocketServerProtocol


class Server:
    """
    Websocket server handler
    """
    def __init__(self, debug=False):
        self.debug = debug
        self.clients = set()

    async def send(self, message: str):
        for client in self.clients:
            if self.debug:
                print(f"To client {client.remote_address} Send message {message}")

            await client.send(message)

    async def get_status(self, message: str):
        data = {}

        try:
            data = json.loads(message)
        except JSONDecodeError:
            if self.debug:
                print("Error on getting status")

        return data.get('status')

    async def handler(self, websocket: WebSocketServerProtocol, path: str):
        # Register new websocket client connection
        self.clients.add(websocket)
        print(f"Accept new client connection from {websocket.remote_address}")

        # Iteration terminates when the client disconnects like
        # https://websockets.readthedocs.io/en/stable/intro.html#consumer
        async for message in websocket:
            if self.debug:
                print(f"Accept from {websocket.remote_address} message {message}")

            status = await self.get_status(message)
            if status == 'closed':
                break

        # Unregister websocket client connection on close it
        print(f"Remote connection closed {websocket.remote_address}")
        self.clients.remove(websocket)
