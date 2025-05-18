import socket
from abc import abstractmethod
from typing import Optional, Tuple

from .exceptions import PyQ3SLError, PyQ3SLTimeoutError
from .connection import Connection
from .buffer import Buffer


class Reader:
    @abstractmethod
    def read(self, connection: Connection, delim: Optional[bytes]) -> Buffer:
        pass

    @staticmethod
    def split_buffer(buffer: Buffer, require_header: bool, delim: Optional[bytes]) -> Tuple[bytes, bytes, bytes]:
        header = b''
        body = b''

        has_header = buffer.peek(22) == (b'\xff' * 4 + b'getserversResponse')
        if require_header and not has_header:
            raise PyQ3SLError('Principal returned invalid data')

        if has_header:
            header += buffer.read(22)

        """
        To complete the header, read bytes until we see the first delimiter.
        Some principals also send a few extra bytes before the first server delimiter,
        Activision for example sends b'\n\x00'.
        """
        while delim is not None and buffer.has() and buffer.peek(len(delim)) != delim:
            header += buffer.read()

        # Read byte by byte until we reach the end or see some sort of end marker
        while buffer.has() and buffer.peek(4) not in [b'\\EOF', b'\\EOT']:
            body += buffer.read()

        # Read what's left of the buffer (if anything)
        tail = buffer.read(len(buffer))

        return header, body, tail


class EOFReader(Reader):
    """
    Reads server list response based on packet markers (requires principal to indicate the end of the response).
    """

    def read(self, connection: Connection, delim: Optional[bytes]) -> Buffer:
        response = Buffer()

        udp = connection.protocol == socket.SOCK_DGRAM

        n = 0
        eof = False
        while not eof:
            buffer = connection.read()

            # Every UDP packet must start with a header. For TCP, only the first packet will start with a header.
            _, body, tail = self.split_buffer(buffer, udp or n == 0, delim)

            # Append body to response
            response.write(body)

            # Check whether the tail indicates the end of the response
            if tail[:4] == b'\\EOF':
                # EOF is clear, always indicates the end of the entire response.
                eof = True
            elif tail[:5] == b'\\EOT\x00':
                # EOT can indicate either the end of the entire response or the end of a response packet (Activision).
                # However, EOT followed by trailing nil-bytes always indicates the end of the response.
                eof = True

            n += 1

        return response


class TimeoutReader(Reader):
    """
    Reads server list response packets until the principal stops sending data.
    For principals that send (proper) EOF markers, use ``EOFReader`` instead.
    """

    def read(self, connection: Connection, delim: Optional[bytes]) -> Buffer:
        response = Buffer()

        udp = connection.protocol == socket.SOCK_DGRAM

        n = 0
        last_length = 0
        end = False
        while not end:
            try:
                buffer = connection.read()
            except PyQ3SLTimeoutError as e:
                # Re-raise exception if we did not read any packets at all.
                if n == 0:
                    raise e
                break

            length = len(buffer)

            # Every UDP packet must start with a header. For TCP, only the first packet will start with a header.
            _, body, _ = self.split_buffer(buffer, udp or n == 0, delim)

            # Append body to response
            response.write(body)

            # Continue to try reading from socket until packets get shorter
            end = n > 0 and length < last_length

            n = n + 1
            last_length = length

        return response
