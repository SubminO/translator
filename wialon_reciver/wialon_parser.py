# -*- coding: utf-8 -*-

import struct
from datetime import datetime


def parse(fmt, binary, offset=0):
    """
    Unpack the string

    fmt      @see https://docs.python.org/2/library/struct.html#format-strings
    value    value to be formated
    offset   offset in bytes from begining
    """
    parsed = struct.unpack_from(fmt, binary, offset)
    return parsed[0] if len(parsed) == 1 else parsed


def parsePacket(packet):
    """
    Parse Wialon Retranslator v1.0 packet w/o first 4 bytes (packet size)
    """
    # parsed message
    msg = {
        'uid': 0,
        'time': '',
        'params': {},
    }

    # parse packet info
    controller_id_size = packet.find('\x00')
    (msg['uid'], time, flags) = parse('> %ds x i i' % (controller_id_size), packet)
    msg['time'] = datetime.fromtimestamp(int(time)).strftime("%Y-%m-%d %H:%M:%S")

    # get data block
    data_blocks = packet[controller_id_size + 1 + 4 + 4:]

    while len(data_blocks):
        # name offset in data block
        offset = 2 + 4 + 1 + 1
        name_size = data_blocks.find('\x00', offset) - offset
        (block_type, block_length, visible, data_type, name) = parse('> h i b b %ds' % (name_size), data_blocks)

        # constuct block info
        block = {'type': block_type, 'length': block_length, 'visibility': visible, 'data_type': data_type,
                 'name': name, 'data_block': data_blocks[offset + name_size + 1:block_length * 1 + 6]}

        # get block data
        v = ''
        # todo сделать определение что разбирать на основе flags http://extapi.wialon.com/hw/cfg/WialonRetranslator%201.0.pdf
        if data_type == 1:
            # text
            # TODO
            pass
        if data_type == 2:
            # binary
            if name == 'posinfo':
                v = {}
                (v['longitude'], v['latitude'], v['altitude']) = parse('d d d', block['data_block'])
                (v['speed'], v['course'], v['satellites']) = parse('> h h b', block['data_block'], 24)
        elif data_type == 3:
            # integer
            v = parse('> i', block['data_block'])
        elif data_type == 4:
            # float
            v = parse('d', block['data_block'])
        elif data_type == 5:
            # long
            v = parse('> q', block['data_block'])

        # add param to message
        msg['params'][name] = v

        # delete parsed info
        data_blocks = data_blocks[block_length + 6:]

    return msg
