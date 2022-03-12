import json

from pyq3serverlist import Server, PyQ3SLError, PyQ3SLTimeoutError

server = Server('140.82.4.154', 27960)
try:
    info = server.get_status()
    print(json.dumps(info))
except (PyQ3SLError, PyQ3SLTimeoutError) as e:
    print(e)
