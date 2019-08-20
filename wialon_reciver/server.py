# -*- coding: utf-8 -*-

import socket
import json
import threading
from websocket_server import WebsocketServer
from wialon_parser import parse, parsePacket


def on_new_client(sck, addr, wsserver):
    queue = ''
    while True:
        data = sck.recv(1024)
        if not data:
            break

        # append to queue
        queue = queue + data
        messages = []

        # get first packet size
        packet_size = parse('<I', queue)
        while packet_size + 4 <= len(queue):
            # get packet
            packet = queue[4:packet_size + 4]
            messages.append(parsePacket(packet))

            # remove packet from queue
            queue = queue[packet_size + 4:]
            if len(queue) <= 4:
                break

            packet_size = parse('<I', queue)

        # on_message(messages, client)
        tracks_json = json.dumps(messages)

        print(tracks_json)

        wsserver.send_message_to_all(tracks_json)

        sck.send(str(0x11))

    sck.close()


CONNECTION = ('0.0.0.0', 20163)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(CONNECTION)
server.listen(1)

ws_server = WebsocketServer(8091, host='0.0.0.0')
ws_thread = threading.Thread(target=ws_server.run_forever)
ws_thread.start()

print("Listen {0} on {1}".format(*CONNECTION))

sock = None

while True:
    sock, addr = server.accept()
    print("Connected {0}:{1}".format(*addr))
    main_thread = threading.Thread(target=on_new_client, args=(sck, addr, ws_server,))
    main_thread.start()

sock.close()
