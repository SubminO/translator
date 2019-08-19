import struct


def parse(fmt, binary, offset=0):
    '''
    Unpack the string

    fmt      @see https://docs.python.org/2/library/struct.html#format-strings
    value    value to be formated
    offset   offset in bytes from begining
    '''
    parsed = struct.unpack_from(fmt, binary, offset)
    return parsed[0] if len(parsed) == 1 else parsed


class Wialon:
    """
    Парсер виалон пакетовю По сути обернутый в класс гист парсера
    https://gist.github.com/ashmigelski/21cdcb369f55444c4f26
    """
    def parse_packet(self, packet):
        '''
        Parse Wialon Retranslator v1.0 packet w/o first 4 bytes (packet size)
        '''

        # parsed message
        message = {
            'id': 0,
            'time': 0,
            'flags': 0,
            'params': {},
            'blocks': []
        }

        # parse packet info
        controller_id_size = packet.find(b'\x00')
        (message['id'], message['time'], message['flags']) = parse('> %ds x i i' % controller_id_size, packet)

        # get data block
        data_blocks = packet[controller_id_size + 1 + 4 + 4:]

        while len(data_blocks):
            # name offset in data block
            offset = 2 + 4 + 1 + 1
            name_size = data_blocks.find(b'\x00', offset) - offset
            (block_type, block_length, visible, data_type, name) = parse('> h i b b %ds' % (name_size), data_blocks)

            # constuct block info
            block = {
                'type': block_type,
                'length': block_length,
                'visibility': visible,
                'data_type': data_type,
                'name': name,
                'data_block': data_blocks[offset + name_size + 1:block_length * 1 + 6]
            }

            v = ''
            if data_type == 1:
                # text
                # TODO
                pass
            if data_type == 2:
                # binary
                if name == 'posinfo':
                    v = {'longitude': 0, 'latitude': 0, 'altitude': 0, 'speed': 0, 'course': 0, 'satellites': 0}
                    (v['lon'], v['lat'], v['h']) = parse('d d d', block['data_block'])
                    (v['s'], v['c'], v['sc']) = parse('> h h b', block['data_block'], 24)
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

            # data blocks parse information
            message['blocks'].append(block)

            # delete parsed info
            data_blocks = data_blocks[block_length + 6:]

        return message
