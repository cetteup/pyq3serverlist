import socket

from .connection import Connection
from .server import Server


class PrincipalServer:
    __address: str
    __port: int
    __connection: Connection
    __query_protocol: int
    __server_entry_prefix: bytes

    def __init__(self, address: str, port: int, query_protocol: int,
                 network_protocol: int = socket.SOCK_DGRAM, server_entry_prefix: bytes = b''):
        self.__address = address
        self.__port = port
        self.__query_protocol = query_protocol
        self.__connection = Connection(self.__address, self.__port, network_protocol)
        self.__server_entry_prefix = server_entry_prefix

    def __parse_data(self, data: bytes) -> list:
        servers = []

        """
        Some 3rd party implementations of the protocol prefix every server entry with the same
        byte sequence (CoD4 X for example) => remove the provided prefix before parsing
        """
        if self.__server_entry_prefix != b'':
            data = data.replace(self.__server_entry_prefix, b'')

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

    def get_servers(self, keywords: str = 'full empty', timeout: float = 1.0) -> list:
        self.__connection.set_timeout(timeout)

        command = f'getservers {self.__query_protocol} {keywords}'

        self.__connection.write(b'\xff' * 4 + command.encode())
        result = self.__connection.read()
        return self.__parse_data(result)
