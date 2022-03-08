import re

from .exceptions import PyQ3SLError
from .connection import Connection


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

        command = 'getstatus'

        self.connection.write(b'\xff' * 4 + command.encode() + b'\x00')
        result = self.connection.read()
        return self.parse_response(result)

    def parse_response(self, data: bytes) -> dict:
        """
        Response should consist of at least three lines:
        1: header indicating response type
        2: list of server variables, delimited by \
        3+: lines containing player info (final player line being empty)
        """
        # Make sure header (first 19 bytes) indicates status response as type
        header = data[:19]
        if header != b'\xff' * 4 + b'statusResponse\n':
            raise PyQ3SLError('Server returned invalid packet header')

        # Make sure body starts with "\" indicating the first variable and contains an even number of keys and values
        body = data[19:]
        if not body.startswith(b'\\') or body.count(b'\\') % 2 != 0:
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
    def strip_colors(value: str) -> str:
        return re.sub(r'\^(X.{6}|.)', '', value)

    def parse_player(self, player_data: bytes) -> dict:
        elements = player_data.split(b'"')
        data_elements = elements.pop(0).split(b' ')

        frags = int(data_elements.pop(0))
        ping = int(data_elements.pop(0))
        colored_name = elements.pop(0).decode('latin1')
        name = self.strip_colors(colored_name)

        return {
            'frags': frags,
            'ping': ping,
            'name': name,
            'colored_name': colored_name
        }
