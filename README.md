# pyq3serverlist

[![ci](https://img.shields.io/github/actions/workflow/status/cetteup/pyq3serverlist/ci.yml?label=ci)](https://github.com/cetteup/pyq3serverlist/actions?query=workflow%3Aci)
[![License](https://img.shields.io/github/license/cetteup/pyq3serverlist)](/LICENSE)
[![Package](https://img.shields.io/pypi/v/pyq3serverlist)](https://pypi.org/project/pyq3serverlist/)
[![Last commit](https://img.shields.io/github/last-commit/cetteup/pyq3serverlist)](https://github.com/cetteup/pyq3serverlist/commits/main)

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
from pyq3serverlist import PrincipalServer, PyQ3SLError, PyQ3SLTimeoutError

principal = PrincipalServer('cod4master.activision.com', 20810)

try:
    servers = principal.get_servers(6)
    print(servers)
except (PyQ3SLError, PyQ3SLTimeoutError) as e:
    print(e)
```

Longer server lists are usually split into multiple packets. Unfortunately, some principal servers implemented the Quake3 protocol without any indication of whether the response consists of multiple packets.
For these principal servers (e.g. `master.quake3arena.com`, `*.idsoftware.com`, `master0.etmaster.net`), we need to keep reading packets until a read attempt times out.

To enable this behavior, use the `TimeoutReader` instead of the default `EOFReader`.

```python
from pyq3serverlist import PrincipalServer, TimeoutReader, PyQ3SLError, PyQ3SLTimeoutError

principal = PrincipalServer('master.quake3arena.com', 27950, reader=TimeoutReader())

try:
    servers = principal.get_servers(68)
    print(servers)
except (PyQ3SLError, PyQ3SLTimeoutError) as e:
    print(e)
```

If you want to query a specific server, initialize a game server object for a known server directly and query its status.

```python
from pyq3serverlist import Server, PyQ3SLError, PyQ3SLTimeoutError

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
from pyq3serverlist import MedalOfHonorServer, PyQ3SLError, PyQ3SLTimeoutError

server = MedalOfHonorServer('217.247.241.12', 12203)
try:
    info = server.get_status()
    print(info)
except (PyQ3SLError, PyQ3SLTimeoutError) as e:
    print(e)
```

You can find a few more examples in the `examples` folder.
