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
from threading import Thread, Lock
from time import sleep

try:
    from queue import Queue
except ImportError:  # Python 2
    # noinspection PyUnresolvedReferences
    from Queue import Queue

from .baseStrategy import BaseStrategy
from ldap3 import REUSABLE_POOL_SIZE, REUSABLE_CONNECTION_LIFETIME, STRATEGY_SYNC_RESTARTABLE, TERMINATE_REUSABLE, RESPONSE_WAITING_TIMEOUT, LDAP_MAX_INT, LDAPException, RESPONSE_SLEEPTIME


class ReusableThreadedStrategy(BaseStrategy):
    """
    A pool of reusable SyncWaitRestartable connections with lazy behaviour and limited lifetime.
    The connection using this strategy presents itself as a normal connection, but internally the strategy has a pool of
    connections that can be used as needed. Each connection lives in its own thread and has a busy/available status. The strategy performs the requested
    operation on the first available connection.
    The pool of connections is instantiated at strategy initialization.
    Strategy has two settable properties, the total number of connection present in the pool and the lifetime of each connection.
    When lifetime is expired the connection is closed and will be opened again when needed
    """
    pools = dict()

    class ConnectionPool(object):
        def __new__(cls, connection):
            if connection.pool_name in ReusableThreadedStrategy.pools:
                return ReusableThreadedStrategy.pools[connection.pool_name]
            else:
                return object.__new__(cls)

        def __init__(self, connection):
            if not hasattr(self, 'connections'):
                self.name = connection.pool_name
                self.original_connection = connection
                self.connections = []
                self.pool_size = REUSABLE_POOL_SIZE
                self.lifetime = REUSABLE_CONNECTION_LIFETIME
                self.request_queue = Queue()
                self.open_pool = False
                self.bind_pool = False
                self._incoming = dict()
                self.lock = Lock()
                ReusableThreadedStrategy.pools[self.name] = self
                self.started = False

        def __str__(self):
            s = str(self.name)
            s += ' - pool size: ' + str(self.pool_size)
            s += ' - lifetime: ' + str(self.lifetime)
            s += ' - ' + 'open: ' + str(self.open_pool)
            s += ' - ' + 'bind: ' + str(self.bind_pool)
            for connection in self.connections:
                s += linesep
                s += str(connection)

            return s

        def __repr__(self):
            return self.__str__()

        def start_pool(self):
            if not self.started:
                self.create_pool()
                for connection in self.connections:
                    connection.thread.start()
                self.started = True
                return True
            return False

        def create_pool(self):
            self.connections = [ReusableThreadedStrategy.ReusableConnection(self.original_connection, self.request_queue) for _ in range(self.pool_size)]

        def terminate_pool(self):
            self.started = False
            self.request_queue.join()  # wait for all queue pending operations

            for _ in range(len([connection for connection in self.connections if connection.thread.is_alive()])):  # put a TERMINATE signal on the queue for each active thread
                self.request_queue.put((TERMINATE_REUSABLE, None, None, None))

            self.request_queue.join()  # wait for all queue terminate operations

    class PooledConnectionThread(Thread):
        def __init__(self, reusable_connection, original_connection):
            Thread.__init__(self)
            self.daemon = True
            self.active_connection = reusable_connection
            self.original_connection = original_connection

        def run(self):
            self.active_connection.running = True
            terminate = False
            pool = self.original_connection.strategy.pool
            while not terminate:
                counter, message_type, request, controls = pool.request_queue.get()
                self.active_connection.busy = True
                if datetime.now() - self.active_connection.creation_time > self.original_connection.strategy.pool.lifetime:  # destroy and create a new connection
                    self.active_connection.connection.unbind()
                    self.active_connection.new_connection()
                if counter == TERMINATE_REUSABLE and not self.active_connection.cannot_terminate:
                    terminate = True
                    if self.active_connection.connection.bound:
                        self.active_connection.connection.unbind()
                else:
                    if message_type not in ['bindRequest', 'unbindRequest']:
                        if pool.open_pool and self.active_connection.connection.closed:
                            self.active_connection.connection.open()
                        if pool.bind_pool and not self.active_connection.connection.bound:
                            self.active_connection.connection.bind()
                        self.active_connection.connection._fire_deferred()  # force deferred operations
                        if message_type == 'searchRequest':
                            result = self.active_connection.connection.post_send_search(self.active_connection.connection.send(message_type, request, controls))
                        else:
                            result = self.active_connection.connection.post_send_single_response(self.active_connection.connection.send(message_type, request, controls))
                        with pool.lock:
                            pool._incoming[counter] = result
                self.active_connection.busy = False
                pool.request_queue.task_done()
            self.active_connection.running = False

    class ReusableConnection(object):
        """
        Container for the Restartable connection. it includes a thread and a lock to execute the connection in the pool
        """
        def __init__(self, connection, request_queue):

            self.original_connection = connection
            self.request_queue = request_queue
            self.running = False
            self.busy = False
            self.cannot_terminate = False
            self.connection = None
            self.creation_time = None
            self.new_connection()
            self.thread = ReusableThreadedStrategy.PooledConnectionThread(self, connection)

        def __str__(self):
            s = str(self.connection) + linesep
            s += 'running ' if self.running else '-halted'
            s += ' - ' + ('busy' if self.busy else ' available')
            s += ' - ' + ('creation time: ' + self.creation_time.isoformat())

            return s

        def new_connection(self):
            from ldap3 import Connection
            self.connection = Connection(server=self.original_connection.server_pool if self.original_connection.server_pool else self.original_connection.server,
                                         user=self.original_connection.user,
                                         password=self.original_connection.password,
                                         version=self.original_connection.version,
                                         authentication=self.original_connection.authentication,
                                         client_strategy=STRATEGY_SYNC_RESTARTABLE,
                                         auto_referrals=self.original_connection.auto_referrals,
                                         sasl_mechanism=self.original_connection.sasl_mechanism,
                                         sasl_credentials=self.original_connection.sasl_credentials,
                                         collect_usage=True if self.original_connection.usage else False,
                                         read_only=self.original_connection.read_only,
                                         lazy=True)

            if self.original_connection.server_pool:
                self.connection.server_pool = self.original_connection.server_pool
                self.connection.server_pool.initialize(self.connection)

            self.creation_time = datetime.now()

    def __init__(self, ldap_connection):
        BaseStrategy.__init__(self, ldap_connection)
        self.sync = False
        self.no_real_dsa = False
        if hasattr(ldap_connection, 'pool_name') and ldap_connection.pool_name:
            self.pool = ReusableThreadedStrategy.ConnectionPool(ldap_connection)
        else:
            raise LDAPException('reusable connection must have a pool_name')

        self.counter = 0

    def open(self, reset_usage=True):
        self.pool.open_pool = True
        self.pool.start_pool()

    def terminate(self):
        self.pool.terminate_pool()
        self.pool.open_pool = False

    def send(self, message_type, request, controls=None):
        if self.pool.started:
            if message_type == 'bindRequest':
                self.pool.bind_pool = True
                return -1  # -1 stands for bind request
            elif message_type == 'unbindRequest':
                self.pool.bind_pool = False
            else:
                self.counter += 1
                if self.counter > LDAP_MAX_INT:
                    self.counter = 1

                self.pool.request_queue.put((self.counter, message_type, request, controls))

            return self.counter

        raise LDAPException('connection pool not started')

    def get_response(self, counter, timeout=RESPONSE_WAITING_TIMEOUT):
        if counter == -1:  # send a bogus bindResponse
            return list(), {'description': 'success', 'referrals': None, 'type': 'bindResponse', 'result': 0, 'dn': '', 'message': '', 'saslCreds': 'None'}
        response = None
        result = None
        while timeout >= 0:  # waiting for completed message to appear in _incoming
            try:
                responses = self.connection.strategy.pool._incoming.pop(counter)
            except KeyError:
                sleep(RESPONSE_SLEEPTIME)
                timeout -= RESPONSE_SLEEPTIME
                continue

            result = responses[-2]
            response = [responses[0]] if len(responses) == 2 else responses[:-1]  # remove the response complete flag
            break
        return response, result

    def post_send_single_response(self, counter):
        return counter

    def post_send_search(self, counter):
        return counter
