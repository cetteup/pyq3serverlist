import json

from pyq3serverlist.exceptions import PyQ3SLError, PyQ3SLTimeoutError
from pyq3serverlist.server import MedalOfHonorServer

server = MedalOfHonorServer('185.107.96.110', 12203)
try:
    info = server.get_status()
    print(json.dumps(info))
except (PyQ3SLError, PyQ3SLTimeoutError) as e:
    print(e)
