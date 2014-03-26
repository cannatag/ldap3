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
from random import choice, randint
from ldap3 import LDAPException, POOLING_STRATEGY_RANDOM_PASSIVE, POOLING_STRATEGY_RANDOM_ACTIVE, POOLING_STRATEGY_NONE, POOLING_STRATEGIES, POOLING_STRATEGY_FIRST_ACTIVE, POOLING_STRATEGY_ROUND_ROBIN_PASSIVE, POOLING_STRATEGY_ROUND_ROBIN_ACTIVE, \
    POOLING_CHECKING_TIMEOUT
from .server import Server


class ServerPoolState(object):
    def __init__(self, server_pool):
        self.servers = []
        self.strategy = server_pool.strategy
        self.server_pool = server_pool
        self.refresh()
        self.initialize_time = datetime.now()
        self.last_used_server = 0

    def __str__(self):
        s = 'servers: '
        if self.servers:
            for server in self.servers:
                s += str(server) + linesep
        else:
            s += 'None'
        s += 'Pool strategy: ' + str(self.strategy)

        return s

    def refresh(self):
        self.servers = []
        for server in self.server_pool.servers:
            self.servers.append(server)

    def get_current_server(self):
        return self.servers[self.last_used_server]

    def get_server(self):
        if self.servers:
            if self.server_pool.strategy == POOLING_STRATEGY_NONE:
                self.last_used_server = 0
                return self.servers[0]  # return alvways the first server - no pooling
            elif self.server_pool.strategy == POOLING_STRATEGY_FIRST_ACTIVE:
                return self.find_active_server()  # returns the first active server
            elif self.server_pool.strategy == POOLING_STRATEGY_ROUND_ROBIN_PASSIVE:
                self.last_used_server = self.last_used_server + 1 if (self.last_used_server + 1) < len(self.servers) else 0
                return self.servers[self.last_used_server]  # returns the next server in a circular range
            elif self.server_pool.strategy == POOLING_STRATEGY_ROUND_ROBIN_ACTIVE:
                return self.find_active_server(self.last_used_server + 1)  # returns the next active server in a circular range
            elif self.server_pool.strategy == POOLING_STRATEGY_RANDOM_PASSIVE:
                self.last_used_server = randint(0, len(self.servers))  # returns a random server in the pool
                return self.servers[self.last_used_server]
            elif self.server_pool.strategy == POOLING_STRATEGY_RANDOM_ACTIVE:
                temp_list = self.servers.copy()
                while temp_list:  # pops a random server from a temp list and checks its availability, if not available tries another one
                    server = temp_list.pop(randint(0, len(temp_list)))
                    if server.check_availability():
                        self.last_used_server = self.servers.index(server)
                        return server  # returns a random active server in the pool
                raise LDAPException('no random active server in server pool')
            else:
                raise LDAPException('unknown pool strategy')
        else:
            raise LDAPException('no servers in server pool')

    def find_active_server(self, starting=0):
        index = starting
        while index < len(self.servers):
            if self.servers[index].check_availability():
                break
            index += 1
        else:  # if no server found upwards in the list checks starting from the base of the list
            index = 0
            while index < starting:
                if self.servers[index].check_availability():
                    break
                index += 1
            else:
                raise LDAPException('no active server available in server pool')

        self.last_used_server = index
        return self.servers[index]

    def __len__(self):
        return len(self.servers)


class ServerPool(object):
    def __init__(self, servers=None, pool_strategy=POOLING_STRATEGY_ROUND_ROBIN_ACTIVE):
        if pool_strategy not in POOLING_STRATEGIES:
            raise LDAPException('unknown pooling strategy')
        self.servers = []
        self.pool_states = dict()
        if isinstance(servers, list):
            for server in servers:
                self.add(server)
        elif isinstance(servers, Server):
            self.add(servers)
        self.strategy = pool_strategy

    def __str__(self):
            s = 'servers: '
            if self.servers:
                for server in self.servers:
                    s += str(server) + linesep
            else:
                s += 'None'
            s += 'Pool strategy: ' + str(self.strategy)

            return s

    def __repr__(self):
        r = 'ServerPool(servers='
        if self.servers:
            r += '['
            for server in self.servers:
                r += server.__repr__() + ', '
            r = r[:-2] + ']'
        else:
            r += 'None'
        r += ', pool_strategy={0.strategy!r}'.format(self)
        r += ')'

        return r

    def __len__(self):
        return len(self.servers)

    def add(self, servers):
        if isinstance(servers, Server):
            if servers not in self.servers:
                self.servers.append(servers)
        elif isinstance(servers, list):
            for server in servers:
                if isinstance(server, Server):
                    self.servers.append(server)
                else:
                    raise LDAPException('pooled server in list must be a Server object')
        else:
            raise LDAPException('pooled server must be a Server object or a list of Server objects')

        for connection in self.pool_states:  # notifies connections using this pool to refresh
            self.pool_states[connection].refresh()

    def remove(self, server):
        if server in self.servers:
            self.servers.remove(server)
        else:
            raise LDAPException('server not in server pool')

        for connection in self.pool_states:  # notifies connections using this pool to refresh
            self.pool_states[connection].refresh()

    def initialize(self, connection):
        pool_state = ServerPoolState(self)
        self.pool_states[connection] = pool_state  # registers pool_state in ServerPool object

    def get_server(self, connection):
        if connection in self.pool_states:
            return self.pool_states[connection].get_server()
        else:
            raise LDAPException('connection not in server pool state')

    def get_current_server(self, connection):
        if connection in self.pool_states:
            return self.pool_states[connection].get_current_server()
        else:
            raise LDAPException('connection not in server pool state')
