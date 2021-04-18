from .connection import Connection
from .server import Server


class MasterServer:
    __address: str
    __port: int
    __connection: Connection
    __protocol: int

    def __init__(self, address: str, port: int, protocol: int):
        self.__address = address
        self.__port = port
        self.__protocol = protocol
        self.__connection = Connection(self.__address, self.__port)

    def __parse_data(self, data: bytes) -> list:
        servers = []

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

        command = f'getservers {self.__protocol} {keywords}'

        self.__connection.write(b'\xff' * 4 + command.encode())
        result = self.__connection.read()
        return self.__parse_data(result)
