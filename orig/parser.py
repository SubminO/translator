import binascii
import struct
from datetime import datetime


def parse(fmt, binary, offset=0):
    '''
    Unpack the string

    fmt      @see https://docs.python.org/2/library/struct.html#format-strings
    value    value to be formated
    offset   offset in bytes from begining
    '''
    parsed = struct.unpack_from(fmt, binary, offset)
    return parsed[0] if len(parsed) == 1 else parsed


def parse_packet(packet):
    '''
    Parse Wialon Retranslator v1.0 packet w/o first 4 bytes (packet size)
    '''
    # parsed message
    message = {
        'uid': 0,
        'params': {},
    }

    # parse packet info
    controller_id_size = packet.find(b'\x00', 4) - 4
    (message['uid'], time, _) = parse('> %ds x i i' % controller_id_size, packet, 4)

    message['uid'] = message['uid'].decode('utf-8') if isinstance(message['uid'], bytes) else message['uid']
    message['datetime'] = datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')

    # get data block
    # 4 bytes of packet size + controller_id_size + 4 bytes of time + 4 bytes of flags + zero byte
    # Look http://extapi.wialon.com/hw/cfg/WialonRetranslator%201.0_en.pdf for details
    data_blocks = packet[4 + controller_id_size + 4 + 4 + 1:]

    while len(data_blocks):
        # name offset in data block
        offset = 2 + 4 + 1 + 1
        name_size = data_blocks.find(b'\x00', offset) - offset
        (block_type, block_length, visible, data_type, name) = parse('> h i b b %ds' % name_size, data_blocks)

        name = name.decode('utf-8') if isinstance(name, bytes) else name

        # constuct block info
        block = {'type': block_type, 'length': block_length, 'visibility': visible, 'data_type': data_type,
                 'name': name, 'data_block': data_blocks[offset + name_size + 1:block_length * 1 + 6]}

        v = ''
        if data_type == 1:
            # text
            v = parse('%ds', block['data_block'])
        if data_type == 2:
            # binary
            if name == 'posinfo':
                v = {
                    'longitude': 0,
                    'latitude': 0,
                    'altitude': 0,
                    'speed': 0,
                    'course': 0,
                    'satellites': 0,
                }
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
        message['params'][name] = v

        # delete parsed info
        data_blocks = data_blocks[block_length + 6:]

    return message


if __name__ == '__main__':
    # test data
    data = [
        '333533393736303133343435343835004B0BFB70000000030BBB000000270102706F73696E666F00A027AFDF5D9848403AC7253383DD4B400000000000805A40003601460B0BBB0000001200047077725F657874002B8716D9CE973B400BBB00000011010361766C5F696E707574730000000001',
        '73686d6900552d3f49000000070bbb000000270102706f73696e666f001f090e42538d3b40af8c20a82dfc4a400000000000000000006c0109ff0bbb0000000f000461646331000000000000ca21400bbb00000011010361766c5f696e7075747300000000240bbb00000012010361766c5f6f7574707574730000000037',
        '74000000333533393736303133343435343835004B0BFB70000000030BBB000000270102706F73696E666F00A027AFDF5D9848403AC7253383DD4B400000000000805A40003601460B0BBB0000001200047077725F657874002B8716D9CE973B400BBB00000011010361766C5F696E707574730000000001',
    ]
    for i in range(len(data)):
        print('\nParse packet: %s\n' % data[i])
        # print(binascii.unhexlify(data[i]))
        print(parse_packet(binascii.unhexlify(data[i])))
