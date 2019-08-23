import struct
import importlib


def parser_factory(proto):
    try:
        return importlib.import_module(f"parser.{proto}").Parser()
    except ModuleNotFoundError as e:
        raise ParserFactoryCreationError(e)



def parse(fmt, binary, offset=0):
    '''
    Unpack the string

    fmt      @see https://docs.python.org/2/library/struct.html#format-strings
    value    value to be formated
    offset   offset in bytes from begining
    '''
    parsed = struct.unpack_from(fmt, binary, offset)
    return parsed[0] if len(parsed) == 1 else parsed
