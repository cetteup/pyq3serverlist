from pyq3serverlist import PrincipalServer
from pyq3serverlist.exceptions import PyQ3SLError, PyQ3SLTimeoutError

principal = PrincipalServer('dpmaster.deathmask.net', 27950)

servers = []
try:
    servers = principal.get_servers(3, 'Nexuiz')
    print(servers)
except (PyQ3SLError, PyQ3SLTimeoutError) as e:
    print(e)

for server in servers:
    try:
        info = server.get_status()
        print(info)
    except (PyQ3SLError, PyQ3SLTimeoutError) as e:
        print(e)

