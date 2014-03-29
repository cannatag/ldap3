"""
Created on 2014.03.23

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
from queue import Queue
from threading import Thread

from .baseStrategy import BaseStrategy
from ldap3 import REUSABLE_POOL_SIZE, REUSABLE_CONNECTION_LIFETIME, STRATEGY_SYNC_RESTARTABLE, TERMINATE_REUSABLE, RESPONSE_WAITING_TIMEOUT, LDAP_MAX_INT


class ReusableStrategy(BaseStrategy):
    """
    A pool of reusable SyncWaitRestartable connections with lazy behaviour and limited lifetime.
    The connection using this strategy presents itself as a normal connection, but internally the strategy has a pool of
    connections that can be used as needed. Each connection lives in its own thread and has a busy/available status. The strategy performs the requested
    operation on the first available connection.
    The pool of connections is instantiated at strategy initialization.
    Strategy has two settable properties, the total number of connection present in the pool and the lifetime of each connection.
    When lifetime is expired the connection is closed and will be opened again when needed
    """

    class PooledConnectionThread(Thread):
        def __init__(self, reusable_connection):
            Thread.__init__(self)
            self.active_connection = reusable_connection

        def run(self):
            self.active_connection.running = True
            terminate = False
            while not terminate:
                operation = self.active_connection.request_queue.get()
                self.active_connection.busy = True
                if operation == TERMINATE_REUSABLE and not self.active_connection.cannot_terminate:
                    terminate = True
                else:
                    result = self.active_connection.connection.send(*operation)
                    # self.active_connection.response_queue.put()
                self.active_connection.busy = False
            self.active_connection.running = False


    class ReusableConnection(object):
        """
        Container for the Restartable connection. it includes a thread and a lock to execute the connection in the pool
        """
        def __init__(self, connection, request_queue):
            from ..core.connection import Connection
            self.connection = Connection(server=connection.server,
                                         user=connection.user,
                                         password=connection.password,
                                         version=connection.version,
                                         authentication=connection.authentication,
                                         client_strategy=STRATEGY_SYNC_RESTARTABLE,
                                         auto_referrals=connection.auto_referrals,
                                         sasl_mechanism=connection.sasl_mechanism,
                                         sasl_credentials=connection.sasl_credentials,
                                         collect_usage=True if connection.usage else False,
                                         read_only=connection.read_only,
                                         lazy=True)
            self.running = False
            self.busy = False
            self.cannot_terminate = False
            self.request_queue = request_queue
            self.creation_time = datetime.now()
            self.thread = ReusableStrategy.PooledConnectionThread(self)

        def __str__(self):
            s = str(self.connection) + linesep
            s += 'running ' if self.running else 'halted' + ' - '
            s += 'busy' if self.busy else ' available' ' - '
            s += 'creation time ' + self.creation_time.isoformat()

            return s

    def __init__(self, ldap_connection):
        BaseStrategy.__init__(self, ldap_connection)
        self.sync = True
        self.no_real_dsa = False
        self.connections = []
        self._pool_size = REUSABLE_POOL_SIZE
        self._lifetime = REUSABLE_CONNECTION_LIFETIME
        self.request_queue = Queue()
        self.counter = 0
        self.create_pool()

    @property
    def pool_size(self):
        return self._pool_size

    @pool_size.setter
    def pool_size(self, value):
        self._pool_size = value

    @property
    def lifetime(self):
        return self._lifetime

    @lifetime.setter
    def lifetime(self, value):
        self._lifetime = value

    def create_pool(self):
        self.connections = [ReusableStrategy.ReusableConnection(self.connection, self.request_queue) for _ in range(self.pool_size)]

    def open(self, reset_usage=True):
        pass

    def close(self):
        pass

    def send(self, message_type, request, controls=None):
        self.counter += 1
        if self.counter > LDAP_MAX_INT:
            self.counter = 1
        self.request_queue.put((self.counter, message_type, request, controls))

        return self.counter

    def get_response(self, message_id, timeout=RESPONSE_WAITING_TIMEOUT):
        pass

    def post_send_single_response(self, counter):
        return counter

    def post_send_search(self, message_id):
        pass
