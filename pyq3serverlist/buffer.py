import re
import struct
from typing import Union, List

from .exceptions import PyQ3SLError

COLOR_REGEX = re.compile(r'\^(X.{6}|.)')


class Buffer:
    data: bytes
    length: int
    index: int

    def __init__(self, data: bytes = b''):
        self.data = data
        self.length = len(data)
        self.index = 0

    def get_buffer(self) -> bytes:
        return self.data[self.index:]

    def read(self, length: int = 1) -> bytes:
        if self.index + length > self.length:
            raise PyQ3SLError('Attempt to read beyond buffer length')

        data = self.data[self.index:self.index + length]
        self.index += length

        return data

    def peek(self, length: int = 1) -> bytes:
        return self.data[self.index:self.index + length]

    def skip(self, length: int = 1) -> None:
        self.index += length

    def has(self, length: int = 1) -> bool:
        return len(self) >= length

    def __len__(self):
        return max(0, self.length - self.index)

    def read_string(
            self,
            sep: Union[bytes, List[bytes]],
            consume_sep: bool = False,
            encoding: str = 'latin1',
            strip_colors: bool = True
    ) -> str:
        b = self.get_buffer()
        """
        ioquake3 server may contain an "fs_manifest", which contains "\n " as a delimiter. Since "\n" would usually
        terminate the sever info like, this breaks the format. So, "greedily" try to use the first given delimiter,
        only switch alternate ones if previous cannot be found at all (will read past the "\n " in "fs_manifest" since 
        it is not the last value.
        """
        sep_list = [sep] if type(sep) == bytes else sep
        index = next((i for sep in sep_list if (i := b.find(sep)) != -1), -1)
        if index == -1:
            raise PyQ3SLError('Expected string delimiters were not found')
        v = self.read(index)

        if consume_sep:
            self.skip(1)

        raw = v.decode(encoding, errors='replace')
        if strip_colors:
            return COLOR_REGEX.sub('', raw)

        return raw

    def read_ushort(self) -> int:
        v, *_ = struct.unpack('>H', self.read(2))
        return v

    def read_ip(self) -> str:
        v = self.read(4)
        return "%d.%d.%d.%d" % struct.unpack(">BBBB", v)

    def write(self, v: bytes) -> None:
        self.data += v
        self.length += len(v)

    def write_string(self, v: str, encoding: str = 'latin1') -> None:
        self.write(v.encode(encoding))

    def write_ushort(self, v: int) -> None:
        self.write(struct.pack('>H', v))
