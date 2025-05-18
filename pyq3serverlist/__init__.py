from .connection import Connection
from .exceptions import PyQ3SLError, PyQ3SLTimeoutError
from .principalserver import PrincipalServer
from .reader import Reader, EOFReader, TimeoutReader
from .server import Server, MedalOfHonorServer

"""
pyq3serverlist.

Simple Python library for querying Quake 3 based principal servers and their game servers.
"""

__version__ = '0.3.2'
__author__ = 'cetteup'
__credits__ = 'https://github.com/jacklul'
__all__ = [
    'PrincipalServer',
    'Server',
    'MedalOfHonorServer',
    'Connection',
    'Reader',
    'EOFReader',
    'TimeoutReader',
    'PyQ3SLError',
    'PyQ3SLTimeoutError'
]
