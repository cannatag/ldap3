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
from queue import Queue
from threading import Thread, Lock
from .baseStrategy import BaseStrategy
from ldap3 import REUSABLE_POOL_SIZE, REUSABLE_CONNECTION_LIFETIME, STRATEGY_SYNC_RESTARTABLE
from ..core.connection import Connection


class SyncWaitStrategy(BaseStrategy):
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
        def __init__(self, queue, pooled_connection):
            Thread.__init__(self)
            self.pooled_connection = pooled_connection
            self.operation_queue = self.pooled_connection.queue

        def run(self):
            self.pooled_connection.running = True
            print(self, self.command_queue)
            while not self.exit:
                operation = self.operation_queue.get()
                print(self, 'unlocked!', operation)
            print(self, 'exiting')
            self.pooled_connection.running = False

    class ReusableConnection(object):
        """
        Container for the Restartable connection. it includes a thread and a lock to execute the connection in the pool
        """
        def __init__(self, connection, queue):
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
            self.creation_time = datetime.now()
            self.thread = SyncWaitStrategy.PooledConnectionThread()
            self.queue = queue
            self.exit = False

        def __str__(self):
            s = str(self.connection)



    def __init__(self, ldap_connection):
        BaseStrategy.__init__(self, ldap_connection)
        self.sync = True
        self.no_real_dsa = False
        self.connections = []
        self._pool_size = REUSABLE_POOL_SIZE
        self._lifetime = REUSABLE_CONNECTION_LIFETIME
        self.queue = Queue()
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

    @pool_size.setter
    def lifetime(self, value):
        self._lifetime = value

    def create_pool(self):
        self.connections = [SyncWaitStrategy.ReusableConnection(self.connection, self.queue) for _ in range(self.pool_size)]
