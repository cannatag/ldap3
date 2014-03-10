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

from ldap3 import LDAP_MAX_INT, LDAPException
from ..protocol.convert import build_controls_list
from ..protocol.rfc2849 import to_ldif
from ..strategy.baseStrategy import BaseStrategy
from ..protocol.rfc4511 import LDAPMessage, MessageID, ProtocolOp


class LdifProducerStrategy(BaseStrategy):
    """
    This strategy is used to create the LDIF stream for the Add, Delete, Modify, ModifyDn operations.
    You send the request and get the request in the ldif-change representation of the operation.
    NO OPERATION IS SENT TO THE LDAP SERVER!
    Connection.request will contain the result LDAP message in a dict form
    Connection.response will contain the ldif-change format of the requested operation if available
    You don't need a real server to connect to for this strategy
    """

    def __init__(self, ldap_connection):
        BaseStrategy.__init__(self, ldap_connection)
        self.sync = True
        self.no_real_dsa = True
        self.restartable = False
        random.seed()

    def open(self, start_listening=True, reset_usage=True):
        pass

    def _start_listen(self):
        pass

    def receiving(self):
        return None

    def send(self, message_type, request, controls=None):
        """
        Build the LDAPMessage without sending to server
        """
        message_id = random.randint(0, LDAP_MAX_INT)
        ldap_message = LDAPMessage()
        ldap_message['messageID'] = MessageID(message_id)
        ldap_message['protocolOp'] = ProtocolOp().setComponentByName(message_type, request)
        message_controls = build_controls_list(controls)
        if message_controls is not None:
            ldap_message['controls'] = message_controls

        self.connection.request = BaseStrategy.decode_request(ldap_message)
        self.connection.request['controls'] = controls
        self._outstanding[message_id] = self.connection.request
        return message_id

    def post_send_single_response(self, message_id):
        self.connection.response = None
        self.connection.result = None
        if self._outstanding and message_id in self._outstanding:
            request = self._outstanding.pop(message_id)
            self.connection.response = to_ldif(self.connection.request['type'], request, False)

            return True

        return False

    def post_send_search(self, message_id):
        raise LDAPException('This strategy cannot produce ldif-content for Search Operations')

    def _get_response(self, message_id):
        pass
