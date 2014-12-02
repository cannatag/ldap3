"""
"""

# Created on 2014.05.31
#
# Author: Giovanni Cannata
#
# Copyright 2014 Giovanni Cannata
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

from os import linesep
from threading import RLock
from pyasn1.codec.ber import encoder
import json

from .. import AUTH_ANONYMOUS, AUTH_SIMPLE, AUTH_SASL, MODIFY_ADD, MODIFY_DELETE, MODIFY_REPLACE, \
    SEARCH_DEREFERENCE_ALWAYS, SEARCH_SCOPE_WHOLE_SUBTREE, STRATEGY_ASYNC_THREADED, STRATEGY_SYNC, \
    CLIENT_STRATEGIES, RESULT_SUCCESS, RESULT_COMPARE_TRUE, NO_ATTRIBUTES, ALL_ATTRIBUTES, \
    ALL_OPERATIONAL_ATTRIBUTES, MODIFY_INCREMENT, STRATEGY_LDIF_PRODUCER, SASL_AVAILABLE_MECHANISMS, \
    STRATEGY_SYNC_RESTARTABLE, POOLING_STRATEGY_ROUND_ROBIN, STRATEGY_REUSABLE_THREADED, \
    DEFAULT_THREADED_POOL_NAME, AUTO_BIND_NONE, AUTO_BIND_TLS_BEFORE_BIND, AUTO_BIND_TLS_AFTER_BIND, \
    AUTO_BIND_NO_TLS, STRING_TYPES, SEQUENCE_TYPES, STRATEGY_SYNC_MOCK_DSA, STRATEGY_ASYNC_MOCK_DSA, \
    SEARCH_SCOPE_BASE_OBJECT

from ..extend import ExtendedOperationsRoot
from .pooling import ServerPool
from .server import Server
from ..strategy.reusableThreaded import ReusableThreadedStrategy
from ..operation.abandon import abandon_operation
from ..operation.add import add_operation
from ..operation.bind import bind_operation
from ..operation.compare import compare_operation
from ..operation.delete import delete_operation
from ..operation.extended import extended_operation
from ..operation.modify import modify_operation
from ..operation.modifyDn import modify_dn_operation
from ..operation.search import search_operation
from ..protocol.rfc2849 import operation_to_ldif, add_ldif_header
from ..protocol.sasl.digestMd5 import sasl_digest_md5
from ..protocol.sasl.external import sasl_external
from ..strategy.asyncThreaded import AsyncThreadedStrategy
from ..strategy.ldifProducer import LdifProducerStrategy
from ..strategy.syncWait import SyncWaitStrategy
from ..strategy.syncWaitRestartable import SyncWaitRestartableStrategy
from ..strategy.syncMockDsa import SyncMockDsaStrategy
from ..strategy.asyncMockDsa import AsyncMockDsaStrategy
from ..operation.unbind import unbind_operation
from ..protocol.rfc2696 import RealSearchControlValue, Cookie, Size
from .usage import ConnectionUsage
from .tls import Tls
from .exceptions import LDAPUnknownStrategyError, LDAPBindError, LDAPUnknownAuthenticationMethodError, LDAPInvalidServerError, LDAPSASLMechanismNotSupportedError, LDAPObjectClassError, LDAPConnectionIsReadOnlyError, LDAPChangesError, LDAPExceptionError
from ..utils.conv import prepare_for_stream, check_json_dict, format_json


def _format_socket_endpoint(endpoint):
    if endpoint and len(endpoint) == 2:
        return str(endpoint[0]) + ':' + str(endpoint[1])
    else:
        return endpoint

