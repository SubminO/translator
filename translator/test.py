#!/usr/bin/env python

import argparse


if __name__ == "__main__":
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('-r', '--proto', action='append', metavar=('proto port'),
                             nargs=2, help='Declare pairs of protocol:port', required=True)
    args_parser.add_argument('-l', '--listen', default='127.0.0.1', help='IP address for websocket ws')
    args_parser.add_argument('-p', '--port', default=8080, help='Port for websocket ws')

    proto = args_parser.parse_args().proto
    listen = args_parser.parse_args().listen
    port = args_parser.parse_args().port
    print(proto, listen, port)
