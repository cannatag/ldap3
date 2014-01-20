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

from threading import Thread
from pyasn1.codec.ber import decoder

from ldap3 import RESPONSE_COMPLETE, SOCKET_SIZE, RESULT_REFERRAL
from ..strategy.baseStrategy import BaseStrategy
from ..protocol.rfc4511 import LDAPMessage


class AsyncThreadedStrategy(BaseStrategy):
    """
    This strategy is asynchronous. You send the request and get the messageId of the request sent
    Receiving data from socket is managed in a separated thread in a blocking mode
    Requests return an int value to indicate the messageId of the requested Operation
    You get the response with getResponse, it has a timeout to wait for response to appear
    Connection.response will contain the whole LDAP response for the messageId requested in a dict form
    Connection.request will contain the result LDAP message in a dict form
    Response appear in strategy._responses dictionary
    """

    def __init__(self, ldapConnection):
        BaseStrategy.__init__(self, ldapConnection)
        self.sync = False
        self.noRealDSA = False
        self._responses = None
        self.receiver = None

    def open(self, startListening = True):
        """
        Open connection and start listen on the socket in a different thread
        """
        with self.connection.lock:
            BaseStrategy.open(self, startListening)
            self._responses = dict()

        self.connection.refreshDsaInfo()

    def close(self):
        """
        Close connection and stop socket thread
        """
        with self.connection.lock:
            BaseStrategy.close(self)

    def postSendSearch(self, messageId):
        """
        Clears connection.response and returns messageId.
        """
        self.connection.response = None
        self.connection.result = messageId
        return messageId

    def postSendSingleResponse(self, messageId):
        """
        Clears connection.response and returns messageId.
        """
        self.connection.response = None
        self.connection.result = messageId
        return messageId

    def _startListen(self):
        """
        Start thread in daemon mode
        """
        if not self.connection.listening:
            self.receiver = ReceiverSocketThread(self.connection)
            self.connection.listening = True
            self.receiver.daemon = True
            self.receiver.start()

    def _getResponse(self, messageId):
        """
        Performs the capture of LDAP response for this strategy
        Checks lock to avoid race condition with receiver thread
        """
        with self.connection.lock:
            responses = self._responses.pop(messageId) if messageId in self._responses and self._responses[messageId][-1] == RESPONSE_COMPLETE else None

        if responses is not None and responses[-2]['result'] == RESULT_REFERRAL and self.connection.autoReferrals:
            refResponse, refResult = self.doOperationOnReferral(self._outstanding[messageId], responses[-2]['referrals'])
            if refResponse is not None:
                responses = refResponse + [refResult]
                responses.append(RESPONSE_COMPLETE)
            elif refResult is not None:
                responses = [refResult, RESPONSE_COMPLETE]

            self._referrals = []

        return responses


class ReceiverSocketThread(Thread):
    """
    The thread that actually manage the receiver socket
    """

    def __init__(self, ldapConnection):
        Thread.__init__(self)
        self.connection = ldapConnection

    def run(self):
        """
        Wait for data on socket, compute the length of the message and wait for enough bytes to decode the message
        Message are appended to strategy._responses
        """
        unprocessed = b''
        getMoreData = True
        listen = True
        data = b''
        while listen:
            if getMoreData:
                try:
                    data = self.connection.socket.recv(SOCKET_SIZE)
                except OSError:
                    listen = False
                if len(data) > 0:
                    unprocessed += data
                    data = b''
                else:
                    listen = False
            length = BaseStrategy.computeLDAPMessageSize(unprocessed)
            if length == -1 or len(unprocessed) < length:
                getMoreData = True
            elif len(unprocessed) >= length:  # add message to message list
                if self.connection.usage:
                    self.connection.usage.receivedMessage(length)
                ldapResp = decoder.decode(unprocessed[:length], asn1Spec = LDAPMessage())[0]
                messageId = int(ldapResp['messageID'])
                dictResponse = BaseStrategy.decodeResponse(ldapResp)
                if dictResponse['type'] == 'extendedResp' and dictResponse['responseName'] == '1.3.6.1.4.1.1466.20037':
                    if dictResponse['result'] == 0:  # StartTls in progress
                        if self.connection.server.tls:
                            self.connection.server.tls._startTls(self.connection)
                        else:
                            self.connection.lastError = 'no Tls object defined in server'
                            raise Exception(self.connection.lastError)
                    else:
                        self.connection.lastError = 'Asynchronous StartTls failed'
                        raise Exception(self.connection.lastError)
                if messageId != 0:  # 0 is reserved for 'Unsolicited Notification' from server as per rfc 4511 (paragraph 4.4)

                    with self.connection.lock:
                        if messageId in self.connection.strategy._responses:
                            self.connection.strategy._responses[messageId].append(dictResponse)
                        else:
                            self.connection.strategy._responses[messageId] = [dictResponse]
                        if dictResponse['type'] not in ['searchResEntry', 'searchResRef', 'intermediateResponse']:
                            self.connection.strategy._responses[messageId].append(RESPONSE_COMPLETE)

                    unprocessed = unprocessed[length:]
                    getMoreData = False if unprocessed else True
                    listen = True if self.connection.listening or unprocessed else False
                else:  # Unsolicited Notification
                    if dictResponse['responseName'] == '1.3.6.1.4.1.1466.20036':  # Notice of Disconnection as per rfc 4511 (paragraph 4.4.1)
                        listen = False
        self.connection.strategy.close()