# noinspection PyProtectedMember
class Connection(object):
    """Main ldap connection class.

    Controls, if used, must be a list of tuples. Each tuple must have 3
    elements, the control OID, a boolean meaning if the control is
    critical, a value.

    If the boolean is set to True the server must honor the control or
    refuse the operation

    Mixing controls must be defined in controls specification (as per
    RFC 4511)

    :param server: the Server object to connect to
    :type server: Server, str
    :param user: the user name for simple authentication
    :type user: str
    :param password: the password for simple authentication
    :type password: str
    :param auto_bind: specify if the bind will be performed automatically when defining the Connection object
    :type auto_bind: int, can be one of AUTO_BIND_NONE, AUTO_BIND_NO_TLS, AUTO_BIND_TLS_BEFORE_BIND, AUTO_BIND_TLS_AFTER_BIND as specified in ldap3
    :param version: LDAP version, default to 3
    :type version: int
    :param authentication: type of authentication
    :type authentication: int, can be one of AUTH_ANONYMOUS, AUTH_SIMPLE or AUTH_SASL, as specified in ldap3
    :param client_strategy: communication strategy used in the Connection
    :type client_strategy: can be one of STRATEGY_SYNC, STRATEGY_ASYNC_THREADED, STRATEGY_LDIF_PRODUCER, STRATEGY_SYNC_RESTARTABLE, STRATEGY_REUSABLE_THREADED as specified in ldap3
    :param auto_referrals: specify if the connection object must automatically follow referrals
    :type auto_referrals: bool
    :param sasl_mechanism: mechanism for SASL authentication, can be one of 'EXTERNAL', 'DIGEST-MD5'
    :type sasl_mechanism: str
    :param sasl_credentials: credentials for SASL mechanism
    :type sasl_credentials: tuple
    :param check_names: if True the library will check names of attributes and object classes against the schema. Also values found in entries will be formatted as indicated by the schema
    :type check_names: bool
    :param collect_usage: collect usage metrics in the usage attribute
    :type collect_usage: bool
    :param read_only: disable operations that modify data in the LDAP server
    :type read_only: bool
    :param lazy: open and bind the connection only when an actual operation is performed
    :type lazy: bool
    :param raise_exceptions: raise exceptions when operations are not successful, if False operations return False if not successful but not raise exceptions
    :type raise_exceptions: bool
    :param pool_name: pool name for pooled strategies
    :type pool_name: str
    :param pool_size: pool size for pooled strategies
    :type pool_size: int
    :param pool_lifetime: pool lifetime for pooled strategies
    :type pool_size: int

    """

    def __init__(self,
                 server,
                 user=None,
                 password=None,
                 auto_bind=AUTO_BIND_NONE,
                 version=3,
                 authentication=None,
                 client_strategy=STRATEGY_SYNC,
                 auto_referrals=True,
                 auto_range=False,
                 sasl_mechanism=None,
                 sasl_credentials=None,
                 check_names=True,
                 collect_usage=False,
                 read_only=False,
                 lazy=False,
                 raise_exceptions=False,
                 pool_name=None,
                 pool_size=None,
                 pool_lifetime=None):

        self.lock = RLock()
        with self.lock:
            if client_strategy not in CLIENT_STRATEGIES:
                self.last_error = 'unknown client connection strategy'
                raise LDAPUnknownStrategyError(self.last_error)

            self.strategy_type = client_strategy
            self.user = user
            self.password = password
            if self.user and self.password and not authentication:
                self.authentication = AUTH_SIMPLE
            elif not authentication:
                self.authentication = AUTH_ANONYMOUS
            elif authentication in [AUTH_SIMPLE, AUTH_ANONYMOUS, AUTH_SASL]:
                self.authentication = authentication
            else:
                self.last_error = 'unknown authentication method'
                raise LDAPUnknownAuthenticationMethodError(self.last_error)
            self.version = version
            self.auto_referrals = True if auto_referrals else False
            self.request = None
            self.response = None
            self.result = None
            self.bound = False
            self.listening = False
            self.closed = True
            self.last_error = None
            if auto_bind is False:  # compatibility with older versione where auto_bind was a boolean
                self.auto_bind = AUTO_BIND_NONE
            elif auto_bind is True:
                self.auto_bind = AUTO_BIND_NO_TLS
            else:
                self.auto_bind = auto_bind
            self.sasl_mechanism = sasl_mechanism
            self.sasl_credentials = sasl_credentials
            self._usage = ConnectionUsage() if collect_usage else None
            self.socket = None
            self.tls_started = False
            self.sasl_in_progress = False
            self.read_only = read_only
            self._context_state = []
            self._deferred_open = False
            self._deferred_bind = False
            self._deferred_start_tls = False
            self._bind_controls = None
            self._executing_deferred = False
            self.lazy = lazy
            self.pool_name = pool_name if pool_name else DEFAULT_THREADED_POOL_NAME
            self.pool_size = pool_size
            self.pool_lifetime = pool_lifetime
            self.starting_tls = False
            self.check_names = check_names
            self.raise_exceptions = raise_exceptions
            self.auto_range = True if auto_range else False
            self.extend = ExtendedOperationsRoot(self)

            if isinstance(server, STRING_TYPES):
                server = Server(server)
            if isinstance(server, SEQUENCE_TYPES):
                server = ServerPool(server, POOLING_STRATEGY_ROUND_ROBIN, active=True, exhaust=True)

            if isinstance(server, ServerPool):
                self.server_pool = server
                self.server_pool.initialize(self)
                self.server = self.server_pool.get_current_server(self)
            else:
                self.server_pool = None
                self.server = server

            if self.strategy_type == STRATEGY_SYNC:
                self.strategy = SyncWaitStrategy(self)
            elif self.strategy_type == STRATEGY_ASYNC_THREADED:
                self.strategy = AsyncThreadedStrategy(self)
            elif self.strategy_type == STRATEGY_LDIF_PRODUCER:
                self.strategy = LdifProducerStrategy(self)
            elif self.strategy_type == STRATEGY_SYNC_RESTARTABLE:
                self.strategy = SyncWaitRestartableStrategy(self)
            elif self.strategy_type == STRATEGY_REUSABLE_THREADED:
                self.strategy = ReusableThreadedStrategy(self)
            elif self.strategy_type == STRATEGY_SYNC_MOCK_DSA:
                self.strategy = SyncMockDsaStrategy(self)
            elif self.strategy_type == STRATEGY_ASYNC_MOCK_DSA:
                self.strategy = AsyncMockDsaStrategy(self)
            else:
                self.last_error = 'unknown strategy'
                raise LDAPUnknownStrategyError(self.last_error)

            # map strategy functions to connection functions
            self.send = self.strategy.send
            self.open = self.strategy.open
            self.get_response = self.strategy.get_response
            self.post_send_single_response = self.strategy.post_send_single_response
            self.post_send_search = self.strategy.post_send_search

            if not self.strategy.no_real_dsa:
                if self.auto_bind:
                    self.open(read_server_info=False)
                    if self.auto_bind == AUTO_BIND_NO_TLS:
                        self.bind(read_server_info=True)
                    elif self.auto_bind == AUTO_BIND_TLS_BEFORE_BIND:
                        self.start_tls(read_server_info=False)
                        self.bind(read_server_info=True)
                    elif self.auto_bind == AUTO_BIND_TLS_AFTER_BIND:
                        self.bind(read_server_info=False)
                        self.start_tls(read_server_info=True)
                    if not self.bound:
                        self.last_error = 'automatic bind not successful' + (' - ' + self.last_error if self.last_error else '')
                        raise LDAPBindError(self.last_error)
            elif self.strategy.no_real_dsa:
                self.server = None
            else:
                self.last_error = 'invalid LDAP server'
                raise LDAPInvalidServerError(self.last_error)

    def __str__(self):
        s = [
            str(self.server) if self.server else 'None',
            'user: ' + str(self.user),
            'unbound' if not self.bound else ('deferred bind' if self._deferred_bind else 'bound'),
            'closed' if self.closed else ('deferred open' if self._deferred_open else 'open'),
            ('[local: ' + _format_socket_endpoint(self.socket.getsockname()) + ' - remote: ' + _format_socket_endpoint(self.socket.getpeername()) + ']') if self.socket else '[no socket]',
            'tls not started' if not self.tls_started else('deferred start_tls' if self._deferred_start_tls else 'tls started'),
            'listening' if self.listening else 'not listening',
            self.strategy.__class__.__name__
        ]
        return ' - '.join(s)

    def __repr__(self):
        if self.server_pool:
            r = 'Connection(server={0.server_pool!r}'.format(self)
        else:
            r = 'Connection(server={0.server!r}'.format(self)
        r += '' if self.user is None else ', user={0.user!r}'.format(self)
        r += '' if self.password is None else ', password={0.password!r}'.format(self)
        r += '' if self.auto_bind is None else ', auto_bind={0.auto_bind!r}'.format(self)
        r += '' if self.version is None else ', version={0.version!r}'.format(self)
        r += '' if self.authentication is None else ', authentication={0.authentication!r}'.format(self)
        r += '' if self.strategy_type is None else ', client_strategy={0.strategy_type!r}'.format(self)
        r += '' if self.auto_referrals is None else ', auto_referrals={0.auto_referrals!r}'.format(self)
        r += '' if self.sasl_mechanism is None else ', sasl_mechanism={0.auto_sasl_mechanism!r}'.format(self)
        r += '' if self.sasl_credentials is None else ', sasl_credentials={0.sasl_credentials!r}'.format(self)
        r += '' if self.check_names is None else ', check_names={0.check_names!r}'.format(self)
        r += '' if self.usage is None else (', collect_usage=' + 'True' if self.usage else 'False')
        r += '' if self.read_only is None else ', read_only={0.read_only!r}'.format(self)
        r += '' if self.lazy is None else ', lazy={0.lazy!r}'.format(self)
        r += '' if self.raise_exceptions is None else ', raise_exceptions={0.raise_exceptions!r}'.format(self)
        r += '' if (self.pool_name is None or self.pool_name == DEFAULT_THREADED_POOL_NAME) else ', pool_name={0.pool_name!r}'.format(self)
        r += '' if self.pool_size is None else ', pool_size={0.pool_size!r}'.format(self)
        r += '' if self.pool_lifetime is None else ', pool_lifetime={0.pool_lifetime!r}'.format(self)
        r += ')'

        return r

    @property
    def stream(self):
        """Used by the LDIFProducer strategy to accumulate the ldif-change operations with a single LDIF header
        :return: reference to the response stream if defined in the strategy.
        """
        return self.strategy.get_stream() if self.strategy.can_stream else None

    @stream.setter
    def stream(self, value):
        with self.lock:
            if self.strategy.can_stream:
                self.strategy.set_stream(value)

    @property
    def usage(self):
        """Usage statistics for the connection.
        :return: Usage object
        """
        if not self._usage:
            return None
        if self.strategy.pooled:  # update masterconnection usage from pooled connections
            self._usage.reset()
            for connection in self.strategy.pool.connections:
                self._usage += connection.connection.usage
            self._usage += self.strategy.pool.terminated_usage
        return self._usage

    def __enter__(self):
        with self.lock:
            self._context_state.append((self.bound, self.closed))  # save status out of context as a tuple in a list
            if self.closed:
                self.open()
            if not self.bound:
                self.bind()

            return self

    # noinspection PyUnusedLocal
    def __exit__(self, exc_type, exc_val, exc_tb):
        with self.lock:
            context_bound, context_closed = self._context_state.pop()
            if (not context_bound and self.bound) or self.stream:  # restore status prior to entering context
                try:
                    self.unbind()
                except LDAPExceptionError:
                    pass

            if not context_closed and self.closed:
                self.open()

            if not exc_type is None:
                return False  # re-raise LDAPExceptionError

    def bind(self,
             read_server_info=True,
             controls=None):
        """Bind to ldap Server with the authentication method and the user defined in the connection

        :param read_server_info: reads info from server
        :param controls: LDAP controls to send along with the bind operation
        :type controls: list of tuple
        :return: bool

        """
        with self.lock:
            if self.lazy and not self._executing_deferred:
                self._deferred_bind = True
                self._bind_controls = controls
                self.bound = True
            else:
                self._deferred_bind = False
                self._bind_controls = None
                if self.closed:  # try to open connection if closed
                    self.open(read_server_info=False)
                if self.authentication == AUTH_ANONYMOUS:
                    request = bind_operation(self.version, self.authentication, '', '')
                    response = self.post_send_single_response(self.send('bindRequest', request, controls))
                elif self.authentication == AUTH_SIMPLE:
                    request = bind_operation(self.version, self.authentication, self.user, self.password)
                    response = self.post_send_single_response(self.send('bindRequest', request, controls))
                elif self.authentication == AUTH_SASL:
                    if self.sasl_mechanism in SASL_AVAILABLE_MECHANISMS:
                        response = self.do_sasl_bind(controls)
                    else:
                        self.last_error = 'requested SASL mechanism not supported'
                        raise LDAPSASLMechanismNotSupportedError(self.last_error)
                else:
                    self.last_error = 'unknown authentication method'
                    raise LDAPUnknownAuthenticationMethodError(self.last_error)

                if not self.strategy.sync and self.authentication != AUTH_SASL:  # get response if async except for sasl that returns the bind result even for async
                    _, result = self.get_response(response)
                elif self.strategy.sync:
                    result = self.result
                else:  # async SASL
                    result = response

                if result is None:
                    self.bound = True if self.strategy_type == STRATEGY_REUSABLE_THREADED else False
                else:
                    self.bound = True if result['result'] == RESULT_SUCCESS else False

                if not self.bound and result and result['description']:
                    self.last_error = result['description']

                if read_server_info and self.bound:
                    print('REFRESH4')
                    self.refresh_server_info()

            return self.bound

    def unbind(self,
               controls=None):
        """Unbind the connected user. Unbind implies closing session as per RFC4511 (4.3)

        :param controls: LDAP controls to send along with the bind operation

        """
        with self.lock:
            if self.lazy and not self._executing_deferred and (self._deferred_bind or self._deferred_open):  # clear deferred status
                self.strategy.close()
                self._deferred_open = False
                self._deferred_bind = False
                self._deferred_start_tls = False
            elif not self.closed:
                request = unbind_operation()
                self.send('unbindRequest', request, controls)
                self.strategy.close()

            return True

    def search(self,
               search_base,
               search_filter,
               search_scope=SEARCH_SCOPE_WHOLE_SUBTREE,
               dereference_aliases=SEARCH_DEREFERENCE_ALWAYS,
               attributes=None,
               size_limit=0,
               time_limit=0,
               types_only=False,
               get_operational_attributes=False,
               controls=None,
               paged_size=None,
               paged_criticality=False,
               paged_cookie=None):
        """
        Perform an ldap search:

        - If attributes is empty no attribute is returned
        - If attributes is ALL_ATTRIBUTES all attributes are returned
        - If paged_size is an int greater than 0 a simple paged search
          is tried as described in RFC2696 with the specified size
        - If paged is 0 and cookie is present the search is abandoned on
          server
        - Cookie is an opaque string received in the last paged search
          and must be used on the next paged search response
        - If lazy = True open and bind will be deferred until another
          LDAP operation is performed
        """
        with self.lock:
            self._fire_deferred()
            if not attributes:
                attributes = [NO_ATTRIBUTES]
            elif attributes == ALL_ATTRIBUTES:
                attributes = ['*']

            if get_operational_attributes and isinstance(attributes, list):
                attributes.append(ALL_OPERATIONAL_ATTRIBUTES)
            elif get_operational_attributes and isinstance(attributes, tuple):
                attributes += (ALL_OPERATIONAL_ATTRIBUTES, )  # concatenate tuple

            if isinstance(paged_size, int):
                real_search_control_value = RealSearchControlValue()
                real_search_control_value['size'] = Size(paged_size)
                real_search_control_value['cookie'] = Cookie(paged_cookie) if paged_cookie else Cookie('')
                if controls is None:
                    controls = []
                controls.append(('1.2.840.113556.1.4.319', paged_criticality if isinstance(paged_criticality, bool) else False, encoder.encode(real_search_control_value)))

            request = search_operation(search_base, search_filter, search_scope, dereference_aliases, attributes, size_limit, time_limit, types_only, self.server.schema if self.server else None)
            response = self.post_send_search(self.send('searchRequest', request, controls))
            if isinstance(response, int):
                return response
            if self.result['type'] == 'searchResDone' and len(response) > 0:
                return True

            return False

    def compare(self,
                dn,
                attribute,
                value,
                controls=None):
        """
        Perform a compare operation
        """
        with self.lock:
            self._fire_deferred()
            request = compare_operation(dn, attribute, value, self.server.schema if self.server else None)
            response = self.post_send_single_response(self.send('compareRequest', request, controls))
            if isinstance(response, int):
                return response
            return True if self.result['type'] == 'compareResponse' and self.result['result'] == RESULT_COMPARE_TRUE else False

    def add(self,
            dn,
            object_class=None,
            attributes=None,
            controls=None):
        """
        Add dn to the DIT, object_class is None, a class name or a list
        of class names.

        Attributes is a dictionary in the form 'attr': 'val' or 'attr':
        ['val1', 'val2', ...] for multivalued attributes
        """
        with self.lock:
            self._fire_deferred()
            attr_object_class = []
            if object_class is None:
                parm_object_class = []
            else:
                parm_object_class = object_class if isinstance(object_class, SEQUENCE_TYPES) else [object_class]

            object_class_attr_name = ''
            if attributes:
                for attr in attributes:
                    if attr.lower() == 'objectclass':
                        object_class_attr_name = attr
                        attr_object_class = attributes[object_class_attr_name] if isinstance(attributes[object_class_attr_name], SEQUENCE_TYPES) else [attributes[object_class_attr_name]]
            else:
                attributes = dict()

            if not object_class_attr_name:
                object_class_attr_name = 'objectClass'

            attributes[object_class_attr_name] = list(set([object_class for object_class in parm_object_class + attr_object_class]))  # remove duplicate ObjectClasses
            if not attributes[object_class_attr_name]:
                self.last_error = 'ObjectClass attribute is mandatory'
                raise LDAPObjectClassError(self.last_error)

            request = add_operation(dn, attributes, self.server.schema if self.server else None)
            response = self.post_send_single_response(self.send('addRequest', request, controls))

            if isinstance(response, STRING_TYPES + (int, )):
                return response

            return True if self.result['type'] == 'addResponse' and self.result['result'] == RESULT_SUCCESS else False

    def delete(self,
               dn,
               controls=None):
        """
        Delete the entry identified by the DN from the DIB.
        """
        with self.lock:
            self._fire_deferred()
            if self.read_only:
                self.last_error = 'connection is read-only'
                raise LDAPConnectionIsReadOnlyError(self.last_error)

            request = delete_operation(dn)
            response = self.post_send_single_response(self.send('delRequest', request, controls))

            if isinstance(response, STRING_TYPES + (int, )):
                return response

            return True if self.result['type'] == 'delResponse' and self.result['result'] == RESULT_SUCCESS else False

    def modify(self,
               dn,
               changes,
               controls=None):
        """
        Modify attributes of entry

        - Changes is a dictionary in the form {'attribute1':
          (operation, [val1, val2]), 'attribute2': (operation, [val1, val2])}
        - Operation is 0 (MODIFY_ADD), 1 (MODIFY_DELETE), 2 (MODIFY_REPLACE), 3 (MODIFY_INCREMENT)
        """
        with self.lock:
            self._fire_deferred()
            if self.read_only:
                self.last_error = 'connection is read-only'
                raise LDAPConnectionIsReadOnlyError(self.last_error)

            if not isinstance(changes, dict):
                self.last_error = 'changes must be a dictionary'
                raise LDAPChangesError(self.last_error)

            if not changes:
                self.last_error = 'no changes in modify request'
                raise LDAPChangesError(self.last_error)

            for change in changes:
                if len(changes[change]) != 2:
                    self.last_error = 'malformed change'
                    raise LDAPChangesError(self.last_error)
                elif changes[change][0] not in [MODIFY_ADD, MODIFY_DELETE, MODIFY_REPLACE, MODIFY_INCREMENT]:
                    self.last_error = 'unknown change type'
                    raise LDAPChangesError(self.last_error)

            request = modify_operation(dn, changes, self.server.schema if self.server else None)
            response = self.post_send_single_response(self.send('modifyRequest', request, controls))

            if isinstance(response, STRING_TYPES + (int, )):
                return response

            return True if self.result['type'] == 'modifyResponse' and self.result['result'] == RESULT_SUCCESS else False

    def modify_dn(self,
                  dn,
                  relative_dn,
                  delete_old_dn=True,
                  new_superior=None,
                  controls=None):
        """
        Modify DN of the entry or performs a move of the entry in the
        DIT.
        """
        with self.lock:
            self._fire_deferred()
            if self.read_only:
                self.last_error = 'connection is read-only'
                raise LDAPConnectionIsReadOnlyError(self.last_error)

            if new_superior and not dn.startswith(relative_dn):  # as per RFC4511 (4.9)
                self.last_error = 'DN cannot change while moving'
                raise LDAPChangesError(self.last_error)

            request = modify_dn_operation(dn, relative_dn, delete_old_dn, new_superior)
            response = self.post_send_single_response(self.send('modDNRequest', request, controls))

            if isinstance(response, STRING_TYPES + (int, )):
                return response

            return True if self.result['type'] == 'modDNResponse' and self.result['result'] == RESULT_SUCCESS else False

    def abandon(self,
                message_id,
                controls=None):
        """
        Abandon the operation indicated by message_id
        """
        with self.lock:
            self._fire_deferred()
            if self.strategy._outstanding:
                if message_id in self.strategy._outstanding and self.strategy._outstanding[message_id]['type'] not in ['abandonRequest', 'bindRequest', 'unbindRequest']:
                    request = abandon_operation(message_id)
                    self.send('abandonRequest', request, controls)
                    self.response = None
                    self.result = None
                    return True

            return False

    def extended(self,
                 request_name,
                 request_value=None,
                 controls=None):
        """
        Performs an extended operation
        """
        with self.lock:
            self._fire_deferred()
            request = extended_operation(request_name, request_value)
            response = self.post_send_single_response(self.send('extendedReq', request, controls))
            if isinstance(response, int):
                return response
            return True if self.result['type'] == 'extendedResp' and self.result['result'] == RESULT_SUCCESS else False

    def start_tls(self, read_server_info=True):  # as per RFC4511. Removal of TLS is defined as MAY in RFC4511 so the client can't implement a generic stop_tls method0
        with self.lock:
            if not self.server.tls:
                self.server.tls = Tls()

            if self.lazy and not self._executing_deferred:
                self._deferred_start_tls = True
                self.tls_started = True
                return True
            else:
                self._deferred_start_tls = False
                print('START_TLS')
                if self.server.tls.start_tls(self) and self.strategy.sync:  # for async connections _start_tls is run by the strategy
                    if read_server_info:
                        print('REFRESH5')
                        self.refresh_server_info()  # refresh server info as per RFC4515 (3.1.5)
                    return True
                elif not self.strategy.sync:
                    return True

            return False

    def do_sasl_bind(self,
                     controls):
        with self.lock:
            response = None
            if not self.sasl_in_progress:
                self.sasl_in_progress = True
                if self.sasl_mechanism == 'EXTERNAL':
                    response = sasl_external(self, controls)
                elif self.sasl_mechanism == 'DIGEST-MD5':
                    response = sasl_digest_md5(self, controls)

                self.sasl_in_progress = False

            return response

    def refresh_server_info(self):
        with self.lock:
            if not self.closed:
                previous_response = self.response
                previous_result = self.result
                self.server.get_info_from_server(self)
                self.response = previous_response
                self.result = previous_result

    def response_to_ldif(self,
                         search_result=None,
                         all_base64=False,
                         line_separator=None,
                         sort_order=None,
                         stream=None):
        with self.lock:
            if search_result is None:
                search_result = self.response

            if isinstance(search_result, SEQUENCE_TYPES):
                ldif_lines = operation_to_ldif('searchResponse', search_result, all_base64, sort_order=sort_order)
                ldif_lines = add_ldif_header(ldif_lines)
                line_separator = line_separator or linesep
                ldif_output = line_separator.join(ldif_lines)
                if stream:
                    if stream.tell() == 0:
                        header = add_ldif_header(['-'])[0]
                        stream.write(prepare_for_stream(header + line_separator + line_separator))
                    stream.write(prepare_for_stream(ldif_output + line_separator + line_separator))
                return ldif_output

            return None

    def response_to_json(self,
                         raw=False,
                         search_result=None,
                         indent=4,
                         sort=True,
                         stream=None):
        with self.lock:
            if search_result is None:
                search_result = self.response

            if isinstance(search_result, SEQUENCE_TYPES):
                json_dict = dict()
                json_dict['entries'] = list()

                for response in search_result:
                    if response['type'] == 'searchResEntry':
                        entry = dict()

                        entry['dn'] = response['dn']
                        entry['attributes'] = dict(response['attributes'])
                        if raw:
                            entry['raw'] = dict(response['raw_attributes'])
                        json_dict['entries'].append(entry)

                if str == bytes:
                    check_json_dict(json_dict)

                json_output = json.dumps(json_dict, ensure_ascii=True, sort_keys=sort, indent=indent, check_circular=True, default=format_json, separators=(',', ': '))

                if stream:
                    stream.write(json_output)

                return json_output

    def response_to_file(self,
                         target,
                         raw=False,
                         indent=4,
                         sort=True):
        with self.lock:
            if self.response:
                if isinstance(target, STRING_TYPES):
                    target = open(target, 'w+')

                target.writelines(self.response_to_json(raw=raw, indent=indent, sort=sort))
                target.close()

    def _fire_deferred(self):
        print('ENTER FIRE', self)
        with self.lock:
            if self.lazy and not self._executing_deferred:
                self._executing_deferred = True
                read_server_info = False
                try:
                    if self._deferred_open:
                        print('EXECUTE DEFERRED OPEN', self)
                        self.open(read_server_info=False)
                        read_server_info = True
                    if self._deferred_start_tls:
                        print('EXECUTE DEFERRED START_TLS', self)
                        self.start_tls(read_server_info=False)
                        read_server_info = True
                    if self._deferred_bind:
                        print('EXECUTE DEFERRED BIND', self)
                        self.bind(read_server_info=False, controls=self._bind_controls)
                        read_server_info = True

                    if read_server_info:
                        print('REFRESH6')
                        self.refresh_server_info()
                        #if self.strategy.pooled:  # executes a generic search to force read of info bacause of lazy connections in pool
                        #    response = self.search(search_base='', search_filter='(objectClass=*)', search_scope=SEARCH_SCOPE_BASE_OBJECT)
                        #    if not self.strategy.sync:
                        #        self.get_response(response)

                except LDAPExceptionError:
                    raise  # re-raise LDAPExceptionError
                finally:
                    self._executing_deferred = False
                    return read_server_info  # return True if info are read
