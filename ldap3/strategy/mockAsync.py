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

from threading import Thread, Lock
import socket

from pyasn1.codec.ber import decoder

from .. import RESPONSE_COMPLETE, SOCKET_SIZE
from ldap3.core.exceptions import LDAPSSLConfigurationError, LDAPStartTLSError, LDAPOperationResult
from ..strategy.base import BaseStrategy
from ..protocol.rfc4511 import LDAPMessage


# noinspection PyProtectedMember
class MockAsyncStrategy(BaseStrategy):
    """
    This strategy is asynchronous. You send the request and get the messageId of the request sent
    Receiving data from socket is managed in a separated thread in a blocking mode
    Requests return an int value to indicate the messageId of the requested Operation
    You get the response with get_response, it has a timeout to wait for response to appear
    Connection.response will contain the whole LDAP response for the messageId requested in a dict form
    Connection.request will contain the result LDAP message in a dict form
    Response appear in strategy._responses dictionary
    """

    # noinspection PyProtectedMember
    class ReceiverSocketThread(Thread):
        """
        The thread that actually manage the receiver socket
        """

        def __init__(self, ldap_connection):
            Thread.__init__(self)
            self.connection = ldap_connection

        def run(self):
            """
            Wait for data on socket, compute the length of the message and wait for enough bytes to decode the message
            Message are appended to strategy._responses
            """
            unprocessed = b''
            get_more_data = True
            listen = True
            data = b''
            while listen:
                if get_more_data:
                    try:
                        data = self.connection.socket.recv(SOCKET_SIZE)
                    except (OSError, socket.error):
                        listen = False
                    except Exception:
                        raise  # unexpected exception - reraise
                    if len(data) > 0:
                        unprocessed += data
                        data = b''
                    else:
                        listen = False
                length = BaseStrategy.compute_ldap_message_size(unprocessed)
                if length == -1 or len(unprocessed) < length:
                    get_more_data = True
                elif len(unprocessed) >= length:  # add message to message list
                    if self.connection.usage:
                        self.connection._usage.update_received_message(length)
                    ldap_resp = decoder.decode(unprocessed[:length], asn1Spec=LDAPMessage())[0]
                    message_id = int(ldap_resp['messageID'])
                    dict_response = self.connection.strategy.decode_response(ldap_resp)
                    if dict_response['type'] == 'extendedResp' and dict_response['responseName'] == '1.3.6.1.4.1.1466.20037':
                        if dict_response['result'] == 0:  # StartTls in progress
                            if self.connection.server.tls:
                                self.connection.server.tls._start_tls(self.connection)
                            else:
                                self.connection.last_error = 'no Tls defined in Server'
                                raise LDAPSSLConfigurationError(self.connection.last_error)
                        else:
                            self.connection.last_error = 'asynchronous StartTls failed'
                            raise LDAPStartTLSError(self.connection.last_error)
                    if message_id != 0:  # 0 is reserved for 'Unsolicited Notification' from server as per RFC4511 (paragraph 4.4)
                        with self.connection.strategy.lock:
                            if message_id in self.connection.strategy._responses:
                                self.connection.strategy._responses[message_id].append(dict_response)
                            else:
                                self.connection.strategy._responses[message_id] = [dict_response]
                            if dict_response['type'] not in ['searchResEntry', 'searchResRef', 'intermediateResponse']:
                                self.connection.strategy._responses[message_id].append(RESPONSE_COMPLETE)

                        unprocessed = unprocessed[length:]
                        get_more_data = False if unprocessed else True
                        listen = True if self.connection.listening or unprocessed else False
                    else:  # Unsolicited Notification
                        if dict_response['responseName'] == '1.3.6.1.4.1.1466.20036':  # Notice of Disconnection as per RFC4511 (paragraph 4.4.1)
                            listen = False
                        else:
                            self.connection.last_error = 'unknown unsolicited notification from server'
                            raise LDAPStartTLSError(self.connection.last_error)
            self.connection.strategy.close()

    def __init__(self, ldap_connection):
        BaseStrategy.__init__(self, ldap_connection)
        self.sync = False
        self.no_real_dsa = True
        self.pooled = False
        self._responses = None
        self.can_stream = False
        self.receiver = None
        self.lock = Lock()

    def open(self, reset_usage=True, read_server_info=True):
        """
        Open connection and start listen on the socket in a different thread
        """
        with self.lock:
            self._responses = dict()
            BaseStrategy.open(self, reset_usage, read_server_info)

        if read_server_info:
            try:
                self.connection.refresh_server_info()
            except LDAPOperationResult:  # catch errors from server if raise_exception = True
                self.connection.server._dsa_info = None
                self.connection.server._schema_info = None

    def close(self):
        """
        Close connection and stop socket thread
        """
        with self.lock:
            BaseStrategy.close(self)

    def post_send_search(self, message_id):
        """
        Clears connection.response and returns messageId
        """
        self.connection.response = None
        self.connection.result = message_id
        return message_id

    def post_send_single_response(self, message_id):
        """
        Clears connection.response and returns messageId.
        """
        self.connection.response = None
        self.connection.result = message_id
        return message_id

    def _start_listen(self):
        """
        Start thread in daemon mode
        """
        if not self.connection.listening:
            self.receiver = MockAsyncStrategy.ReceiverSocketThread(self.connection)
            self.connection.listening = True
            self.receiver.daemon = True
            self.receiver.start()

    def _get_response(self, message_id):
        """
        Performs the capture of LDAP response for this strategy
        Checks lock to avoid race condition with receiver thread
        """
        with self.lock:
            responses = self._responses.pop(message_id) if message_id in self._responses and self._responses[message_id][-1] == RESPONSE_COMPLETE else None

        return responses
