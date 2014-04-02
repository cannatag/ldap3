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
from ldap3 import REUSABLE_POOL_SIZE, REUSABLE_CONNECTION_LIFETIME, STRATEGY_SYNC_RESTARTABLE, TERMINATE_REUSABLE, RESPONSE_WAITING_TIMEOUT, LDAP_MAX_INT, LDAPException, RESPONSE_COMPLETE, RESPONSE_SLEEPTIME


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
    pools = dict()

    class ConnectionPool(object):
        def __new__(cls, connection):
            if connection.pool_name in ReusableStrategy.pools:
                return ReusableStrategy.pools[connection.pool_name]
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
                self.response_queue = Queue()
                self.create_pool()
                self.open_pool = False
                self.bind_pool = False
                self._incoming = dict()
                self.lock = Lock
                ReusableStrategy.pools[self.name] = self
                self.started = False

        def __str__(self):
            s = self.name
            s += ' - pool size: ' + str(self.pool_size)
            s += ' - lifetime: ' + str(self.lifetime)
            s += ' - ' + 'open: ' + str(self.open_pool)
            s += ' - ' + 'bind: ' + str(self.bind_pool)
            for connection in self.connections:
                s += linesep
                s += str(connection)

            return s

        def start_pool(self):
            if not self.started:
                for connection in self.connections:
                    connection.thread.start()
                return True
            return False

        def __repr__(self):
            return self.__str__()

        def create_pool(self):
            self.connections = [ReusableStrategy.ReusableConnection(self.original_connection, self.request_queue, self.response_queue) for _ in range(self.pool_size)]

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
                (counter, message_type, request, controls) = pool.request_queue.get()
                print(self, 'got request', message_type)
                self.active_connection.busy = True
                if message_type == TERMINATE_REUSABLE and not self.active_connection.cannot_terminate:
                    terminate = True
                else:
                    if pool.open_pool and self.active_connection.connection.closed:
                        print(self, 'opening')
                        self.active_connection.connection.open()
                    if pool.bind_pool and not self.active_connection.connection.bound:
                        print(self, 'binding')
                        self.active_connection.connection.bind()
                    print(self, '***')
                    print(self, self.active_connection)
                    print(self, '***')
                    print(self, 'sending', request)
                    result = self.active_connection.connection.send(message_type, request, controls)
                    print(self, 'receiving', result)
                    with pool.lock:
                        pool._incoming[counter] = result
                self.active_connection.busy = False
            self.active_connection.running = False
            print(self, 'exiting')

    class ReusableConnection(object):
        """
        Container for the Restartable connection. it includes a thread and a lock to execute the connection in the pool
        """
        def __init__(self, connection, request_queue, response_queue):
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
            self.creation_time = datetime.now()
            self.thread = ReusableStrategy.PooledConnectionThread(self, connection)

        def __str__(self):
            s = str(self.connection) + linesep
            s += 'running ' if self.running else '-halted'
            s += ' - ' + ('busy' if self.busy else ' available')
            s += ' - ' + ('creation time: ' + self.creation_time.isoformat())

            return s

    def __init__(self, ldap_connection):
        BaseStrategy.__init__(self, ldap_connection)
        self.sync = False
        self.no_real_dsa = False
        if hasattr(ldap_connection, 'pool_name') and ldap_connection.pool_name:
            self.pool = ReusableStrategy.ConnectionPool(ldap_connection)
        else:
            raise LDAPException('reusable connection must have a pool_name')

        self.counter = 0

    def open(self, reset_usage=True):
        self.pool.open_pool = True
        self.pool.start_pool()

    def close(self):
        self.pool.open_pool = False

    def send(self, message_type, request, controls=None):
        print('sending', message_type)
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

    def get_response(self, counter, timeout=RESPONSE_WAITING_TIMEOUT):
        if counter == -1:  # send a bogus bindResponse
            return list(), {'description': 'success', 'referrals': None, 'type': 'bindResponse', 'result': 0, 'dn': '', 'message': '', 'saslCreds': 'None'}
        response = None
        result = None
        if self.connection.strategy.pool._incoming:
            while timeout >= 0:  # waiting for completed message to appear in _incoming
                responses = self.connection.strategy.pool._outstanding.pop(counter)
                if not responses:
                    sleep(RESPONSE_SLEEPTIME)
                    timeout -= RESPONSE_SLEEPTIME
                else:
                    if responses:
                        result = responses[-2]
                        response = [responses[0]] if len(responses) == 2 else responses[:-1]  # remove the response complete flag
                    break
        return response, result

    def post_send_single_response(self, counter):
        print('post_send_single_response', counter)
        return counter

    def post_send_search(self, counter):
        return counter
