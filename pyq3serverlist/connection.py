import socket

from .buffer import Buffer
from .exceptions import PyQ3SLError, PyQ3SLTimeoutError
from .logger import logger


class Connection:
    address: str
    port: int
    protocol: socket.SocketKind
    sock: socket.socket
    timeout: float
    is_connected: bool

    def __init__(self, address: str, port: int, protocol: socket.SocketKind, timeout: float):
        self.address = address
        self.port = port
        self.protocol = protocol
        self.timeout = timeout

        self.is_connected = False

    def connect(self) -> None:
        if self.is_connected:
            return

        self.sock = socket.socket(socket.AF_INET, self.protocol)
        self.sock.settimeout(self.timeout)

        logger.debug(f'Connecting to {self.address}:{self.port}')

        try:
            self.sock.connect((self.address, self.port))
            self.is_connected = True
        except socket.timeout:
            self.is_connected = False
            raise PyQ3SLTimeoutError(f'Connection attempt to {self.address}:{self.port} timed out')
        except socket.error as e:
            self.is_connected = False
            raise PyQ3SLError(f'Failed to connect to {self.address}:{self.port} ({e})')

    def write(self, data: bytes) -> None:
        if not self.is_connected:
            self.connect()

        logger.debug('Writing to socket')

        try:
            self.sock.sendall(data)
        except socket.error:
            raise PyQ3SLError('Failed to send data to server')

        logger.debug(f'Sent data: {data.hex(" ")}')

    def read(self) -> Buffer:
        if not self.is_connected:
            self.connect()

        logger.debug('Reading from socket')

        try:
            # Packet size differs from server to server => read up to max possible UDP size
            data = self.sock.recv(65507)
        except socket.timeout:
            raise PyQ3SLTimeoutError('Timed out while receiving server data')
        except socket.error:
            raise PyQ3SLError('Failed to receive data from server')

        logger.debug(f'Received data: {data.hex(" ")}')

        return Buffer(data)

    def __del__(self):
        self.close()

    def close(self) -> bool:
        if hasattr(self, 'sock') and isinstance(self.sock, socket.socket):
            if self.is_connected:
                self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
            self.is_connected = False
            return True

        return False
