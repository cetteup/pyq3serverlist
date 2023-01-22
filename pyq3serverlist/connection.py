import socket

from .buffer import Buffer
from .exceptions import PyQ3SLError, PyQ3SLTimeoutError


class Connection:
    address: str
    port: int
    protocol: int
    sock: socket.socket
    timeout: float = 2.0
    is_connected: bool = False

    def __init__(self, address: str, port: int, protocol: int = socket.SOCK_DGRAM):
        self.address = address
        self.port = port
        self.protocol = protocol

    def set_timeout(self, timeout: float) -> None:
        self.timeout = timeout

    def set_timeout_option(self, timeout: float) -> None:
        if not isinstance(self.sock, socket.socket):
            raise PyQ3SLError('Socket handle is not valid')

        self.sock.settimeout(timeout)

    def connect(self) -> None:
        if self.is_connected:
            return

        self.sock = socket.socket(socket.AF_INET, self.protocol)

        self.set_timeout_option(self.timeout)

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

        try:
            self.sock.sendall(data)
        except socket.error:
            raise PyQ3SLError('Failed to send data to server')

    def read(self) -> Buffer:
        if not self.is_connected:
            self.connect()

        data = b''
        last_packet_length = 0
        receive_next = True

        while receive_next:
            try:
                # Packet size differs from server to server => just read up to max possible UDP size
                iteration_data = self.sock.recv(65507)
            except socket.timeout:
                # Raise exception if no data was retrieved at all, else break loop
                if data == b'':
                    raise PyQ3SLTimeoutError('Timed out while receiving server data')
                else:
                    break
            except socket.error:
                raise PyQ3SLError('Failed to receive data from server')

            data += iteration_data

            buffer_end = iteration_data[-10:]
            # Continue to try reading from socket until packets get shorter or peer indicates EOF (in case of TCP)
            receive_next = (self.protocol == socket.SOCK_DGRAM and len(iteration_data) >= last_packet_length) or \
                           (self.protocol == socket.SOCK_STREAM and b'EOF' not in buffer_end)
            last_packet_length = len(iteration_data)

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
