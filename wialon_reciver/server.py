# -*- coding: utf-8 -*-
# import redis
import binascii
import pytz
import socket
import os
import json
import requests
import threading

# from lxml import etree
from datetime import datetime, timedelta

from wialon_parser import parse, parsePacket


# redis_tracks = redis.StrictRedis(host='redis', port=6379, db=0)
# redis_data_count = redis.StrictRedis(host='redis', port=6379, db=1)


def on_new_client(sck, addr, client):
    queue = ''
    while True:
        data = sck.recv(1024)
        if not data:
            break
        # append to queue
        queue = queue + data
        messages = []
        # get first packet size
        packet_size = parse('<i', queue)
        while packet_size + 4 <= len(queue):
            # get packet
            packet = queue[4:packet_size + 4]
            messages.append(parsePacket(packet))
            # remove packet from queue
            queue = queue[packet_size + 4:]
            if len(queue) <= 4:
                break
            packet_size = parse('<i', queue)

            # packet was received successfully
        on_message(messages, client)
        sck.send(str(0x11))
    sck.close()


def on_message(messages, client):
    tracks = {}
    tracks['tracks'] = []
    # tracks = etree.Element('tracks')
    # tracks.set('clid', 'balakovo')
    for message in messages:
        # try:
        # route = redis_tracks.get(message['id']).decode('utf-8')
        # except:
        #     print('Автобус UID=' + message['id'] + ', не имеет заданного маршрута')
        #     print(addr)
        #     return

        print('Пришли данные: UID = ' + message['id'])

        # Счетчик входящих данных
        # redis_data_count.incr(message['id'])

        if 'posinfo' in message['params']:
            try:
                # TODO: Check if uuid in (tracks = [track['uuid']])
                # track = tracks.findall('track[@uuid="' + message['id'] + '"]')[0]
                track = [t for t in tracks['tracks'] if t['track']['uuid'] == message['id']][0]
            except:
                track = {'track': {'points': []}}
                # track.set('route', '5')
                # track.set('route', route)

            bus_time = datetime.fromtimestamp(int(message['time']), tz=pytz.timezone('Europe/Samara')).astimezone(
                pytz.utc)
            point = {'latitude': str(message['params']['posinfo']['lat']),
                     'longitude': str(message['params']['posinfo']['lon']),
                     'avg_speed': str(message['params']['posinfo']['s']),
                     'direction': str(message['params']['posinfo']['c']),
                     'time': bus_time.strftime("%d%m%Y:%H%M%S")}
            # point.set('time', time.strftime("%d%m%Y:%H%M%S", time.gmtime()))
            # bus_time = midnight + timedelta(seconds=int(key['time']))

            track['track']['points'].append(point)
            tracks['tracks'].append(track)

    tracks_json = json.dumps(tracks)
    if client:
        client.send(tracks_json)
    # TODO: Send to unix and web socket


CONNECTION = ('0.0.0.0', 724)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# prevent 'ERROR: Address already in use'
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind(CONNECTION)
server.listen(1)

# socket server for unix serialized data
# if os.path.exists("/tmp/test.sock"):
#     os.remove("/tmp/test.sock")
# unix_server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
# unix_server.bind("/tmp/test.sock")
# unix_server.listen(1)

# unix socket_client
if os.path.exists("/tmp/test.sock"):
    client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    client.connect("/tmp/test.sock")
else:
    client = None

print("Listen {0} on {1}".format(*CONNECTION))

while True:
    sck, addr = server.accept()
    print("Connected {0}:{1}".format(*addr))
    my_thread = threading.Thread(target=on_new_client, args=(sck, addr, client, ))
    my_thread.start()
sck.close()
