# -*- coding: utf-8 -*-
# import redis
# import binascii
# import pytz
import socket
# import os
import json
# import requests
import threading
from websocket_server import WebsocketServer
# import websocket
# from simple_websocket_server import WebSocketServer, WebSocket
import logging

# from lxml import etree
# from datetime import datetime, timedelta

from wialon_parser import parse, parsePacket


# redis_tracks = redis.StrictRedis(host='redis', port=6379, db=0)
# redis_data_count = redis.StrictRedis(host='redis', port=6379, db=1)


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

            # packet was received successfully

        # on_message(messages, client)
        tracks_json = json.dumps(messages)

        print(tracks_json)

        wsserver.send_message_to_all(tracks_json)

        sck.send(str(0x11))

    sck.close()


CONNECTION = ('0.0.0.0', 20163)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# prevent 'ERROR: Address already in use'
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind(CONNECTION)
server.listen(1)

# wsserver = WebsocketServer(8091, host='0.0.0.0')
wsserver = WebsocketServer(8091, host='0.0.0.0', loglevel=logging.INFO)
# wsserver.set_fn_new_client(new_client)
wsserver.run_forever()

print("Listen {0} on {1}".format(*CONNECTION))

sck = None

while True:
    sck, addr = server.accept()
    print("Connected {0}:{1}".format(*addr))
    my_thread = threading.Thread(target=on_new_client, args=(sck, addr, wsserver,))
    my_thread.start()

sck.close()
