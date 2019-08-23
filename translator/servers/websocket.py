import json
from websockets.server import WebSocketServerProtocol

class Server:
    """
    Websocket servers handler
    """
    def __init__(self):
        self.clients = set()

    async def send(self, message: str):
        for client in self.clients:
            await client.send(message)

    async def get_status(self, message: str):
        return json.loads(message).get('status')

    async def handler(self, websocket: WebSocketServerProtocol, path: str):
        # Register new websocket client connection
        self.clients.add(websocket)

        # Iteration terminates when the client disconnects like
        # https://websockets.readthedocs.io/en/stable/intro.html#consumer
        async for message in websocket:
            status = await self.get_status(message)
            if status == 'closed':
                break

        # Unregister websocket client connection on close it
        self.clients.remove(websocket)
