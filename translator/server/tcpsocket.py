import json

from parser import parse


class Server:
    def __init__(self, parser, ws, debug=False):
        self.parser = parser.parse_packet
        self.debug = debug
        self.ws = ws

    async def handler(self, reader, writer):
        queue = bytes()
        while True:
            data = await reader.read(4096)
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
                messages.append(self.parser(packet))

                # remove packet from queue
                queue = queue[packet_size + 4:]
                if len(queue) <= 4:
                    break

                packet_size = parse('<I', queue)

            # on_message(messages, client)
            tracks_json = json.dumps(messages)

            if self.debug:
                print(f"Wialon package parsed to {tracks_json}")

            await self.ws.send(tracks_json)

            writer.write(b"\x11")
