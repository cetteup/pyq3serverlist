import socket

from pyq3serverlist import PrincipalServer
from pyq3serverlist.exceptions import PyQ3SLError, PyQ3SLTimeoutError

principal = PrincipalServer('cod4master.cod4x.me', 20810, 6, socket.SOCK_STREAM, b'\x00\x00\x00\x00\x04')

try:
    servers = principal.get_servers(keywords='full empty \x00', timeout=3)
    print(servers)
except (PyQ3SLError, PyQ3SLTimeoutError) as e:
    print(e)

