from __future__ import annotations

import codecs
from encodings import utf_8

from .lang import PyxyTranspiler


def pyxy_decode(input: bytes | memoryview, errors: str = 'strict') -> tuple[str, int]:
    if isinstance(input, memoryview):
        input = bytes(input)

    # First, convert bytes to str. Assumes utf-8.
    decoded = input.decode('utf-8', errors=errors)
    return PyxyTranspiler(decoded).run(), len(decoded)


class PyxyStreamReader(utf_8.StreamReader):
    decode = pyxy_decode


class PyxyIncrementalDecoder(codecs.BufferedIncrementalDecoder):
    def decode(self, input: bytes, final: bool = False) -> str:
        self.buffer += input
        if final:
            decoded, _ = pyxy_decode(self.buffer)
            self.buffer = b''
            return decoded
        else:
            return ''


def search_function(name):
    if name != 'pyxy':
        return None

    import encodings

    utf8 = encodings.search_function('utf8')
    return codecs.CodecInfo(
        name='pyxy',
        encode=utf8.encode,
        decode=pyxy_decode,
        incrementalencoder=utf8.incrementalencoder,
        incrementaldecoder=PyxyIncrementalDecoder,
        streamreader=PyxyStreamReader,
        streamwriter=utf8.streamwriter
    )


codecs.register(search_function)
