import socket

from pyq3serverlist import PrincipalServer, PyQ3SLError, PyQ3SLTimeoutError

principal = PrincipalServer('cod4master.cod4x.ovh', 20810, network_protocol=socket.SOCK_STREAM, timeout=2.0)

servers = []
try:
    servers = principal.get_servers(
        query_protocol=6, game_name='cod4x', keywords='full empty \x00', server_entry_prefix=b'\x00\x00\x00\x00\x04'
    )
    print(servers)
except (PyQ3SLError, PyQ3SLTimeoutError) as e:
    print(e)

for server in servers:
    try:
        info = server.get_status()
        print(info)
    except (PyQ3SLError, PyQ3SLTimeoutError) as e:
        print(e)
