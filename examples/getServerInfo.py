from pyq3serverlist import Server
from pyq3serverlist.exceptions import PyQ3SLError, PyQ3SLTimeoutError
import json

server = Server('140.82.4.154', 27960)
try:
    info = server.get_status()
    print(json.dumps(info))
except (PyQ3SLError, PyQ3SLTimeoutError) as e:
    print(e)