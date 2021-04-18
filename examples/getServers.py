from pyq3serverlist import MasterServer
from pyq3serverlist.exceptions import PyQ3SLError, PyQ3SLTimeoutError

master = MasterServer('cod4master.activision.com', 20810, 6)

try:
    servers = master.get_servers(timeout=3)
    print(servers)
except (PyQ3SLError, PyQ3SLTimeoutError) as e:
    print(e)

