"""
Created on 2013.05.31

@author: Giovanni Cannata

Copyright 2013 Giovanni Cannata

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

from datetime import datetime, timedelta
from os import linesep

from pyasn1.codec.ber import encoder

from ldap3 import AUTH_ANONYMOUS, AUTH_SIMPLE, AUTH_SASL, MODIFY_ADD, MODIFY_DELETE, MODIFY_REPLACE, SEARCH_DEREFERENCE_ALWAYS, SEARCH_SCOPE_WHOLE_SUBTREE, STRATEGY_ASYNC_THREADED, STRATEGY_SYNC, CLIENT_STRATEGIES, RESULT_SUCCESS, \
    RESULT_COMPARE_TRUE, NO_ATTRIBUTES, ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES, MODIFY_INCREMENT, STRATEGY_LDIF_PRODUCER, SASL_AVAILABLE_MECHANISMS, LDAPException, STRATEGY_SYNC_RESTARTABLE, POOLING_STRATEGY_ROUND_ROBIN, \
    STRATEGY_POOL_REUSABLE
from .pooling import ServerPool
from ..strategy.Reusable import ReusableStrategy
from ..operation.abandon import abandon_operation
from ..operation.add import add_operation
from ..operation.bind import bind_operation
from ..operation.compare import compare_operation
from ..operation.delete import delete_operation
from ..operation.extended import extended_operation
from ..operation.modify import modify_operation
from ..operation.modifyDn import modify_dn_operation
from ..operation.search import search_operation
from ..protocol.rfc2849 import to_ldif
from ..protocol.sasl.digestMd5 import sasl_digest_md5
from ..protocol.sasl.external import sasl_external
from ..strategy.asyncThreaded import AsyncThreadedStrategy
from ..strategy.ldifProducer import LdifProducerStrategy
from ..strategy.syncWait import SyncWaitStrategy
from ..strategy.syncWaitRestartable import SyncWaitRestartableStrategy
from ..operation.unbind import unbind_operation
from ..protocol.rfc2696 import RealSearchControlValue, Cookie, Size
from .usage import ConnectionUsage
from .tls import Tls


class Connection(object):
    """
    Main ldap connection class
    controls, if used, must be a list of tuples. Each tuple must have 3 elements,
    the control OID, a boolean meaning if the control is critical, a value
    If the boolean is set to True the server must honorate the control or refuse the operation
    Mixing controls must be defined in controls specification (as per rfc 4511)
    """

    def __init__(self, server, user=None, password=None, auto_bind=False, version=3, authentication=None, client_strategy=STRATEGY_SYNC, auto_referrals=True, sasl_mechanism=None, sasl_credentials=None, collect_usage=False, read_only=False, lazy=False):
        if client_strategy not in CLIENT_STRATEGIES:
            self.last_error = 'unknown client connection strategy'
            raise LDAPException(self.last_error)

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
            raise LDAPException('unknown authentication method')

        self.version = version
        self.auto_referrals = True if auto_referrals else False
        self.request = None
        self.response = None
        self.result = None
        self.bound = False
        self.listening = False
        self.closed = True
        self.last_error = None
        self.auto_bind = True if auto_bind else False
        self.sasl_mechanism = sasl_mechanism
        self.sasl_credentials = sasl_credentials
        self.usage = ConnectionUsage() if collect_usage else None
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
        if isinstance(server, list):
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
        elif self.strategy_type == STRATEGY_POOL_REUSABLE:
            self.strategy = ReusableStrategy(self)
        else:
            raise LDAPException('unavailable strategy')

        # map strategy functions to connection functions
        self.send = self.strategy.send
        self.open = self.strategy.open
        self.get_response = self.strategy.get_response
        self.post_send_single_response = self.strategy.post_send_single_response
        self.post_send_search = self.strategy.post_send_search

        if not self.strategy.no_real_dsa and self.server.is_valid():
            if self.auto_bind:
                self.open()
                self.bind()
                if not self.bound:
                    raise LDAPException('auto_bind not successful')
        elif self.strategy.no_real_dsa:
            self.server = None
        else:
            self.last_error = 'invalid ldap server'
            raise LDAPException(self.last_error)

    # noinspection PyListCreation
    def __str__(self):
        s = [str(self.server) if self.server.is_valid else 'None']
        s.append('user: ' + str(self.user))
        s.append('unbound' if not self.bound else ('deferred bind' if self._deferred_bind else 'bound'))
        s.append('closed' if self.closed else ('deferred open' if self._deferred_open else 'open'))
        s.append('tls not started' if not self.tls_started else('deferred start_tls' if self._deferred_start_tls else 'tls started'))
        s.append('listening' if self.listening else 'not listening')
        s.append(self.strategy.__class__.__name__)

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
        r += ')'

        return r

    def __enter__(self):
        self._context_state.append((self.bound, self.closed))  # save status out of context as a tuple in a list
        if self.closed:
            self.open()
        if not self.bound:
            self.bind()

        return self

    # noinspection PyUnusedLocal
    def __exit__(self, exc_type, exc_val, exc_tb):
        context_bound, context_closed = self._context_state.pop()
        if not context_bound and self.bound:  # restore status prior to entering context
            self.unbind()

        if not context_closed and self.closed:
            self.open()

        if not exc_type is None:
            return False  # reraise LDAPException

    def bind(self, controls=None):
        """
        Bind to ldap with the user defined in Server object
        """
        if self.lazy and not self._executing_deferred:
            self._deferred_bind = True
            self._bind_controls = controls
            self.bound = True
        else:
            self._deferred_bind = False
            self._bind_controls = None
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
                    self.last_error = 'requested sasl mechanism not supported'
                    raise LDAPException(self.last_error)
            else:
                self.last_error = 'unknown authentication method'
                raise LDAPException(self.last_error)

            if isinstance(response, int):  # get response if async
                self.get_response(response)

            if response is None:
                self.bound = False
            else:
                self.bound = True if self.result['result'] == RESULT_SUCCESS else False

            if self.bound:
                self.refresh_dsa_info()

        return self.bound

    def unbind(self, controls=None):
        """
        Unbinds the connected user
        Unbind implies closing session as per rfc 4511 (4.3)
        """
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

    def close(self):
        """
        Alias for unbind operation
        """
        self.unbind()

    def search(self, search_base, search_filter, search_scope=SEARCH_SCOPE_WHOLE_SUBTREE, dereference_aliases=SEARCH_DEREFERENCE_ALWAYS, attributes=None, size_limit=0, time_limit=0, types_only=False, get_operational_attributes=False, controls=None,
               paged_size=None, paged_criticality=False, paged_cookie=None):
        """
        Perform an ldap search
        if attributes is empty no attribute is returned
        if attributes is ALL_ATTRIBUTES all attributes are returned
        if paged_size is an int greater than 0 a simple paged search is tried as described in RFC2696 with the specified size
        if paged is 0 and cookie is present the search is abandoned on server
        cookie is an opaque string received in the last paged search and must be used on the next paged search response
        if lazy = True open and bind will be deferred until another LDAP operation is performed
        """
        self._fire_deferred()
        if not attributes:
            attributes = [NO_ATTRIBUTES]
        elif attributes == ALL_ATTRIBUTES:
            attributes = ['*']

        if get_operational_attributes:
            attributes.append(ALL_OPERATIONAL_ATTRIBUTES)

        if isinstance(paged_size, int):
            real_search_control_value = RealSearchControlValue()
            real_search_control_value['size'] = Size(paged_size)
            real_search_control_value['cookie'] = Cookie(paged_cookie) if paged_cookie else Cookie('')
            if controls is None:
                controls = []
            controls.append(('1.2.840.113556.1.4.319', paged_criticality if isinstance(paged_criticality, bool) else False, encoder.encode(real_search_control_value)))

        request = search_operation(search_base, search_filter, search_scope, dereference_aliases, attributes, size_limit, time_limit, types_only)

        response = self.post_send_search(self.send('searchRequest', request, controls))
        if isinstance(response, int):
            return response

        if self.result['type'] == 'searchResDone' and len(response) > 0:
            return True

        return False

    def compare(self, dn, attribute, value, controls=None):
        """
        Perform a compare operation
        """
        self._fire_deferred()
        request = compare_operation(dn, attribute, value)
        response = self.post_send_single_response(self.send('compareRequest', request, controls))
        if isinstance(response, int):
            return response
        return True if self.result['type'] == 'compareResponse' and self.result['result'] == RESULT_COMPARE_TRUE else False

    def add(self, dn, object_class, attributes=None, controls=None):
        """
        add dn to the DIT, object_class is None, a class name or a list of class names,
        attributes is a dictionary in the form 'attr': 'val' or 'attr': ['val1', 'val2', ...] for multivalued attributes
        """
        self._fire_deferred()
        attr_object_class = []
        if object_class is None:
            parm_object_class = []
        else:
            parm_object_class = object_class if isinstance(object_class, list) else [object_class]

        if attributes:
            if 'objectClass' in attributes:
                attr_object_class = attributes['objectClass'] if isinstance(attributes['objectClass'], list) else [attributes['objectClass']]
        else:
            attributes = dict()

        attributes['objectClass'] = list(set([object_class.lower() for object_class in parm_object_class + attr_object_class]))  # remove duplicate object_class
        if not attributes['objectClass']:
            self.last_error = 'object_class is mandatory'
            raise LDAPException(self.last_error)

        request = add_operation(dn, attributes)
        response = self.post_send_single_response(self.send('addRequest', request, controls))

        if isinstance(response, int) or isinstance(response, str):
            return response

        return True if self.result['type'] == 'addResponse' and self.result['result'] == RESULT_SUCCESS else False

    def delete(self, dn, controls=None):
        """
        Delete in the dib the entry identified by dn
        """
        self._fire_deferred()
        if self.read_only:
            raise LDAPException('Connection is in read-only mode')

        request = delete_operation(dn)
        response = self.post_send_single_response(self.send('delRequest', request, controls))

        if isinstance(response, int) or isinstance(response, str):
            return response

        return True if self.result['type'] == 'delResponse' and self.result['result'] == RESULT_SUCCESS else False

    def modify(self, dn, changes, controls=None):
        """
        Modify attributes of entry
        Changes is a dictionary in the form {'attribute1': [(operation, [val1, val2])], 'attribute2': [(operation, [val1, val2])]}
        Operation is 0 (MODIFY_ADD), 1 (MODIFY_DELETE), 2 (MODIFY_REPLACE), 3 (MODIFY_INCREMENT)
        """
        self._fire_deferred()
        if self.read_only:
            raise LDAPException('Connection is in read-only mode')

        if not isinstance(changes, dict):
            self.last_error = 'changes must be a dictionary'
            raise LDAPException(self.last_error)

        for change in changes:
            if len(changes[change]) != 2:
                self.last_error = 'malformed change'
                raise LDAPException(self.last_error)
            elif changes[change][0] not in [MODIFY_ADD, MODIFY_DELETE, MODIFY_REPLACE, MODIFY_INCREMENT]:
                self.last_error = 'unknown change type'
                raise LDAPException(self.last_error)
        if not changes:
            self.last_error = 'no changes in modify request'
            raise LDAPException(self.last_error)

        request = modify_operation(dn, changes)
        response = self.post_send_single_response(self.send('modifyRequest', request, controls))

        if isinstance(response, int) or isinstance(response, str):
            return response

        return True if self.result['type'] == 'modifyResponse' and self.result['result'] == RESULT_SUCCESS else False

    def modify_dn(self, dn, relative_dn, delete_old_dn=True, new_superior=None, controls=None):
        """
        Modify dn of the entry or performs a move of the entry in the DIT
        """
        self._fire_deferred()
        if self.read_only:
            raise LDAPException('Connection is in read-only mode')

        if new_superior and not dn.startswith(relative_dn):  # as per rfc 4511 (4.9)
            raise LDAPException('dn cannot change while moving object')

        request = modify_dn_operation(dn, relative_dn, delete_old_dn, new_superior)
        response = self.post_send_single_response(self.send('modDNRequest', request, controls))

        if isinstance(response, int) or isinstance(response, str):
            return response

        return True if self.result['type'] == 'modDNResponse' and self.result['result'] == RESULT_SUCCESS else False

    def abandon(self, message_id, controls=None):
        """
        Abandon the operation indicated by message_id
        """
        self._fire_deferred()
        if self.strategy._outstanding:
            if message_id in self.strategy._outstanding and self.strategy._outstanding[message_id]['type'] not in ['abandonRequest', 'bindRequest', 'unbindRequest']:
                request = abandon_operation(message_id)
                self.send('abandonRequest', request, controls)
                self.response = None
                self.result = None
                return True

        return False

    def extended(self, request_name, request_value=None, controls=None):
        """
        Performs an extended operation
        """
        self._fire_deferred()
        request = extended_operation(request_name, request_value)
        response = self.post_send_single_response(self.send('extendedReq', request, controls))
        if isinstance(response, int):
            return response
        return True if self.result['type'] == 'extendedResp' and self.result['result'] == RESULT_SUCCESS else False

    def start_tls(self):  # as per RFC4511. Removal of TLS is defined as MAY in RFC4511 so the client can't implement a generic stop_tls method0
        if not self.server.tls:
            self.server.tls = Tls()

        if self.lazy and not self._executing_deferred:
            self._deferred_start_tls = True
            self.tls_started = True
            return True
        else:
            self._deferred_start_tls = False
            if self.server.tls.start_tls(self):
                self.refresh_dsa_info()  # refresh server info as per rfc 4515 (3.1.5)
                self.tls_started = True
                return True

        return False

    def do_sasl_bind(self, controls):
        response = None
        if not self.sasl_in_progress:
            self.sasl_in_progress = True
            if self.sasl_mechanism == 'EXTERNAL':
                response = sasl_external(self, controls)
            elif self.sasl_mechanism == 'DIGEST-MD5':
                response = sasl_digest_md5(self, controls)

            self.sasl_in_progress = False

        return response

    def refresh_dsa_info(self):
        if not self.closed:
            self.server.get_info_from_server(self)

    def response_to_ldif(self, search_result=None, all_base64=False):
        if search_result is None:
            search_result = self.response

        if isinstance(search_result, list):
            search_result_to_ldif = to_ldif('searchResponse', search_result, all_base64)
        else:
            search_result_to_ldif = None

        return search_result_to_ldif

    def _fire_deferred(self):
        if self.lazy:
            self._executing_deferred = True
            try:
                if self._deferred_open:
                    self.open()
                if self._deferred_bind:
                    self.bind(self._bind_controls)
                if self._deferred_start_tls:
                    self.start_tls()
            except LDAPException:
                raise
            finally:
                self._executing_deferred = False
