from pyq3serverlist import PrincipalServer
from pyq3serverlist.exceptions import PyQ3SLError, PyQ3SLTimeoutError

principal = PrincipalServer('cod4master.activision.com', 20810, 6)

try:
    servers = principal.get_servers(timeout=3)
    print(servers)
except (PyQ3SLError, PyQ3SLTimeoutError) as e:
    print(e)

