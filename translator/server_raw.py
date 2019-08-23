#!/usr/bin/env python

import argparse
import asyncio
import websockets
import json


class ServerError(Exception):
    pass


class ServerProtocolError(ServerError):
    pass


class ServerRegistrationError(ServerError):
    pass


class ServerClientRegistrationError(ServerRegistrationError):
    pass


class Server:
    _protocols = ('wialon', 'egts')

    def __init__(self, proto, ws_addr='127.0.0.1', ws_port=8080, srv_addr='127.0.0.1'):
        self._proto = {(protocol, port) for protocol, port in proto if protocol in self._protocols }
        if not self._proto:
            raise ServerProtocolError()

        self.srvaddr = srv_addr
        self.wsaddr = ws_addr
        self.wsport = ws_port

        self.clients = set()

    async def get_connection_state(self, message):
        data = json.loads(message)
        return False if data.get('state') == 'closed' else True

    # принимает сообщения от клиента
    async def ws_consumer_handler(self, websocket, path):
        # цикл
        async for message in websocket:
            is_closed = await self.get_connection_state(message)
            if is_closed: break

    # отправляет сообщения к4лиентам
    async def ws_producer_handler(self, websocket, path):
        while True:
            message = await self.producer()
            await websocket.send(message)

    async def wshandler(self, websocket, path):
        consumer_task = asyncio.ensure_future(self.ws_consumer_handler(websocket, path))
        producer_task = asyncio.ensure_future(self.ws_producer_handler(websocket, path))
        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()






    async def sent_to_all(self, message):
        for client in self.clients:
            await client.send(message)

    def register(self, ws):
        client = Client(ws)
        self._clients.add(client)

        registered = [c for c in self._clients if c._ws == ws]

        if len(registered) != 1:
            raise ServerClientRegistrationError()

        return registered[0]

    def unregister(self):
        pass

    async def serve(self, protocol, srv_port):
        pass

    def run(self):
        loop = asyncio.get_event_loop()

        websocket = websockets.serve(self.wshandler, self.wsaddr, self.wsport)
        loop.run_until_complete(websocket)

        for protocol, srv_port in self._proto:
            loop.run_until_complete(self.serve(protocol, srv_port))

        loop.run_forever()




# async def handle_echo(reader, writer):
#     data = await reader.read(100)
#     message = data.decode()
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


# def client(self, ws):
#
#
# async def wshandler(self, websock, path, idle=3 * 3600):
#     try:
#         client = self.register(websock)
#
#         while client.active:
#
#     await asyncio.sleep(idle)
#     self._clients.remove(ws)


# import socket
# import json
# import threading
# from websocket_server import WebsocketServer
# from parser.wialon import parse, Wialon
#
#
# def on_new_client(sck, addr, wsserver):
#     queue = ''
#     while True:
#         data = sck.recv(1024)
#         if not data:
#             break
#
#         # append to queue
#         queue = queue + data
#         messages = []
#
#         # get first packet size
#         packet_size = parse('<I', queue)
#         while packet_size + 4 <= len(queue):
#             # get packet
#             packet = queue[4:packet_size + 4]
#             messages.append(parsePacket(packet))
#
#             # remove packet from queue
#             queue = queue[packet_size + 4:]
#             if len(queue) <= 4:
#                 break
#
#             packet_size = parse('<I', queue)
#
#         # on_message(messages, client)
#         tracks_json = json.dumps(messages)
#
#         print(tracks_json)
#
#         wsserver.send_message_to_all(tracks_json)
#
#         sck.send(str(0x11))
#
#     sck.close()
#
#
# CONNECTION = ('0.0.0.0', 20163)
#
# servers = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# servers.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# servers.bind(CONNECTION)
# servers.listen(1)
#
# ws_server = WebsocketServer(8080, host='0.0.0.0')
# ws_thread = threading.Thread(target=ws_server.run_forever)
# ws_thread.start()
#
# print("Listen {0} on {1}".format(*CONNECTION))
#
# sock = None
#
# while True:
#     sock, addr = servers.accept()
#     print("Connected {0}:{1}".format(*addr))
#     main_thread = threading.Thread(target=on_new_client, args=(sck, addr, ws_server,))
#     main_thread.start()
#
# sock.close()


if __name__ == "__main__":
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('-r', '--proto', action='append', metavar=('proto port'),
                             nargs=2, help='Declare pairs of protocol:port', required=True)
    args_parser.add_argument('-l', '--listen', default='127.0.0.1', help='IP address for protocols serving')
    args_parser.add_argument('-w', '--wsaddr', default='127.0.0.1', help='IP address for websocket ws')
    args_parser.add_argument('-p', '--ws_port', default=8080, help='Port for websocket ws')

    server = Server(args_parser.parse_args())