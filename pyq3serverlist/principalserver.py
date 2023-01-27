import socket
from typing import List, Optional

from .buffer import Buffer
from .connection import Connection
from .exceptions import PyQ3SLError
from .server import Server


class PrincipalServer:
    address: str
    port: int
    connection: Connection

    def __init__(
            self,
            address: str,
            port: int,
            network_protocol: socket.SocketKind = socket.SOCK_DGRAM,
            timeout: float = 1.0
    ):
        self.address = address
        self.port = port
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
        result = self.connection.read()

        # Server entries are separated by slashes
        return self.parse_response(result, b'\\', server_entry_prefix)

    @staticmethod
    def parse_response(buffer: Buffer, sep: Optional[bytes] = None, prefix: Optional[bytes] = None) -> list:
        if not PrincipalServer.buffer_has_packet_header(buffer, sep):
            raise PyQ3SLError('Principal returned invalid data')

        sep_len = len(sep) if sep is not None else 0
        """
        Some 3rd party implementations of the protocol also prefix every server entry with the same
        byte sequence (CoD4 X for example) => ignore prefix while parsing
        """
        prefix_len = len(prefix) if prefix is not None else 0

        # Servers are represented as six byte sequences, plus the length of any separator and prefix
        servers = []
        while buffer.has(6 + sep_len + prefix_len):
            # Skip backspace delimiter and prefix
            buffer.skip(sep_len + prefix_len)
            ip, port = buffer.read_ip(), buffer.read_ushort()

            """
            Some principals return complete responses in each packet
            => check for and skip b'\\EOT' or b'\\EOT\x00' and additional headers
            """
            if buffer.peek(4) == b'\\EOT':
                buffer.skip(4)
                if buffer.peek(1) == b'\x00':
                    buffer.skip(1)
            PrincipalServer.buffer_has_packet_header(buffer, sep)

            # Init and append valid server
            if ip != '0.0.0.0' and port != 0:
                servers.append(Server(ip, port))

        return servers

    @staticmethod
    def buffer_has_packet_header(buffer: Buffer, sep: Optional[bytes] = None) -> bool:
        if buffer.peek(22) != (b'\xff' * 4 + b'getserversResponse'):
            return False

        buffer.skip(22)

        """
        Some principals send a few extra bytes before the first server delimiter, Activision for example sends
        b'\n\x00' => read until we see the first delimiter
        """
        while sep is not None and buffer.peek(1) != sep:
            buffer.skip(1)

        return True
