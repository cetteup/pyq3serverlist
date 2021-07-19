# pyq3serverlist

Simple Python 🐍 library for querying Quake 3 based principal servers and their game servers. Very much based on [jacklul's PHP implementation](https://github.com/jacklul/q3serverlist).

## Features
- retrieve a list of game servers from a Quake 3 principal ("master") server
- supports both UDP (default) and TCP for server list retrieval
- retrieve status details and current players from game servers

## Installation
Simply install the package via pip.

```bash
$ pip install pyq3serverlist
```

## Usage
The following example retrieves and prints a game server list for Call of Duty 4: Modern Warfare directly from Activision via UDP.

```python
from pyq3serverlist import PrincipalServer
from pyq3serverlist.exceptions import PyQ3SLError, PyQ3SLTimeoutError

principal = PrincipalServer('cod4master.activision.com', 20810)

try:
    servers = principal.get_servers(6)
    print(servers)
except (PyQ3SLError, PyQ3SLTimeoutError) as e:
    print(e)
```

You can also directly initialize a game server object for a known server and query its status.

```python
from pyq3serverlist import Server
from pyq3serverlist.exceptions import PyQ3SLError, PyQ3SLTimeoutError

server = Server('198.144.177.2', 27963)
try:
    info = server.get_status()
    print(info)
except (PyQ3SLError, PyQ3SLTimeoutError) as e:
    print(e)
```

You can find a few more examples in the `examples` folder.