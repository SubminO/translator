from datetime import datetime

from parser import parse


class Parser:
    """
    Парсер виалон пакетов. По сути обернутый в класс гист парсера
    https://gist.github.com/ashmigelski/21cdcb369f55444c4f26
    """
    def parse_packet(self, packet):
        '''
        Parse Wialon Retranslator v1.0 packet w/o first 4 bytes (packet size)
        '''
        # parsed message with undefined content
        message = {}

        # parse packet info
        controller_id_size = packet.find(b'\x00')
        # flags - зарезервировано для расширения парсера в будущем
        (uid, message['time'], flags) = parse('> %ds x i i' % controller_id_size, packet)

        message['uid'] = uid.decode('utf-8') if isinstance(uid, bytes) else uid
        message['datetime'] = datetime.fromtimestamp(message['time']).strftime('%Y-%m-%d %H:%M:%S')

        # get data block
        # controller_id_size + 4 bytes of time + 4 bytes of flags + zero byte
        # Look http://extapi.wialon.com/hw/cfg/WialonRetranslator%201.0_en.pdf for details
        data_blocks = packet[controller_id_size + 1 + 4 + 4:]

        while len(data_blocks):
            # name offset in data block
            offset = 2 + 4 + 1 + 1
            name_size = data_blocks.find(b'\x00', offset) - offset
            (block_type, block_length, visible, data_type, name) = parse('> h i b b %ds' % name_size, data_blocks)

            name = name.decode('utf-8') if isinstance(name, bytes) else name

            # constuct data block
            data_block = data_blocks[offset + name_size + 1:block_length * 1 + 6]

            value = None
            if data_type == 1:
                # text
                value = data_block[:data_block.find(b'\x00')].decode('utf-8')
            elif data_type == 2:
                # binary
                if name == 'posinfo':
                    value = {}
                    (value['longitude'], value['latitude'], value['altitude']) = parse('d d d', data_block)
                    (value['speed'], value['course'], value['satellites']) = parse('> h h b', data_block, 24)
            elif data_type == 3:
                # integer
                value = parse('> i', data_block)
            elif data_type == 4:
                # float
                value = parse('d', data_block)
            elif data_type == 5:
                # long
                value = parse('> q', data_block)

            # add param to message
            message[name] = value

            # delete parsed info
            data_blocks = data_blocks[block_length + 6:]

        return message
