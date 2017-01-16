"""
"""

# Created on 2014.03.23
#
# Author: Giovanni Cannata
#
# Copyright 2014, 2015, 2016, 2017 Giovanni Cannata
#
# This file is part of ldap3.
#
# ldap3 is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ldap3 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ldap3 in the COPYING and COPYING.LESSER files.
# If not, see <http://www.gnu.org/licenses/>.

from datetime import datetime
from os import linesep
from threading import Thread, Lock
from time import sleep

from .. import RESTARTABLE, get_config_parameter
from .base import BaseStrategy
from ..core.usage import ConnectionUsage
from ..core.exceptions import LDAPConnectionPoolNameIsMandatoryError, LDAPConnectionPoolNotStartedError, LDAPOperationResult, LDAPExceptionError, LDAPResponseTimeoutError
from ..utils.log import log, log_enabled, ERROR, BASIC
from ..protocol.rfc4511 import LDAP_MAX_INT

TERMINATE_REUSABLE = 'TERMINATE_REUSABLE_CONNECTION'

BOGUS_BIND = -1
BOGUS_UNBIND = -2
BOGUS_EXTENDED = -3
BOGUS_ABANDON = -4

try:
    from queue import Queue
except ImportError:  # Python 2
    # noinspection PyUnresolvedReferences
    from Queue import Queue


