"""
Created on 2013.07.15

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

from pyasn1.codec.ber import decoder

from .. import SESSION_TERMINATED_BY_SERVER, RESPONSE_COMPLETE, SOCKET_SIZE, RESULT_REFERRAL
from ..core.exceptions import LDAPSocketReceiveError, communication_exception_factory, LDAPExceptionError
from ..strategy.baseStrategy import BaseStrategy
from ..protocol.rfc4511 import LDAPMessage


class SyncWaitStrategy(BaseStrategy):
    """
    This strategy is synchronous. You send the request and get the response
    Requests return a boolean value to indicate the result of the requested Operation
    Connection.response will contain the whole LDAP response for the messageId requested in a dict form
    Connection.request will contain the result LDAP message in a dict form
    """

    def __init__(self, ldap_connection):
        BaseStrategy.__init__(self, ldap_connection)
        self.sync = True
        self.no_real_dsa = False
        self.pooled = False
        self.can_stream = False

    def open(self, reset_usage=True):
        BaseStrategy.open(self, reset_usage)
        self.connection.refresh_dsa_info()

    def _start_listen(self):
        if not self.connection.listening and not self.connection.closed:
            self.connection.listening = True

    def receiving(self):
        """
        Receive data over the socket
        Checks if the socket is closed
        """
        messages = []
        receiving = True
        unprocessed = b''
        data = b''
        get_more_data = True
        exc = None
        while receiving:
            if get_more_data:
                try:
                    data = self.connection.socket.recv(SOCKET_SIZE)
                except (OSError, socket.error, AttributeError) as e:
                    self.connection.last_error = 'error receiving data: ' + str(e)
                    exc = e

                if exc:
                    try:  # try to close the connection before raising exception
                        self.close()
                    except (socket.error, LDAPExceptionError):
                        pass
                    raise communication_exception_factory(LDAPSocketReceiveError, e)(self.connection.last_error)

                unprocessed += data
            if len(data) > 0:
                length = BaseStrategy.compute_ldap_message_size(unprocessed)
                if length == -1:  # too few data to decode message length
                    get_more_data = True
                    continue
                if len(unprocessed) < length:
                    get_more_data = True
                else:
                    messages.append(unprocessed[:length])
                    unprocessed = unprocessed[length:]
                    get_more_data = False
                    if len(unprocessed) == 0:
                        receiving = False
            else:
                receiving = False

        return messages

    def post_send_single_response(self, message_id):
        """
        Executed after an Operation Request (except Search)
        Returns the result message or None
        """
        responses, result = self.get_response(message_id)
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
        if isinstance(responses, list):
            self.connection.response = responses[:]  # copy search result entries without result
            return responses

        self.connection.last_error = 'error receiving response'
        raise LDAPSocketReceiveError(self.connection.last_error)

    def _get_response(self, message_id):
        """
        Performs the capture of LDAP response for SyncWaitStrategy
        """
        ldap_responses = []
        response_complete = False
        while not response_complete:
            responses = self.receiving()
            if responses:
                for response in responses:
                    while len(response) > 0:
                        if self.connection._usage:
                            self.connection._usage.received_message(len(response))
                        ldap_resp, unprocessed = decoder.decode(response, asn1Spec=LDAPMessage())
                        if int(ldap_resp['messageID']) == message_id:
                            dict_response = BaseStrategy.decode_response(ldap_resp)
                            ldap_responses.append(dict_response)
                            if dict_response['type'] not in ['searchResEntry', 'searchResRef', 'intermediateResponse']:
                                response_complete = True
                        elif int(ldap_resp['messageID']) == 0:  # 0 is reserved for 'Unsolicited Notification' from server as per RFC4511 (paragraph 4.4)
                            dict_response = BaseStrategy.decode_response(ldap_resp)
                            if dict_response['responseName'] == '1.3.6.1.4.1.1466.20036':  # Notice of Disconnection as per RFC4511 (paragraph 4.4.1)
                                return SESSION_TERMINATED_BY_SERVER
                        else:
                            self.connection.last_error = 'invalid messageId received'
                            raise LDAPSocketReceiveError(self.connection.last_error)
                        response = unprocessed
                        if response:  # if this statement is removed unprocessed data will be processed as another message
                            self.connection.last_error = 'unprocessed substrate error'
                            raise LDAPSocketReceiveError(self.connection.last_error)
            else:
                return SESSION_TERMINATED_BY_SERVER

        ldap_responses.append(RESPONSE_COMPLETE)

        if ldap_responses[-2]['result'] == RESULT_REFERRAL:
            if self.connection._usage:
                self.connection._usage.referrals_received += 1
            if self.connection.auto_referrals:
                ref_response, ref_result = self.do_operation_on_referral(self._outstanding[message_id], ldap_responses[-2]['referrals'])
                if ref_response is not None:
                    ldap_responses = ref_response + [ref_result]
                    ldap_responses.append(RESPONSE_COMPLETE)
                elif ref_result is not None:
                    ldap_responses = [ref_result, RESPONSE_COMPLETE]

                self._referrals = []

        return ldap_responses
