import json

from pyq3serverlist import MedalOfHonorServer, PyQ3SLError, PyQ3SLTimeoutError

server = MedalOfHonorServer('185.107.96.110', 12203)
try:
    info = server.get_status()
    print(json.dumps(info))
except (PyQ3SLError, PyQ3SLTimeoutError) as e:
    print(e)
