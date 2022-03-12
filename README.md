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

Medal of Honor: Allied Assault, Medal of Honor: Allied Assault Spearhead, Medal of Honor: Allied Assault Breakthrough and Medal of Honor: Pacific Assault all use GameSpy for listing server and support the GameSpy1 query protocol. They do, however, also support a Quake3 protocol variant, which allows queries via the game port.

You can query any known game server for the mentioned Medal of Honor games using `MedalOfHonorServer` instead of `Server`.

```python
from pyq3serverlist import MedalOfHonorServer
from pyq3serverlist.exceptions import PyQ3SLError, PyQ3SLTimeoutError

server = MedalOfHonorServer('217.247.241.12', 12203)
try:
    info = server.get_status()
    print(info)
except (PyQ3SLError, PyQ3SLTimeoutError) as e:
    print(e)
```

You can find a few more examples in the `examples` folder.