import socket
from typing import Any

from .buffer import Buffer
from .connection import Connection
from .exceptions import PyQ3SLError


class Server:
    ip: str
    port: int

    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port


    def __repr__(self):
        return f'{self.ip}:{self.port}'

    def __iter__(self):
        yield 'ip', self.ip
        yield 'port', self.port

    def __eq__(self, other: Any):
        return isinstance(other, type(self)) and \
            other.ip == self.ip and \
            other.port == self.port

    def get_status(self, strip_colors: bool = True, timeout: float = 1.0):
        connection = Connection(self.ip, self.port, socket.SOCK_DGRAM, timeout)

        packet = self.build_query_packet()

        connection.write(packet)
        result = connection.read()
        return self.parse_response(result, strip_colors)

    def parse_response(self, buffer: Buffer, strip_colors: bool) -> dict:
        """
        Response should consist of at least three lines:
        1: header indicating response type
        2: list of server variables, delimited by \
        3+: lines containing player info (final player line being empty)
        """
        # Make sure header indicates status response as type
        if not self.has_valid_response_header(buffer):
            raise PyQ3SLError('Server returned invalid packet header')

        # Make sure body starts with "\" indicating the first variable and contains an even number of keys and values
        if not self.has_valid_response_body(buffer):
            raise PyQ3SLError('Server returned invalid packet body')

        # Parse variable keys and values
        i = 0
        keys = []
        values = []
        while buffer.peek(1) == b'\\':
            """
            Skip the \\ indicating the start of the key/value and use
            a) all bytes until the next separator (anything but the last value
            or
            b) all bytes until the next linebreak (last value)
            as the key/value
            """
            buffer.skip(1)
            element = buffer.read_string([b'\\', b'\n'], strip_colors=strip_colors)
            if i % 2 == 0:
                keys.append(element)
            else:
                values.append(element)

            i += 1

        players = []
        # A player with 0 frags, 0 ping and an empty name would take up 7 bytes plus the line break
        while buffer.peek(1) == b'\n' and buffer.has(8):
            player = self.parse_player(buffer, strip_colors)
            players.append(player)

        return {
            'ip': self.ip,
            'port': self.port,
            **dict(zip(keys, values)),
            'players': players
        }

    @staticmethod
    def build_query_packet() -> bytes:
        return b'\xff\xff\xff\xffgetstatus\x00'

    @staticmethod
    def has_valid_response_header(buffer: Buffer) -> bool:
        return buffer.has(19) and buffer.read(19) == b'\xff\xff\xff\xffstatusResponse\n'

    @staticmethod
    def has_valid_response_body(buffer: Buffer) -> bool:
        return buffer.peek(1) == b'\\' and buffer.get_buffer().count(b'\\') % 2 == 0

    @staticmethod
    def parse_player(buffer: Buffer, strip_colors: bool) -> dict:
        frags = int(buffer.read_string(b' ', consume_sep=True, strip_colors=strip_colors))
        ping = int(buffer.read_string(b' ', consume_sep=True, strip_colors=strip_colors))
        buffer.skip(1)
        name = buffer.read_string(b'"', consume_sep=True, strip_colors=strip_colors)

        return {
            'frags': frags,
            'ping': ping,
            'name': name,
        }


class MedalOfHonorServer(Server):
    """
    Medal of Honor uses a custom Quake3 protocol variant with some key differences, making it incompatible with the
    "vanilla" protocol. Since all the Medal of Honor games use GameSpy to list servers, Medal of Honor servers can only
    be created directly.
    """
    def __init__(self, ip: str, port: int):
        super().__init__(ip, port)

    @staticmethod
    def build_query_packet() -> bytes:
        # Medal of Honor uses a slightly different query packet
        return b'\xff\xff\xff\xff\x02getstatus xxx\x00'

    @staticmethod
    def has_valid_response_header(buffer: Buffer) -> bool:
        # Medal of Honor responses contain an extra byte (b'\x01')
        return buffer.has(20) and buffer.read(20) == b'\xff\xff\xff\xff\x01statusResponse\n'

    @staticmethod
    def parse_player(buffer: Buffer, strip_colors: bool) -> dict:
        # Medal of Honor only sends a player's ping and name (seems like colors are not supported)
        ping = int(buffer.read_string(b' ', consume_sep=True, strip_colors=strip_colors))
        buffer.skip(1)
        name = buffer.read_string(b'"', consume_sep=True, strip_colors=strip_colors)

        return {
            'ping': ping,
            'name': name,
        }