# noinspection PyProtectedMember
class ReusableStrategy(BaseStrategy):
    """
    A pool of reusable SyncWaitRestartable connections with lazy behaviour and limited lifetime.
    The connection using this strategy presents itself as a normal connection, but internally the strategy has a pool of
    connections that can be used as needed. Each connection lives in its own thread and has a busy/available status.
    The strategy performs the requested operation on the first available connection.
    The pool of connections is instantiated at strategy initialization.
    Strategy has two customizable properties, the total number of connections in the pool and the lifetime of each connection.
    When lifetime is expired the connection is closed and will be open again when needed.
    """

    def receiving(self):
        raise NotImplementedError

    def _start_listen(self):
        raise NotImplementedError

    def _get_response(self, message_id):
        raise NotImplementedError

    def get_stream(self):
        raise NotImplementedError

    def set_stream(self, value):
        raise NotImplementedError

    pools = dict()

    # noinspection PyProtectedMember
    class ConnectionPool(object):
        """
        Container for the Connection Threads
        """
        def __new__(cls, connection):
            if connection.pool_name in ReusableStrategy.pools:  # returns existing connection pool
                pool = ReusableStrategy.pools[connection.pool_name]
                if not pool.started:  # if pool is not started remove it from the pools singleton and create a new onw
                    del ReusableStrategy.pools[connection.pool_name]
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
                self.pool_size = connection.pool_size or get_config_parameter('REUSABLE_THREADED_POOL_SIZE')
                self.lifetime = connection.pool_lifetime or get_config_parameter('REUSABLE_THREADED_LIFETIME')
                self.request_queue = Queue()
                self.open_pool = False
                self.bind_pool = False
                self.tls_pool = False
                self._incoming = dict()
                self.counter = 0
                self.terminated_usage = ConnectionUsage() if connection._usage else None
                self.terminated = False
                self.lock = Lock()
                ReusableStrategy.pools[self.name] = self
                self.started = False
                if log_enabled(BASIC):
                    log(BASIC, 'instantiated ConnectionPool: <%r>', self)

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

        def get_info_from_server(self):
            for pooled_connection_worker in self.connections:
                with pooled_connection_worker.lock:
                    pooled_connection_worker.get_info_from_server = True

        def rebind_pool(self):
            for pooled_connection_worker in self.connections:
                with pooled_connection_worker.lock:
                    pooled_connection_worker.connection.rebind(self.master_connection.user,
                                                               self.master_connection.password,
                                                               self.master_connection.authentication,
                                                               self.master_connection.sasl_mechanism,
                                                               self.master_connection.sasl_credentials)

        def start_pool(self):
            if not self.started:
                self.create_pool()
                for pooled_connection_worker in self.connections:
                    with pooled_connection_worker.lock:
                        pooled_connection_worker.thread.start()
                self.started = True
                self.terminated = False
                if log_enabled(BASIC):
                    log(BASIC, 'connection worker started for pool <%s>', self)
                return True
            return False

        def create_pool(self):
            if log_enabled(BASIC):
                log(BASIC, 'created pool <%s>', self)
            self.connections = [ReusableStrategy.PooledConnectionWorker(self.master_connection, self.request_queue) for _ in range(self.pool_size)]

        def terminate_pool(self):
            if not self.terminated:
                if log_enabled(BASIC):
                    log(BASIC, 'terminating pool <%s>', self)
                self.started = False
                self.master_schema = None
                self.master_info = None
                self.request_queue.join()  # waits for all queue pending operations
                for _ in range(len([connection for connection in self.connections if connection.thread.is_alive()])):  # put a TERMINATE signal on the queue for each active thread
                    self.request_queue.put((TERMINATE_REUSABLE, None, None, None))
                self.request_queue.join()  # waits for all queue terminate operations
                self.terminated = True
                if log_enabled(BASIC):
                    log(BASIC, 'pool terminated for <%s>', self)

    class PooledConnectionThread(Thread):
        """
        The thread that holds the Reusable connection and receive operation request via the queue
        Result are sent back in the pool._incoming list when ready
        """
        def __init__(self, pooled_connection_worker, master_connection):
            Thread.__init__(self)
            self.daemon = True
            self.worker = pooled_connection_worker
            self.master_connection = master_connection
            if log_enabled(BASIC):
                log(BASIC, 'instantiated PooledConnectionThread: <%r>', self)

        # noinspection PyProtectedMember
        def run(self):
            self.worker.running = True
            terminate = False
            pool = self.master_connection.strategy.pool
            while not terminate:
                counter, message_type, request, controls = pool.request_queue.get()
                with self.worker.lock:
                    self.worker.busy = True
                    if counter == TERMINATE_REUSABLE:
                        terminate = True
                        if self.worker.connection.bound:
                            try:
                                self.worker.connection.unbind()
                                if log_enabled(BASIC):
                                    log(BASIC, 'thread terminated')
                            except LDAPExceptionError:
                                pass
                    else:
                        if (datetime.now() - self.worker.creation_time).seconds >= self.master_connection.strategy.pool.lifetime:  # destroy and create a new connection
                            try:
                                self.worker.connection.unbind()
                            except LDAPExceptionError:
                                pass
                            self.worker.new_connection()
                            if log_enabled(BASIC):
                                log(BASIC, 'thread respawn')
                        if message_type not in ['bindRequest', 'unbindRequest']:
                            if pool.open_pool and self.worker.connection.closed:
                                self.worker.connection.open(read_server_info=False)
                                if pool.tls_pool and not self.worker.connection.tls_started:
                                    self.worker.connection.start_tls(read_server_info=False)
                                if pool.bind_pool and not self.worker.connection.bound:
                                    self.worker.connection.bind(read_server_info=False)
                            elif pool.open_pool and not self.worker.connection.closed:  # connection already open, issues a start_tls
                                if pool.tls_pool and not self.worker.connection.tls_started:
                                    self.worker.connection.start_tls(read_server_info=False)
                            if self.worker.get_info_from_server and counter:
                                self.worker.connection._fire_deferred()
                                self.worker.get_info_from_server = False
                            exc = None
                            response = None
                            result = None
                            try:
                                if message_type == 'searchRequest':
                                    response = self.worker.connection.post_send_search(self.worker.connection.send(message_type, request, controls))
                                else:
                                    response = self.worker.connection.post_send_single_response(self.worker.connection.send(message_type, request, controls))
                                result = self.worker.connection.result
                            except LDAPOperationResult as e:  # raise_exceptions has raised an exception. It must be redirected to the original connection thread
                                exc = e

                            with pool.lock:
                                if exc:
                                    pool._incoming[counter] = (exc, None)
                                else:
                                    pool._incoming[counter] = (response, result)

                    self.worker.busy = False
                    pool.request_queue.task_done()
                    self.worker.task_counter += 1
            if log_enabled(BASIC):
                log(BASIC, 'thread terminated')
            if self.master_connection.usage:
                pool.terminated_usage += self.worker.connection.usage
            self.worker.running = False

    class PooledConnectionWorker(object):
        """
        Container for the restartable connection. it includes a thread and a lock to execute the connection in the pool
        """
        def __init__(self, connection, request_queue):
            self.master_connection = connection
            self.request_queue = request_queue
            self.running = False
            self.busy = False
            self.get_info_from_server = False
            self.connection = None
            self.creation_time = None
            self.new_connection()
            self.task_counter = 0
            self.thread = ReusableStrategy.PooledConnectionThread(self, connection)
            self.lock = Lock()
            if log_enabled(BASIC):
                log(BASIC, 'instantiated PooledConnectionWorker: <%s>', self)

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
                                         client_strategy=RESTARTABLE,
                                         auto_referrals=self.master_connection.auto_referrals,
                                         auto_range=self.master_connection.auto_range,
                                         sasl_mechanism=self.master_connection.sasl_mechanism,
                                         sasl_credentials=self.master_connection.sasl_credentials,
                                         check_names=self.master_connection.check_names,
                                         collect_usage=True if self.master_connection._usage else False,
                                         read_only=self.master_connection.read_only,
                                         raise_exceptions=self.master_connection.raise_exceptions,
                                         lazy=True,
                                         fast_decoder=self.master_connection.fast_decoder,
                                         receive_timeout=self.master_connection.receive_timeout,
                                         return_empty_attributes=self.master_connection.empty_attributes)

            if self.master_connection.server_pool:
                self.connection.server_pool = self.master_connection.server_pool
                self.connection.server_pool.initialize(self.connection)

            self.creation_time = datetime.now()

    # ReusableStrategy methods
    def __init__(self, ldap_connection):
        BaseStrategy.__init__(self, ldap_connection)
        self.sync = False
        self.no_real_dsa = False
        self.pooled = True
        self.can_stream = False
        if hasattr(ldap_connection, 'pool_name') and ldap_connection.pool_name:
            self.pool = ReusableStrategy.ConnectionPool(ldap_connection)
        else:
            if log_enabled(ERROR):
                log(ERROR, 'reusable connection must have a pool_name')
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
        if self.pool.started:
            if message_type == 'bindRequest':
                self.pool.bind_pool = True
                counter = BOGUS_BIND
            elif message_type == 'unbindRequest':
                self.pool.bind_pool = False
                counter = BOGUS_UNBIND
            elif message_type == 'abandonRequest':
                counter = BOGUS_ABANDON
            elif message_type == 'extendedReq' and self.connection.starting_tls:
                self.pool.tls_pool = True
                counter = BOGUS_EXTENDED
            else:
                with self.pool.lock:
                    self.pool.counter += 1
                    if self.pool.counter > LDAP_MAX_INT:
                        self.pool.counter = 1
                    counter = self.pool.counter
                self.pool.request_queue.put((counter, message_type, request, controls))

            return counter
        if log_enabled(ERROR):
            log(ERROR, 'reusable connection pool not started')
        raise LDAPConnectionPoolNotStartedError('reusable connection pool not started')

    def validate_bind(self, controls):
        temp_connection = self.pool.connections[0].connection
        temp_connection.lazy = False
        result = self.pool.connections[0].connection.bind(controls=controls)
        temp_connection.unbind()
        temp_connection.lazy = True
        if result:
            self.pool.bind_pool = True  # bind pool if bind is validated
        return result

    def get_response(self, counter, timeout=None):
        if timeout is None:
            timeout = get_config_parameter('RESPONSE_WAITING_TIMEOUT')
        if counter == BOGUS_BIND:  # send a bogus bindResponse
            response = list()
            result = {'description': 'success', 'referrals': None, 'type': 'bindResponse', 'result': 0, 'dn': '', 'message': '<bogus Bind response>', 'saslCreds': None}
        elif counter == BOGUS_UNBIND:  # bogus unbind response
            response = None
            result = None
        elif counter == BOGUS_ABANDON:  # abandon cannot be executed because of multiple connections
            response = list()
            result = {'result': 0, 'referrals': None, 'responseName': '1.3.6.1.4.1.1466.20037', 'type': 'extendedResp', 'description': 'success', 'responseValue': 'None', 'dn': '', 'message': '<bogus StartTls response>'}
        elif counter == BOGUS_EXTENDED:  # bogus startTls extended response
            response = list()
            result = {'result': 0, 'referrals': None, 'responseName': '1.3.6.1.4.1.1466.20037', 'type': 'extendedResp', 'description': 'success', 'responseValue': 'None', 'dn': '', 'message': '<bogus StartTls response>'}
            self.connection.starting_tls = False
        else:
            response = None
            result = None
            while timeout >= 0:  # waiting for completed message to appear in _incoming
                try:
                    with self.connection.strategy.pool.lock:
                        response, result = self.connection.strategy.pool._incoming.pop(counter)
                except KeyError:
                    sleep(get_config_parameter('RESPONSE_SLEEPTIME'))
                    timeout -= get_config_parameter('RESPONSE_SLEEPTIME')
                    continue
                break

            if timeout <= 0:
                if log_enabled(ERROR):
                    log(ERROR, 'no response from worker threads in Reusable connection')
                raise LDAPResponseTimeoutError('no response from worker threads in Reusable connection')

        if isinstance(response, LDAPOperationResult):
            raise response  # an exception has been raised with raise_connections

        return response, result

    def post_send_single_response(self, counter):
        return counter

    def post_send_search(self, counter):
        return counter
