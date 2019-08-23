import asyncio
import json
from typing import Optional
from error import ServerProtocolError
from parser import parse


class Server:

    def __init__(self, port: int, proto: str, addr: Optional[str] = '127.0.0.1'):
        if proto not  in self._protocols:
            raise ServerProtocolError()

        self._proto = {(protocol, port) for protocol, port in proto if protocol in self._protocols }

    async def serve(self, protocol, srv_port):
        pass

    async def handler(self, reader, _, ws):
        data = await reader.read(1024)
        message = data.decode()
#
#     addr = writer.get_extra_info('peername')
#
#     print(f"Received {message!r} from {addr!r}")
#
#     print(f"Send: {message!r}")
#     writer.write(data)
#     await writer.drain()
#
#     print("Close the ws")
#     writer.close()
#
# async def main():
#     servers = await asyncio.start_server(
#         handle_echo, '127.0.0.1', 8888)
#
#     async with servers:
#         await servers.serve_forever()
#
# asyncio.run(main())
