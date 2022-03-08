import socket
from typing import List

from .exceptions import PyQ3SLError
from .connection import Connection
from .server import Server


class PrincipalServer:
    address: str
    port: int
    connection: Connection

    def __init__(self, address: str, port: int, network_protocol: int = socket.SOCK_DGRAM):
        self.address = address
        self.port = port
        self.connection = Connection(self.address, self.port, network_protocol)

    def get_servers(self, query_protocol: int, game_name: str = '', keywords: str = 'full empty',
                    server_entry_prefix: bytes = b'', timeout: float = 1.0) -> List[Server]:
        self.connection.set_timeout(timeout)

        # Build command/packet string
        command = 'getservers '
        # Add game name if set
        if game_name != '':
            command += f'{game_name} '
        # Add query protocol and keywords
        command += f'{query_protocol} {keywords}'

        self.connection.write(b'\xff' * 4 + command.encode())
        result = self.connection.read()
        return self.parse_response(result, server_entry_prefix)

    @staticmethod
    def parse_response(data: bytes, server_entry_prefix: bytes) -> list:
        servers = []

        if not data.startswith(b'\xff' * 4 + b'getserversResponse'):
            raise PyQ3SLError('Principal returned invalid data')

        """
        Some 3rd party implementations of the protocol prefix every server entry with the same
        byte sequence (CoD4 X for example) => remove the provided prefix before parsing
        """
        if server_entry_prefix != b'':
            data = data.replace(server_entry_prefix, b'')

        # Server is represented as six byte sequences, separated by backslashes
        raw_entries = [entry for entry in data.split(b'\\') if len(entry) == 6]

        for entry in raw_entries:
            # Join first 4 bytes together as IP address
            ip = '.'.join([str(octet) for octet in entry[0:4]])
            # Shift 5th byte to the left by 8 bits and add 6th byte to get (query) port
            port = (entry[4] << 8) + entry[5]

            # Init and append valid server
            if ip != '0.0.0.0' and port != 0:
                servers.append(Server(ip, port))

        return servers
