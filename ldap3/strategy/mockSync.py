"""
"""

# Created on 2014.11.17
#
# Author: Giovanni Cannata
#
# Copyright 2015 Giovanni Cannata
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
from threading import Lock

from pyasn1.codec.ber import decoder, encoder
from .. import SESSION_TERMINATED_BY_SERVER, RESPONSE_COMPLETE, SOCKET_SIZE, SEQUENCE_TYPES
from ..core.exceptions import LDAPSocketReceiveError, communication_exception_factory, LDAPExceptionError, LDAPExtensionError, \
    LDAPSASLBindInProgressError, LDAPSocketOpenError, LDAPUnknownRequestError
from ..utils.ciDict import CaseInsensitiveDict
from ..strategy.base import BaseStrategy
from ..strategy.sync import SyncStrategy
from ..protocol.rfc4511 import LDAPMessage, MessageID, ProtocolOp
from ..protocol.convert import prepare_changes_for_request, build_controls_list


class Dsa(object):
    def __init__(self):
        self.database = CaseInsensitiveDict()
        self.connections = list()
        self.ready_to_send = dict()
        self.lock = Lock()

    def produce_response(self):
        message_id = min(self.ready_to_send.keys())
        print('SERVER: processing response', message_id)
        if message_id in self.ready_to_send:
            with self.lock:
                return message_id, self.ready_to_send.pop(message_id)
        else:
            raise LDAPExceptionError('response not ready in mock server')

    def accept_request(self, ldap_message):
        request = BaseStrategy.decode_request(ldap_message)
        print('SERVER: processing request', request)

        response = None
        if request['type'] == 'bindRequest':
            result = self.do_bind(request)
        elif request['type'] == 'unbindRequest':
            result = self.do_unbind(request)
            result = dict()  # unbind doesn't return anything
        elif request['type'] == 'addRequest':
            result = self.do_add(request)
        elif request['type'] == 'compareRequest':
            result = self.do_compare(request)
        elif request['type'] == 'delRequest':
            result = self.do_delete(request)
        elif request['type'] == 'extendedReq':
            result = self.do_extended(request)
        elif request['type'] == 'modifyRequest':
            result = self.do_modify(request)
        elif request['type'] == 'modDNRequest':
            result = self.do_modify_dn(request)
        elif request['type'] == 'searchRequest':
            response, result = self.do_search(request)
        elif request['type'] == 'abandonRequest':
            result = self.do_abandon(request)
        else:
            raise LDAPUnknownRequestError('unknown request')

        self.ready_to_send[int(ldap_message['messageID'])] = [(response, result)]

    def do_bind(self, request):
        with self.lock:
            result = None
            return result

    def do_unbind(self, request):
        with self.lock:
            result = None
            return result

    def do_add(self, request):
        with self.lock:
            result = None
            return result

    def do_compare(self, request):
        with self.lock:
            result = None
            return result

    def do_delete(self, request):
        with self.lock:
            result = None
            return result

    def do_modify(self, request):
        with self.lock:
            result = None
            return result

    def do_modify_dn(self, request):
        with self.lock:
            result = None
            return result

    def do_search(self, request):
        with self.lock:
            response = None
            result = None
            return response, result

    def do_abandon(self, request):
        with self.lock:
            result = None
            return result

    def do_extended(self, request):
        with self.lock:
            result = None
            return result


# noinspection PyProtectedMember
class MockSyncStrategy(SyncStrategy):
    """
    This strategy create a mock LDAP server, with synchronous access
    It can be useful to test LDAP without a real Server
    """
    def __init__(self, ldap_connection):
        SyncStrategy.__init__(self, ldap_connection)
        self.sync = True
        self.no_real_dsa = True
        self.pooled = False
        self.can_stream = False
        self.dsa = Dsa()

    def sending(self, ldap_message):
        self.dsa.accept_request(ldap_message)

    def receiving(self):
        return self.dsa.produce_response()

    def _start_listen(self):
        self.connection.listening = True
        self.connection.closed = False
        self._header_added = False
        print('start listening')

    def _stop_listen(self):
        self.connection.listening = False
        self.connection.closed = True
        print('stop listening')

