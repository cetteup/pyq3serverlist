from pyq3serverlist import PrincipalServer, PyQ3SLError, PyQ3SLTimeoutError, TimeoutReader

# Because the Tremulous master does not send (proper) EOF marks, there no way of knowing when we read the last packet.
# See https://github.com/darklegion/tremulous-master/blob/20a0675ab5f66da3d3c47ce0701cd141faa4efc9/master.py#L401.
# Thus, we need to use the TimeoutReader rather than the EOFReader.
principal = PrincipalServer('master.tremulous.net', 30710, reader=TimeoutReader())

servers = []
try:
    servers = principal.get_servers(69)
    print(servers)
except (PyQ3SLError, PyQ3SLTimeoutError) as e:
    print(e)

for server in servers:
    try:
        info = server.get_status()
        print(info)
    except (PyQ3SLError, PyQ3SLTimeoutError) as e:
        print(e)

