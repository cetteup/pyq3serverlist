import re
from typing import Tuple

from .connection import Connection
from .exceptions import PyQ3SLError


class Server:
    ip: str
    port: int
    connection: Connection

    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.connection = Connection(ip, port)

    def __repr__(self):
        return f'{self.ip}:{self.port}'

    def __iter__(self):
        yield 'ip', self.ip
        yield 'port', self.port

    def get_status(self, timeout: float = 1.0):
        self.connection.set_timeout(timeout)

        packet = self.build_query_packet()

        self.connection.write(packet)
        result = self.connection.read()
        return self.parse_response(result)

    def parse_response(self, data: bytes) -> dict:
        """
        Response should consist of at least three lines:
        1: header indicating response type
        2: list of server variables, delimited by \
        3+: lines containing player info (final player line being empty)
        """
        header, body = self.split_packet(data)
        # Make sure header indicates status response as type
        if not self.is_valid_response_header(header):
            raise PyQ3SLError('Server returned invalid packet header')

        # Make sure body starts with "\" indicating the first variable and contains an even number of keys and values
        if not self.is_valid_response_body(body):
            raise PyQ3SLError('Server returned invalid packet body')

        # Parse variable keys and values
        i = 0
        keys = []
        values = []
        while body.startswith(b'\\'):
            """
            Skip the \\ indicating the start of the key/value and use
            a) all bytes until the next separator (anything but the last value
            or
            b) all bytes until the next linebreak (last value)
            as the key/value
            """
            if b'\\' in body[1:]:
                element_end = body.index(b'\\', 1)
            elif b'\n' in body[1:]:
                element_end = body.index(b'\n', 1)
            else:
                # This should never happen
                raise PyQ3SLError('Server returned invalid packet body')

            element = body[1:element_end]
            if i % 2 == 0:
                keys.append(element.decode('latin1'))
            else:
                values.append(self.strip_colors(element.decode('latin1')))

            # Cut used data from body
            body = body[element_end:]
            i += 1

        # Split remaining body into player lines
        lines = body.split(b'\n')
        player_lines = [line for line in lines if line != b'']
        players = []
        for player_line in player_lines:
            player = self.parse_player(player_line)
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
    def split_packet(packet: bytes) -> Tuple[bytes, bytes]:
        """
        Split a query response packet into header and body
        """
        return packet[:19], packet[19:]

    @staticmethod
    def is_valid_response_header(header: bytes) -> bool:
        return header == b'\xff\xff\xff\xffstatusResponse\n'

    @staticmethod
    def is_valid_response_body(body: bytes) -> bool:
        return body.startswith(b'\\') and body.count(b'\\') % 2 == 0

    @staticmethod
    def strip_colors(value: str) -> str:
        return re.sub(r'\^(X.{6}|.)', '', value)

    @staticmethod
    def parse_player(player_data: bytes) -> dict:
        elements = player_data.split(b'"')
        data_elements = elements.pop(0).split(b' ')

        frags = int(data_elements.pop(0))
        ping = int(data_elements.pop(0))
        colored_name = elements.pop(0).decode('latin1')
        name = Server.strip_colors(colored_name)

        return {
            'frags': frags,
            'ping': ping,
            'name': name,
            'colored_name': colored_name
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
    def split_packet(packet: bytes) -> Tuple[bytes, bytes]:
        # Medal of Honor responses contain an extra byte (b'\x01') before "statusResponse", hence 20 instead of 19 bytes
        return packet[:20], packet[20:]

    @staticmethod
    def is_valid_response_header(header: bytes) -> bool:
        # Medal of Honor responses contain an extra byte (b'\x01')
        return header == b'\xff\xff\xff\xff\x01statusResponse\n'

    @staticmethod
    def parse_player(player_data: bytes) -> dict:
        elements = player_data.split(b'"')
        data_elements = elements.pop(0).split(b' ')

        # Medal of Honor only sends a player's ping and name (seems like colors are not supported)
        ping = int(data_elements.pop(0))
        name = elements.pop(0).decode('latin1')

        return {
            'ping': ping,
            'name': name
        }
