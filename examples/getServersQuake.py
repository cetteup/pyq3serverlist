from pyq3serverlist import PrincipalServer
from pyq3serverlist.exceptions import PyQ3SLError, PyQ3SLTimeoutError

principal = PrincipalServer('master.quake3arena.com', 27950, 68)

try:
    servers = principal.get_servers()
    print(servers)
except (PyQ3SLError, PyQ3SLTimeoutError) as e:
    print(e)

