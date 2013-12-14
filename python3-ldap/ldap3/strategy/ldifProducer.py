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
import random

from pyasn1.codec.ber import decoder
from ldap3.protocol.convert import buildControlsList
from ldap3.protocol.rfc2849 import convertToLDIF, toLDIF

from ldap3.strategy.baseStrategy import BaseStrategy
from ldap3 import SESSION_TERMINATED_BY_SERVER, RESPONSE_COMPLETE, SOCKET_SIZE, RESULT_REFERRAL, LDAP_MAX_INT
from ldap3.protocol.rfc4511 import LDAPMessage, MessageID, ProtocolOp


class LDIFProducerStrategy(BaseStrategy):
    """
    This strategy is used to create the LDIF stream for the Add, Delete, Modify, ModifyDn operations.
    You send the request and get the request in the ldif-change representation of the operation.
    NO OPERATION IS SENT TO THE LDAP SERVER!
    Connection.request will contain the result LDAP message in a dict form
    Connection.response will contain the ldif-change format of the requested operation if available
    You don't need a real server to connect to for this strategy
    """

    def __init__(self, ldapConnection):
        self.connection = ldapConnection
        self._outstanding = None
        self.sync = True
        self.noRealDSA = True
        random.seed()
        self._outstanding = dict()

    def open(self, startListening = True):
        pass

    def _startListen(self):
        pass

    def receiving(self):
        return None

    def send(self, messageType, request, controls = None):
        """
        Build the LDAPMessage without sending to server
        """
        messageId = random.randint(0, LDAP_MAX_INT)
        ldapMessage = LDAPMessage()
        ldapMessage['messageID'] = MessageID(messageId)
        ldapMessage['protocolOp'] = ProtocolOp().setComponentByName(messageType, request)
        messageControls = buildControlsList(controls)
        if messageControls is not None:
            ldapMessage['controls'] = messageControls

        self.connection.request = BaseStrategy.decodeRequest(ldapMessage)
        self._outstanding[messageId] = self.connection.request
        return messageId

    def postSendSingleResponse(self, messageId):
        self.connection.response = None
        self.connection.result = None
        if self._outstanding and messageId in self._outstanding:
            request = self._outstanding.pop(messageId)
            self.connection.response = toLDIF(self.connection.request['type'], request, False)

            return True

        return False

    def postSendSearch(self, messageId):
        raise Exception('This strategy cannot produce ldif-content for Search Operations')

    def _getResponse(self, messageId):
        pass
