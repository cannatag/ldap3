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

    def produce_response(self, message_id):
        print('SERVER: processing response', message_id)
        if message_id in self.ready_to_send:
            with self.lock:
                return message_id, self.ready_to_send.pop(message_id)
        else:
            raise LDAPExceptionError('response not ready in mock server')

    def accept_request(self, message_id, request):
        print('SERVER: processing request', message_id, request)

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

        self.ready_to_send[message_id] = [(response, result)]

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

    def send(self, message_type, request, controls=None):
        """
        Send an LDAP message
        Returns the message_id
        """
        exc = None
        self.connection.request = None
        if self.connection.listening:
            if self.connection.sasl_in_progress and message_type not in ['bindRequest']:  # as per RFC4511 (4.2.1)
                self.connection.last_error = 'cannot send operation requests while SASL bind is in progress'
                raise LDAPSASLBindInProgressError(self.connection.last_error)
            message_id = self.connection.server.next_message_id()
            print('server request: ', request)
            ldap_message = LDAPMessage()
            ldap_message['messageID'] = MessageID(message_id)
            ldap_message['protocolOp'] = ProtocolOp().setComponentByName(message_type, request)
            message_controls = build_controls_list(controls)
            if message_controls is not None:
                ldap_message['controls'] = message_controls

            encoded_message = encoder.encode(ldap_message)

            self.connection.request = BaseStrategy.decode_request(ldap_message)
            self.connection.request['controls'] = controls
            self._outstanding[message_id] = self.connection.request
            if self.connection.usage:
                self.connection._usage.update_transmitted_message(self.connection.request, len(encoded_message))

            self.dsa.accept_request(message_id, self.connection.request)
        else:
            self.connection.last_error = 'unable to send message, socket is not open'
            raise LDAPSocketOpenError(self.connection.last_error)

        return message_id

    def post_send_single_response(self, message_id):
        """
        Executed after an Operation Request (except Search)
        Returns the result message or None
        """
        responses, result = self.get_response(message_id)
        self.connection.result = result
        if result['type'] == 'intermediateResponse':  # checks that all responses are intermediates (there should be only one)
            for response in responses:
                if response['type'] != 'intermediateResponse':
                    self.connection.last_error = 'multiple messages error'
                    raise LDAPSocketReceiveError(self.connection.last_error)

        responses.append(result)
        return responses

    def post_send_search(self, message_id):
        """
        Executed after a search request
        Returns the result message and store in connection.response the objects found
        """
        responses, result = self.get_response(message_id)
        self.connection.result = result
        if isinstance(responses, SEQUENCE_TYPES):
            self.connection.response = responses[:]  # copy search result entries
            return responses

        self.connection.last_error = 'error receiving response'
        raise LDAPSocketReceiveError(self.connection.last_error)

    def _get_response(self, message_id):
        """
        Performs the capture of LDAP response for MockSyncStrategy
        """
        ldap_responses = []
        response_complete = False
        while not response_complete:
            responses = self.dsa.produce_response(message_id)
            if responses:
                for returned_message_id, dict_response in responses:
                    if self.connection.usage:
                        self.connection._usage.update_received_message(len(dict_response))
                    if returned_message_id == message_id:
                        ldap_responses.append(dict_response)
                        if dict_response['type'] not in ['searchResEntry', 'searchResRef', 'intermediateResponse']:
                            response_complete = True
                    elif returned_message_id == 0:  # 0 is reserved for 'Unsolicited Notification' from server as per RFC4511 (paragraph 4.4)
                        if dict_response['responseName'] == '1.3.6.1.4.1.1466.20036':  # Notice of Disconnection as per RFC4511 (paragraph 4.4.1)
                            return SESSION_TERMINATED_BY_SERVER
                        else:
                            self.connection.last_error = 'unknown unsolicited notification from server'
                            raise LDAPSocketReceiveError(self.connection.last_error)
                    elif returned_message_id != message_id and self.decode_response(dict_response)['type'] == 'extendedResp':
                        self.connection.last_error = 'multiple extended responses to a single extended request'
                        raise LDAPExtensionError(self.connection.last_error)
                        # pass  # ignore message with invalid messageId when receiving multiple extendedResp. This is not allowed by RFC4511 but some LDAP server do it
                    else:
                        self.connection.last_error = 'invalid messageId received'
                        raise LDAPSocketReceiveError(self.connection.last_error)
            else:
                return SESSION_TERMINATED_BY_SERVER

        ldap_responses.append(RESPONSE_COMPLETE)

        return ldap_responses

    def _start_listen(self):
        self.connection.listening = True
        self.connection.closed = False
        self._header_added = False
        print('start listening')

    def _stop_listen(self):
        self.connection.listening = False
        self.connection.closed = True
        print('stop listening')

