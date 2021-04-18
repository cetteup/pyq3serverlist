import socket
from typing import Optional

from .exceptions import PyQ3SLError, PyQ3SLTimeoutError


class Connection:
    __address: str
    __port: int
    __protocol: int
    __socket: socket.socket
    __timeout: float = 2.0
    __is_connected: bool = False
    __buffer: bytes = b''

    def __init__(self, address: str, port: int, protocol: int = socket.SOCK_DGRAM):
        self.__address = address
        self.__port = port
        self.__protocol = protocol

    def set_timeout(self, timeout: float) -> None:
        self.__timeout = timeout

    def __set_timeout_option(self, timeout: float) -> None:
        if not isinstance(self.__socket, socket.socket):
            raise PyQ3SLError('Socket handle is not valid')

        self.__socket.settimeout(timeout)

    def connect(self) -> None:
        if self.__is_connected:
            return

        self.__socket = socket.socket(socket.AF_INET, self.__protocol)

        self.__set_timeout_option(self.__timeout)

        try:
            self.__socket.connect((self.__address, self.__port))
            self.__is_connected = True
        except socket.timeout:
            self.__is_connected = False
            raise PyQ3SLTimeoutError(f'Connection attempt to {self.__address}:{self.__port} timed out')
        except socket.error as e:
            self.__is_connected = False
            raise PyQ3SLError(f'Failed to connect to {self.__address}:{self.__port} ({e})')

    def write(self, data: bytes) -> None:
        if not self.__is_connected:
            self.connect()

        try:
            self.__socket.sendall(data)
        except socket.error:
            raise PyQ3SLError('Failed to send data to server')

    def read(self) -> Optional[bytes]:
        if not self.__is_connected:
            self.connect()

        self.__buffer = b''
        last_packet_length = 0
        receive_next = True

        while receive_next:
            try:
                # Packet size differs from server to server => just read up to max possible UDP size
                buffer = self.__socket.recv(65507)
            except socket.timeout:
                # Raise exception if no data was retrieved at all, else break loop
                if self.__buffer == b'':
                    raise PyQ3SLTimeoutError('Timed out while receiving server data')
                else:
                    break
            except socket.error:
                raise PyQ3SLError('Failed to receive data from server')

            self.__buffer += buffer

            buffer_end = buffer[-10:]
            # Continue to try reading from socket until packets get shorter or peer indicates EOF (in case of TCP)
            receive_next = (self.__protocol == socket.SOCK_DGRAM and len(buffer) >= last_packet_length) or \
                           (self.__protocol == socket.SOCK_STREAM and b'EOF' not in buffer_end)
            last_packet_length = len(buffer)

        return self.__buffer

    def __del__(self):
        self.close()

    def close(self) -> bool:
        if isinstance(self.__socket, socket.socket):
            if self.__is_connected:
                self.__socket.shutdown(socket.SHUT_RDWR)
            self.__socket.close()
            self.__is_connected = False
            return True

        return False
