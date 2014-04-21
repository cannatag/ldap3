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
from random import randint
from ldap3 import LDAPException, POOLING_STRATEGY_FIRST, POOLING_STRATEGY_ROUND_ROBIN, POOLING_STRATEGY_RANDOM, POOLING_STRATEGIES
from .server import Server


class ServerPoolState(object):
    def __init__(self, server_pool):
        self.servers = []
        self.strategy = server_pool.strategy
        self.server_pool = server_pool
        self.refresh()
        self.initialize_time = datetime.now()
        self.last_used_server = randint(0, len(self.servers)-1)

    def __str__(self):
        s = 'servers: '
        if self.servers:
            for server in self.servers:
                s += str(server) + linesep
        else:
            s += 'None'
        s += 'Pool strategy: ' + str(self.strategy)
        s += ' - Last used server: ' + ('None' if self.last_used_server == -1 else str(self.servers[self.last_used_server]))

        return s

    def refresh(self):
        self.servers = []
        for server in self.server_pool.servers:
            self.servers.append(server)
        self.last_used_server = randint(0, len(self.servers) - 1)

    def get_current_server(self):
        return self.servers[self.last_used_server]

    def get_server(self):
        if self.servers:
            if self.server_pool.strategy == POOLING_STRATEGY_FIRST:
                if self.server_pool.active:
                    # returns the first active server
                    self.last_used_server = self.find_active_server(starting=0, exhaust=self.server_pool.exhaust)
                else:
                    # returns alvways the first server - no pooling
                    self.last_used_server = 0
            elif self.server_pool.strategy == POOLING_STRATEGY_ROUND_ROBIN:
                if self.server_pool.active:
                    # returns the next active server in a circular range
                    self.last_used_server = self.find_active_server(self.last_used_server + 1, exhaust=self.server_pool.exhaust)
                else:
                    # returns the next server in a circular range
                    self.last_used_server = self.last_used_server + 1 if (self.last_used_server + 1) < len(self.servers) else 0
            elif self.server_pool.strategy == POOLING_STRATEGY_RANDOM:
                if self.server_pool.active:
                    self.last_used_server = self.find_active_random_server(exhaust=self.server_pool.exhaust)
                else:
                    # returns a random server in the pool
                    self.last_used_server = randint(0, len(self.servers))
            else:
                raise LDAPException('unknown pool strategy')
            return self.servers[self.last_used_server]
        else:
            raise LDAPException('no servers in server pool')

    def find_active_random_server(self, exhaust=True):
        while True:
            temp_list = self.servers.copy()
            while temp_list:
                # pops a random server from a temp list and checks its
                # availability, if not available tries another one
                server = temp_list.pop(randint(0, len(temp_list) - 1))
                if server.check_availability():
                    # returns a random active server in the pool
                    return self.servers.index(server)
            if exhaust:
                raise LDAPException('no random active server in server pool')

    def find_active_server(self, starting=0, exhaust=True):
        while True:
            index = starting
            while index < len(self.servers):
                if self.servers[index].check_availability():
                    break
                index += 1
            else:
                # if no server found in the list (from starting index)
                # checks starting from the base of the list
                index = 0
                while index < starting:
                    if self.servers[index].check_availability():
                        break
                    index += 1
                else:
                    if exhaust:
                        raise LDAPException('no active server available in server pool')
                    else:
                        continue
            return index

    def __len__(self):
        return len(self.servers)


class ServerPool(object):
    def __init__(self,
                 servers=None,
                 pool_strategy=POOLING_STRATEGY_ROUND_ROBIN,
                 active=True,
                 exhaust=False):

        if pool_strategy not in POOLING_STRATEGIES:
            raise LDAPException('unknown pooling strategy')
        if exhaust and not active:
            raise LDAPException('pool can be exhausted only when checking for active servers')
        self.servers = []
        self.pool_states = dict()
        self.active = active
        self.exhaust = exhaust
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
            s += ' - ' + 'active only: ' + ('True' if self.active else 'False')
            s += ' - ' + 'exhaust pool: ' + ('True' if self.exhaust else 'False')
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
        r += ', active={0.active!r}'.format(self)
        r += ', exhaust={0.exhaust!r}'.format(self)
        r += ')'

        return r

    def __len__(self):
        return len(self.servers)

    def __getitem__(self, item):
        return self.servers[item]

    def __iter__(self):
        return self.servers.__iter__()

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

        for connection in self.pool_states:
            # notifies connections using this pool to refresh
            self.pool_states[connection].refresh()

    def remove(self, server):
        if server in self.servers:
            self.servers.remove(server)
        else:
            raise LDAPException('server not in server pool')

        for connection in self.pool_states:
            # notifies connections using this pool to refresh
            self.pool_states[connection].refresh()

    def initialize(self, connection):
        pool_state = ServerPoolState(self)
        # registers pool_state in ServerPool object
        self.pool_states[connection] = pool_state

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
