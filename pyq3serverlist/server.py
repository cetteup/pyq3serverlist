import re

from .exceptions import PyQ3SLError
from .connection import Connection


class Server:
    ip: str
    port: int
    __connection: Connection

    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.__connection = Connection(ip, port)

    def __repr__(self):
        return f'{self.ip}:{self.port}'

    def __iter__(self):
        yield 'ip', self.ip
        yield 'port', self.port

    def __strip_colors(self, value: str) -> str:
        return re.sub(r'\^(X.{6}|.)', '', value)

    def __parse_player(self, player_data: bytes) -> dict:
        elements = player_data.split(b' ', 2)
        frags = int(elements.pop(0))
        ping = int(elements.pop(0))
        colored_name = elements.pop().decode('latin1').replace('"', '')
        name = self.__strip_colors(colored_name)

        return {
            'frags': frags,
            'ping': ping,
            'name': name,
            'colored_name': colored_name
        }

    def __parse_data(self, data: bytes) -> dict:
        lines = data.split(b'\n')

        """
        Response should contain at least thee lines:
        1: header indicating response type
        2: list of server variables, delimited by \
        3+: lines containing player info (final player line being empty) 
        """
        if len(lines) < 3:
            raise PyQ3SLError('Server returned invalid data')

        # Make sure header indicates status response as type
        header = lines.pop(0)
        if header != b'\xff' * 4 + b'statusResponse':
            raise PyQ3SLError('Server returned invalid data')

        variables = lines.pop(0).split(b'\\')[1:]

        keys = [v.decode('latin1') for (i, v) in enumerate(variables) if i % 2 == 0]
        values = [self.__strip_colors(v.decode('latin1')) for (i, v) in enumerate(variables) if i % 2 == 1]

        player_lines = [line for line in lines if line != b'']
        players = []
        for player_line in player_lines:
            player = self.__parse_player(player_line)
            players.append(player)

        return {
            'ip': self.ip,
            'port': self.port,
            **dict(zip(keys, values)),
            'players': players
        }

    def get_status(self, timeout: float = 1.0):
        self.__connection.set_timeout(timeout)

        command = 'getstatus'

        self.__connection.write(b'\xff' * 4 + command.encode() + b'\x00')
        result = self.__connection.read()
        return self.__parse_data(result)
