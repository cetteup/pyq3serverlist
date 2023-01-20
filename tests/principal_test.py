import unittest
from dataclasses import dataclass
from typing import Optional, List

from pyq3serverlist import Server, PyQ3SLError, PrincipalServer


class PrincipalTest(unittest.TestCase):
    def test_parse_response(self):
        @dataclass
        class ParseResponseTestCase:
            name: str
            data: bytes
            entry_prefix: bytes = b''
            expected: Optional[List[Server]] = None
            wantErrContains: Optional[str] = None

        tests: List[ParseResponseTestCase] = [
            ParseResponseTestCase(
                name='parses response packet with single server',
                data=b'\xff\xff\xff\xffgetserversResponse\\\x7f\x00\x00\x01m8\\EOT',
                expected=[
                    Server('127.0.0.1', 27960)
                ]
            ),
            ParseResponseTestCase(
                name='parses response packet with single server',
                data=b'\xff\xff\xff\xffgetserversResponse\\\x7f\x00\x00\x01m8\\\x7f\x00\x00\x02m9\\EOT',
                expected=[
                    Server('127.0.0.1', 27960),
                    Server('127.0.0.2', 27961)
                ]
            ),
            ParseResponseTestCase(
                name='parses response packet without trailing \\EOT',
                data=b'\xff\xff\xff\xffgetserversResponse\\\x7f\x00\x00\x01m8',
                expected=[
                    Server('127.0.0.1', 27960)
                ]
            ),
            ParseResponseTestCase(
                name='parses response packet with entry prefix',
                data=b'\xff\xff\xff\xffgetserversResponse'
                     b'\\\x00\x00\x00\x00\x04\x7f\x00\x00\x01m8'
                     b'\\\x00\x00\x00\x00\x04\x7f\x00\x00\x02m9'
                     b'\\EOT',
                entry_prefix=b'\x00\x00\x00\x00\x04',
                expected=[
                    Server('127.0.0.1', 27960),
                    Server('127.0.0.2', 27961)
                ]
            ),
            ParseResponseTestCase(
                name='ignores zero ip entry',
                data=b'\xff\xff\xff\xffgetserversResponse\\\x7f\x00\x00\x01m8\\\x00\x00\x00\x00m9\\EOT',
                expected=[
                    Server('127.0.0.1', 27960)
                ]
            ),
            ParseResponseTestCase(
                name='ignores zero port entry',
                data=b'\xff\xff\xff\xffgetserversResponse\\\x7f\x00\x00\x01m8\\\x7f\x00\x00\x02\x00\x00\\EOT',
                expected=[
                    Server('127.0.0.1', 27960)
                ]
            ),
            ParseResponseTestCase(
                name='errors for response packet not starting with expected bytes',
                data=b'\xff\xff\xff\xff\xffnotAGetserversResponse',
                wantErrContains='Principal returned invalid data'
            )
        ]

        for t in tests:
            if t.wantErrContains is not None:
                # WHEN/THEN
                self.assertRaisesRegex(
                    PyQ3SLError,
                    t.wantErrContains,
                    PrincipalServer.parse_response,
                    t.data,
                    t.entry_prefix
                )
            else:
                # WHEN
                actual = PrincipalServer.parse_response(t.data, t.entry_prefix)

                # THEN
                self.assertListEqual(t.expected, actual)


if __name__ == '__main__':
    unittest.main()
