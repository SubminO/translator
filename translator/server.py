#!/usr/bin/env python

import argparse
import asyncio
import websockets
from servers import websocket, tcpsocket
from parser import parser_factory
from error import ParserFactoryCreationError


if __name__ == "__main__":
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('-r', '--proto', action='append', metavar=('proto port'),
                             nargs=2, help='Declare pairs of protocol:port', required=True)
    args_parser.add_argument('-l', '--addr', default='127.0.0.1', help='IP address for protocols serving')
    args_parser.add_argument('-w', '--wsaddr', default='127.0.0.1', help='IP address for websocket ws')
    args_parser.add_argument('-p', '--wsport', default=8080, help='Port for websocket ws')
    args_parser.add_argument('-d', '--debug', action='store_true', help='Debug mode turn on')

    args = args_parser.parse_args()

    wssrv = websocket.Server(debug=args.debug)

    loop = asyncio.get_event_loop()

    tasks = [
        websockets.serve(wssrv.handler, args.wsaddr, args.wsport)
    ]

    try:
        for proto, parser, port in [(proto, parser_factory(proto), port) for proto, port in args.proto]:
            tasks.append(asyncio.start_server(tcpsocket.Server(parser, wssrv).handler, args.addr, port))
            print(f"Start {proto} parser on {args.addr}:{port}")

        loop.run_until_complete(asyncio.wait(tasks))
        loop.run_forever()
    except KeyboardInterrupt:
        print("Keyboard interrupt signal accepted. Stopping")
    except (ParserFactoryCreationError, Exception) as e:
        print(e)

    loop.close()