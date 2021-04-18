from .connection import Connection
from .exceptions import PyQ3SLError, PyQ3SLTimeoutError
from .principalserver import PrincipalServer
from .server import Server

"""
pyq3serverlist.

Simple Python library for querying Quake 3 based principal servers and their game servers.
"""

__version__ = '0.1.3'
__author__ = 'cetteup'
__credits__ = 'https://github.com/jacklul'
__all__ = ['Connection', 'PrincipalServer', 'Server', 'PyQ3SLError', 'PyQ3SLTimeoutError']
