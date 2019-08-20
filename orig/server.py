# -*- coding: utf-8 -*-

import binascii
import socket

from parser import parse, parsePacket

CONNECTION = (socket.gethostname(), 12374)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# prevent 'ERROR: Address already in use'
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


server.bind((socket.gethostname(), 12374))
server.listen(1)

print "Listen {0} on {1}".format(*CONNECTION)
# Accept connections
sck, addr = server.accept()
print "Connected {0}:{1}".format(*addr)

# packet queue
queue = ''

while 1:
    data = sck.recv(1024)
    if not data:
        break
    # append to queue
    queue = queue + data

    # get first packet size
    packet_size = parse('<i', queue)
    if packet_size + 4 <= len(queue):
        # get packet
        packet = queue[4:packet_size + 4]

        # print binascii.hexlify(packet)
        print parsePacket(packet)

        # remove packet from queue
        queue = queue[packet_size + 4:]

        # packet was received successfully
        sck.send(str(0x11))
