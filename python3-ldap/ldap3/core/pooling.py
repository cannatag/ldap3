"""
Created on 2014.03.14

@author: Giovanni Cannata

Copyright 2014 Giovanni Cannata

This file is part of python3-ldap.

python3-ldap is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

python3-ldap is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with python3-ldap in the COPYING and COPYING.LESSER files.
If not, see <http://www.gnu.org/licenses/>.
"""
from datetime import datetime
from os import linesep
from random import choice
import socket
from ldap3 import LDAPException, POOLING_STRATEGY_RANDOM, POOLING_STRATEGY_NONE, POOLING_STRATEGIES, POOLING_STRATEGY_FIRST_ACTIVE, POOLING_STRATEGY_ROUND_ROBIN
from .server import Server


class PooledServer(Server):
    def __init__(self, server):
        self.server = server
        self.active = False
        self.available = False
        self.last_activity = None
        self._connections = []

    def __str__(self):
        s = str(self.server) + ' - '
        s += ('active' if self.active else 'inactive') + ' - '
        s += ('available' if self.available else 'unavailable') + ' - '
        s += 'last activity: ' + (self.last_activity.iso_format() if self.last_activity else 'never') + ' - '
        s += 'connections: ' + len(self._connections)
        return s

    def __repr__(self):
        return self.__str__()


class ServerPoolState(object):
    def __init__(self, server_pool):
        self.servers = []
        for server in server_pool.servers:
            self.servers.append(PooledServer(server))
        self.initialize_time = datetime.now()
        self.strategy = server_pool.strategy
        self.last_used_server = 0

    def get_server(self):
        if self.servers:
            if self.strategy == POOLING_STRATEGY_NONE:
                return self.servers[0]
            elif self.strategy == POOLING_STRATEGY_FIRST_ACTIVE:
                return self.get_first_active_server()
            elif self.strategy == POOLING_STRATEGY_ROUND_ROBIN:
                self.last_used_server = self.last_used_server + 1 if self.last_used_server < len(self.servers) else 0
                return self.server[self.last_used_server]
            elif self.strategy == POOLING_STRATEGY_RANDOM:
                return choice(self.server)
            else:
                raise LDAPException('unknown pool strategy')
        else:
            raise LDAPException('no servers in pool')

    def get_active_server(self):
        cont = -1
        for server in self.servers:
            cont += 1
            if server.check_availability():
                self.last_used_server = cont
                return server

        raise LDAPException('no active server available')

    def _check_availability(self):
        """
        Tries to open, connect and close a socket to check availability
        """
        try:
            temp_socket = socket(socket.AF_INET, socket.SOCK_STREAM)
            temp_socket.connect((self.host, self.port))
            temp_socket.shutdown(socket.SHUT_RDWR)
            temp_socket.close()
        except socket.error:
            return False

        return True


class ServerPool(object):
    def __init__(self, servers=None, pool_strategy=POOLING_STRATEGY_NONE):
        if pool_strategy not in POOLING_STRATEGIES:
            raise LDAPException('unknown pooling strategy')
        self.servers = []
        self.strategy = pool_strategy
        self.states = []

    def __str__(self):
        s = 'servers: '
        for server in self.servers:
            s += str(server) + linesep
        s += 'pool strategy:' + self.strategy

    def __repr__(self):
        return self.__str__()

    def add(self, server):
        if isinstance(server, Server):
            self.servers.append(server)
        else:
            raise LDAPException('pooled server must be a Server object')

    def initialize(self):
        pool_state = ServerPoolState(self)
        self.states.append(pool_state)
        return pool_state

class ConnectionPool(object):
    pass
