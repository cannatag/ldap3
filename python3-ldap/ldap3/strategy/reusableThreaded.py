"""
"""

# Created on 2014.03.23
#
# Author: Giovanni Cannata
#
# Copyright 2013 Giovanni Cannata
#
# This file is part of python3-ldap.
#
# python3-ldap is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python3-ldap is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with python3-ldap in the COPYING and COPYING.LESSER files.
# If not, see <http://www.gnu.org/licenses/>.

from datetime import datetime
from os import linesep
from threading import Thread, Lock
from time import sleep
from .. import REUSABLE_THREADED_POOL_SIZE, REUSABLE_THREADED_LIFETIME, STRATEGY_SYNC_RESTARTABLE, TERMINATE_REUSABLE, RESPONSE_WAITING_TIMEOUT, LDAP_MAX_INT, RESPONSE_SLEEPTIME
from .baseStrategy import BaseStrategy
from ..core.usage import ConnectionUsage
from ..core.exceptions import LDAPConnectionPoolNameIsMandatoryError, LDAPConnectionPoolNotStartedError, LDAPOperationResult, LDAPExceptionError

try:
    from queue import Queue
except ImportError:  # Python 2
    # noinspection PyUnresolvedReferences
    from Queue import Queue


# noinspection PyProtectedMember
class ReusableThreadedStrategy(BaseStrategy):
    """
    A pool of reusable SyncWaitRestartable connections with lazy behaviour and limited lifetime.
    The connection using this strategy presents itself as a normal connection, but internally the strategy has a pool of
    connections that can be used as needed. Each connection lives in its own thread and has a busy/available status.
    The strategy performs the requested operation on the first available connection.
    The pool of connections is instantiated at strategy initialization.
    Strategy has two customizable properties, the total number of connections in the pool and the lifetime of each connection.
    When lifetime is expired the connection is closed and will be open again when needed.
    """
    pools = dict()

    # noinspection PyProtectedMember
    class ConnectionPool(object):
        """
        Container for the Connection Threads
        """
        def __new__(cls, connection):
            if connection.pool_name in ReusableThreadedStrategy.pools:  # returns existing connection pool
                pool = ReusableThreadedStrategy.pools[connection.pool_name]
                if not pool.started:  # if pool is not started remove it from the pools singleton and create a new onw
                    del ReusableThreadedStrategy.pools[connection.pool_name]
                    return object.__new__(cls)
                if connection.pool_lifetime and pool.lifetime != connection.pool_lifetime:  # change lifetime
                    pool.lifetime = connection.pool_lifetime
                if connection.pool_size and pool.pool_size != connection.pool_size:  # if pool size has changed terminate and recreate the connections
                    pool.terminate_pool()
                    pool.pool_size = connection.pool_size
                return pool
            else:
                return object.__new__(cls)

        def __init__(self, connection):
            if not hasattr(self, 'connections'):
                self.name = connection.pool_name
                self.master_connection = connection
                self.master_schema = None
                self.master_info = None
                self.connections = []
                self.pool_size = connection.pool_size or REUSABLE_THREADED_POOL_SIZE
                self.lifetime = connection.pool_lifetime or REUSABLE_THREADED_LIFETIME
                self.request_queue = Queue()
                self.open_pool = False
                self.bind_pool = False
                self.tls_pool = False
                self._incoming = dict()
                self.counter = 0
                self.terminated_usage = ConnectionUsage() if connection._usage else None
                self.terminated = False
                self.lock = Lock()
                ReusableThreadedStrategy.pools[self.name] = self
                self.started = False

        def __str__(self):
            s = 'POOL: ' + str(self.name) + ' - status: ' + ('started' if self.started else 'terminated')
            s += ' - responses in queue: ' + str(len(self._incoming))
            s += ' - pool size: ' + str(self.pool_size)
            s += ' - lifetime: ' + str(self.lifetime)
            s += ' - open: ' + str(self.open_pool)
            s += ' - bind: ' + str(self.bind_pool)
            s += ' - tls: ' + str(self.tls_pool) + linesep
            s += 'MASTER CONN: ' + str(self.master_connection) + linesep
            s += 'CONNECTIONS:'
            if self.connections:
                for i, connection in enumerate(self.connections):
                    s += linesep + str(i).rjust(5) + ': ' + str(connection)
            else:
                s += linesep + '    no active connections in pool'

            return s

        def __repr__(self):
            return self.__str__()

        def start_pool(self):
            if not self.started:
                self.create_pool()
                for inner_connection in self.connections:
                    inner_connection.thread.start()
                self.started = True
                return True
            return False

        def fire_deferred_in_pool(self):
            for inner_connection in self.connections:
                inner_connection.connection._fire_deferred()

        def create_pool(self):
            self.connections = [ReusableThreadedStrategy.InnerConnection(self.master_connection, self.request_queue) for _ in range(self.pool_size)]

        def terminate_pool(self):
            self.started = False
            self.master_schema = None
            self.master_info = None
            self.request_queue.join()  # wait for all queue pending operations

            for _ in range(len([connection for connection in self.connections if connection.thread.is_alive()])):  # put a TERMINATE signal on the queue for each active thread
                self.request_queue.put((TERMINATE_REUSABLE, None, None, None))

            self.request_queue.join()  # wait for all queue terminate operations

    class PooledConnectionThread(Thread):
        """
        The thread that holds the Reusable connection and receive operation request via the queue
        Result are sent back in the pool._incoming list when ready
        """
        def __init__(self, inner_connection, master_connection):
            Thread.__init__(self)
            self.daemon = True
            self.active_thread = inner_connection
            self.master_connection = master_connection


        # noinspection PyProtectedMember
        def run(self):
            self.active_thread.running = True
            terminate = False
            pool = self.master_connection.strategy.pool
            while not terminate:
                counter, message_type, request, controls = pool.request_queue.get()
                self.active_thread.busy = True
                if counter == TERMINATE_REUSABLE:
                    terminate = True
                    if self.active_thread.connection.bound:
                        try:
                            self.active_thread.connection.unbind()
                        except LDAPExceptionError:
                            pass
                else:
                    if (datetime.now() - self.active_thread.creation_time).seconds >= self.master_connection.strategy.pool.lifetime:  # destroy and create a new connection
                        try:
                            self.active_thread.connection.unbind()
                        except LDAPExceptionError:
                            pass
                        self.active_thread.new_connection()
                    if message_type not in ['bindRequest', 'unbindRequest']:
                        if pool.open_pool and self.active_thread.connection.closed:
                            self.active_thread.connection.open(read_server_info=False)
                            if pool.tls_pool and not self.active_thread.connection.tls_started:
                                self.active_thread.connection.start_tls(read_server_info=False)
                            if pool.bind_pool and not self.active_thread.connection.bound:
                                self.active_thread.connection.bind(read_server_info=False)
                        # noinspection PyProtectedMember
                        #print('FIRE DEFERRED FROM INNER CONNECTION')
                        self.active_thread.connection._fire_deferred()  # force deferred operations
                        # with self.master_connection.lock:
                        #    pool.master_schema = self.active_thread.connection.server.schema
                        #    pool.master_info = self.active_thread.connection.server.info
                        exc = None
                        response = None
                        result = None
                        print('CONN SEND', message_type)
                        try:
                            if message_type == 'searchRequest':
                                response = self.active_thread.connection.post_send_search(self.active_thread.connection.send(message_type, request, controls))
                            else:
                                response = self.active_thread.connection.post_send_single_response(self.active_thread.connection.send(message_type, request, controls))
                            result = self.active_thread.connection.result
                        except LDAPOperationResult as e:  # raise_exceptions has raise an exception. It must be redirected to the original connection thread
                            exc = e

                        with pool.lock:
                            if exc:
                                pool._incoming[counter] = (exc, None)
                            else:
                                pool._incoming[counter] = (response, result)
                self.active_thread.busy = False
                pool.request_queue.task_done()
                self.active_thread.task_counter += 1
            if self.master_connection.usage:
                pool.terminated_usage += self.active_thread.connection.usage
            self.active_thread.running = False

    class InnerConnection(object):
        """
        Container for the restartable connection. it includes a thread and a lock to execute the connection in the pool
        """
        def __init__(self, connection, request_queue):
            self.master_connection = connection
            self.request_queue = request_queue
            self.running = False
            self.busy = False
            self.connection = None
            self.creation_time = None
            self.new_connection()
            self.task_counter = 0
            self.thread = ReusableThreadedStrategy.PooledConnectionThread(self, connection)

        def __str__(self):
            s = 'CONN: ' + str(self.connection) + linesep + '       THREAD: '
            s += 'running' if self.running else 'halted'
            s += ' - ' + ('busy' if self.busy else 'available')
            s += ' - ' + ('created at: ' + self.creation_time.isoformat())
            s += ' - time to live: ' + str(self.master_connection.strategy.pool.lifetime - (datetime.now() - self.creation_time).seconds)
            s += ' - requests served: ' + str(self.task_counter)

            return s

        def new_connection(self):
            from ..core.connection import Connection
            # noinspection PyProtectedMember
            self.connection = Connection(server=self.master_connection.server_pool if self.master_connection.server_pool else self.master_connection.server,
                                         user=self.master_connection.user,
                                         password=self.master_connection.password,
                                         auto_bind=self.master_connection.auto_bind,
                                         version=self.master_connection.version,
                                         authentication=self.master_connection.authentication,
                                         client_strategy=STRATEGY_SYNC_RESTARTABLE,
                                         auto_referrals=self.master_connection.auto_referrals,
                                         auto_range=self.master_connection.auto_range,
                                         sasl_mechanism=self.master_connection.sasl_mechanism,
                                         sasl_credentials=self.master_connection.sasl_credentials,
                                         check_names=self.master_connection.check_names,
                                         collect_usage=True if self.master_connection._usage else False,
                                         read_only=self.master_connection.read_only,
                                         raise_exceptions=self.master_connection.raise_exceptions,
                                         lazy=True)

            if self.master_connection.server_pool:
                self.connection.server_pool = self.master_connection.server_pool
                self.connection.server_pool.initialize(self.connection)

            self.creation_time = datetime.now()

    def __init__(self, ldap_connection):
        BaseStrategy.__init__(self, ldap_connection)
        self.sync = False
        self.no_real_dsa = False
        self.pooled = True
        self.can_stream = False
        if hasattr(ldap_connection, 'pool_name') and ldap_connection.pool_name:
            self.pool = ReusableThreadedStrategy.ConnectionPool(ldap_connection)
        else:
            raise LDAPConnectionPoolNameIsMandatoryError('reusable connection must have a pool_name')

    def open(self, reset_usage=True, read_server_info=True):
        self.pool.open_pool = True
        self.pool.start_pool()
        self.connection.closed = False
        if self.connection.usage:
            if reset_usage or not self.connection._usage.initial_connection_start_time:
                self.connection._usage.start()

    def terminate(self):
        self.pool.terminate_pool()
        self.pool.open_pool = False
        self.connection.bound = False
        self.connection.closed = True
        self.pool.bind_pool = False
        self.pool.tls_pool = False

    def _close_socket(self):
        """
        Doesn't really close the socket
        """
        self.connection.closed = True

        if self.connection.usage:
            self.connection._usage.closed_sockets += 1

    def send(self, message_type, request, controls=None):
        print('MASTER SEND', message_type)
        if self.pool.started:
            if message_type == 'bindRequest':
                self.pool.bind_pool = True
                counter = -1  # -1 stands for bind request
            elif message_type == 'unbindRequest':
                self.pool.bind_pool = False
                counter = -2  # -1 stands for unbind request
            elif message_type == 'extendedReq' and self.connection.starting_tls:
                self.pool.tls_pool = True
                counter = -3  # -1 stands for start_tls extended request
            else:
                with self.pool.lock:
                    self.pool.counter += 1
                    if self.pool.counter > LDAP_MAX_INT:
                        self.pool.counter = 1
                    counter = self.pool.counter
                self.pool.request_queue.put((counter, message_type, request, controls))

            return counter
        raise LDAPConnectionPoolNotStartedError('reusable connection pool not started')

    def get_response(self, counter, timeout=RESPONSE_WAITING_TIMEOUT):
        if counter == -1:  # send a bogus bindResponse
            return list(), {'description': 'success', 'referrals': None, 'type': 'bindResponse', 'result': 0, 'dn': '', 'message': '', 'saslCreds': 'None'}
        elif counter == -2:  # bogus unbind
            return None
        elif counter == -3:  # bogus startTls extended request
            return list(), {'result': 0, 'referrals': None, 'responseName': '1.3.6.1.4.1.1466.20037', 'type': 'extendedResp', 'description': 'success', 'responseValue': 'None', 'dn': '', 'message': ''}
        response = None
        result = None
        while timeout >= 0:  # waiting for completed message to appear in _incoming
            try:
                with self.connection.strategy.pool.lock:
                    response, result = self.connection.strategy.pool._incoming.pop(counter)

            except KeyError:
                sleep(RESPONSE_SLEEPTIME)
                timeout -= RESPONSE_SLEEPTIME
                continue
            break

        if isinstance(response, LDAPOperationResult):
            raise response  # an exception has been raised with raise_connections
        return response, result

    def post_send_single_response(self, counter):
        return counter

    def post_send_search(self, counter):
        return counter
