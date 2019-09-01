#!/usr/bin/env python

import argparse
import asyncio
import websockets

from server import websocket, tcpsocket
from parser import parser_factory
from errors import ParserFactoryCreationError


if __name__ == "__main__":
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('-r', '--proto', action='append', metavar=('proto port'),
                             nargs=2, help='Declare pairs of protocol:port', required=True)
    args_parser.add_argument('-l', '--addr', default='127.0.0.1', help='IP address for protocols serving')
    args_parser.add_argument('-w', '--wsaddr', default='127.0.0.1', help='IP address for websocket ws')
    args_parser.add_argument('-p', '--wsport', default=8080, help='Port for websocket ws')
    args_parser.add_argument('-m', '--mode', default='development', help='Run server mode')

    args = args_parser.parse_args()

    if args.mode != 'production':
        debug = False
    else:
        debug = True

    print(f"Server starting '{args.mode}' mode")

    loop = asyncio.get_event_loop()
    wssrv = websocket.Server(debug=debug)
    tasks = [websockets.serve(wssrv.handler, args.wsaddr, args.wsport)]

    print(f"Start websocket server on {args.wsaddr}:{args.wsport}")

    try:
        for proto, parser, port in [(proto, parser_factory(proto), port) for proto, port in args.proto]:
            tasks.append(asyncio.start_server(tcpsocket.Server(parser, wssrv, debug=debug).handler, args.addr, port))
            print(f"Start {proto} parser on {args.addr}:{port}")

        loop.run_until_complete(asyncio.wait(tasks))
        loop.run_forever()
    except KeyboardInterrupt:
        print("Keyboard interrupt signal accepted. Stopping")
    except (ParserFactoryCreationError, Exception) as e:
        print(e)

    loop.close()