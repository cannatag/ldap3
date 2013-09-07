"""
Created on 2013.07.15

@author: Giovanni Cannata

Copyright 2013 Giovanni Cannata

This file is part of Python3-ldap.

Python3-ldap is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Python3-ldap is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with Python3-ldap in the COPYING and COPYING.LESSER files.
If not, see <http://www.gnu.org/licenses/>.
"""

from pyasn1.codec.ber import decoder

from ldap3.strategy.baseStrategy import BaseStrategy
from ldap3 import SESSION_TERMINATED_BY_SERVER, RESPONSE_COMPLETE, SOCKET_SIZE, \
    RESULT_REFERRAL
from ldap3.protocol.rfc4511 import LDAPMessage


class SyncWaitStrategy(BaseStrategy):
    """
    This strategy is synchronous. You send the request and get the response
    Requests return a boolean value to indicate the result of the requested Operation
    Connection.response will contain the whole LDAP response for the messageId requested in a dict form
    Connection.request will contain the result LDAP message in a dict form
    """

    def __init__(self, ldapConnection):
        super(SyncWaitStrategy, self).__init__(ldapConnection)

    def _startListen(self):
        if not self.connection.listening and not self.connection.closed:
            self.connection.listening = True

    def receiving(self):
        """
        Receive data over the socket
        Check if the socket is closed
        """
        messages = []
        receiving = True
        unprocessed = b''
        data = b''
        getMoreData = True
        while receiving:
            if getMoreData:
                try:
                    data = self.connection.socket.recv(SOCKET_SIZE)
                except OSError as e:
                    # if e.winerror == 10004:  # window error for socket not open
                    self.connection.close()
                    self.connection.lastError = 'Error receiving data: ' + str(e)
                    raise Exception(self.connection.lastError)
                unprocessed += data
            if len(data) > 0:
                length = BaseStrategy.computeLDAPMessageSize(unprocessed)
                if length == -1:  # too few data to decode message length
                    getMoreData = True
                    continue
                if len(unprocessed) < length:
                    getMoreData = True
                else:
                    messages.append(unprocessed[:length])
                    unprocessed = unprocessed[length:]
                    getMoreData = False
                    if len(unprocessed) == 0:
                        receiving = False
            else:
                receiving = False

        return messages

    def postSendSingleResponse(self, messageId):
        """
        To be executed after an Operation Request (except Search)
        Return the result message or None
        """
        responses = self.getResponse(messageId)
        if responses and len(responses) == 1 and responses[0]['type'] != 'intermediateResponse':
            return responses
        elif not responses:
            return None
        else:
            checkIntermediateResponse = True
            for response in responses[:-1]:
                if response['type'] != 'intermediateResponse':
                    checkIntermediateResponse = False
                    break
            if not checkIntermediateResponse:
                self.connection.lastError = 'multiple messages error'
                raise Exception(self.connection.lastError)

        return responses

    def postSendSearch(self, messageId):
        """
        To be executed after a search request
        Returns the result message and store in connection.response the objects found
        """
        responses = self.getResponse(messageId)
        if isinstance(responses, list):
            self.connection.response = responses[:-1] if responses[-1]['type'] == 'searchResDone' else responses
            return self.connection.response

        raise Exception('error receiving response')
        # elif isinstance(responses, dict):
        #    raise Exception("why I'm here?")
        #    self.connection.response = []
        #    return responses

    def _getResponse(self, messageId):
        """
        Performs the capture of LDAP response for SyncWaitStrategy
        """
        ldapResponses = []
        responseComplete = False
        while not responseComplete:
            responses = self.receiving()
            if responses:
                for response in responses:
                    while len(response) > 0:
                        if self.connection.usage:
                            self.connection.usage.receivedMessage(len(response))
                        ldapResp, unprocessed = decoder.decode(response, asn1Spec = LDAPMessage())
                        if int(ldapResp['messageID']) == messageId:
                            dictResponse = BaseStrategy.decodeResponse(ldapResp)
                            ldapResponses.append(dictResponse)
                            if dictResponse['type'] not in ['searchResEntry', 'searchResRef', 'intermediateResponse']:
                                responseComplete = True
                        elif int(ldapResp[
                            'messageID']) == 0:  # 0 is reserved for 'Unsolicited Notification' from server as per rfc 4511 (paragraph 4.4)
                            dictResponse = BaseStrategy.decodeResponse(ldapResp)
                            if dictResponse[
                                'responseName'] == '1.3.6.1.4.1.1466.20036':  # Notice of Disconnection as per rfc 4511 (paragraph 4.4.1)
                                return SESSION_TERMINATED_BY_SERVER
                        else:
                            self.connection.lastError = 'invalid messageID received'
                            raise Exception(self.connection.lastError)
                        response = unprocessed
                        if response:  # if this statement is removed unprocessed data will be processed as another message
                            self.connection.lastError = 'unprocessed substrate error'
                            raise Exception(self.connection.lastError)
            else:
                return SESSION_TERMINATED_BY_SERVER

        ldapResponses.append(RESPONSE_COMPLETE)

        if ldapResponses[-2]['result'] == RESULT_REFERRAL and self.connection.autoReferrals:
            refResponse, refResult = self.doOperationOnReferral(self._outstanding[messageId],
                                                                ldapResponses[-2]['referrals'])
            if refResponse is not None:
                ldapResponses = refResponse + [refResult]
                ldapResponses.append(RESPONSE_COMPLETE)
            elif refResult is not None:
                ldapResponses = [refResult, RESPONSE_COMPLETE]

            self._referrals = []
        return ldapResponses
