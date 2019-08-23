#!/usr/bin/env python

import argparse
import asyncio
import websockets
from servers import websocket, tcpsocket


if __name__ == "__main__":
    args_parser = argparse.ArgumentParser()

    args_parser.add_argument('-r', '--proto', action='append', metavar=('proto port'),
                             nargs=2, help='Declare pairs of protocol:port', required=True)
    args_parser.add_argument('-l', '--addr', default='127.0.0.1', help='IP address for protocols serving')
    args_parser.add_argument('-w', '--wsaddr', default='127.0.0.1', help='IP address for websocket ws')
    args_parser.add_argument('-p', '--wsport', default=8080, help='Port for websocket ws')

    args = args_parser.parse_args()


    parsers = {for proto, port in args.proto}

    loop = asyncio.get_event_loop()

    wssrv = websocket.Server()

    websocket = websockets.serve(wssrv.handler, args.wsaddr, args.wsport)
    loop.run_until_complete(websocket)

    for proto, port in args.proto:
        tcpsrv = tcpsocket.Server(port, proto, args.addr)
        loop.run_until_complete(tcpsrv.handler())

    loop.run_forever()
