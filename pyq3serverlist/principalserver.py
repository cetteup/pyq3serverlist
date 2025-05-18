import socket
from typing import List, Optional

from .buffer import Buffer
from .connection import Connection
from .reader import Reader, EOFReader
from .server import Server


class PrincipalServer:
    address: str
    port: int
    reader: Reader
    connection: Connection

    def __init__(
            self,
            address: str,
            port: int,
            reader: Reader = EOFReader(),
            network_protocol: socket.SocketKind = socket.SOCK_DGRAM,
            timeout: float = 1.0
    ):
        self.address = address
        self.port = port
        self.reader = reader
        self.connection = Connection(self.address, self.port, network_protocol, timeout)

    def get_servers(
            self,
            query_protocol: int,
            game_name: str = '',
            keywords: str = 'full empty',
            server_entry_prefix: Optional[bytes] = None
    ) -> List[Server]:
        buffer = Buffer(b'\xff' * 4)
        buffer.write_string('getservers ')
        # Add game name if set
        if game_name != '':
            buffer.write_string(f'{game_name} ')
        # Add query protocol and keywords
        buffer.write_string(f'{query_protocol} {keywords}')

        self.connection.write(buffer.get_buffer())

        buffer = self.reader.read(self.connection, b'\\')

        return self.parse_response(buffer, b'\\', server_entry_prefix)

    @staticmethod
    def parse_response(buffer: Buffer, delim: Optional[bytes] = None, prefix: Optional[bytes] = None) -> List[Server]:
        delim_len = len(delim) if delim is not None else 0
        """
        Some 3rd party implementations of the protocol also prefix every server entry with the same
        byte sequence (CoD4 X for example) => ignore prefix while parsing
        """
        prefix_len = len(prefix) if prefix is not None else 0

        # Servers are represented as six byte sequences, plus the length of any separator and prefix
        servers: List[Server] = []
        while buffer.has(6 + delim_len + prefix_len):
            # Skip backspace delimiter and prefix
            buffer.skip(delim_len + prefix_len)
            ip, port = buffer.read_ip(), buffer.read_ushort()

            # Init and append valid server
            if ip != '0.0.0.0' and port != 0:
                servers.append(Server(ip, port))

        return servers
