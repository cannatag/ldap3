"""
"""

# Created on 2013.07.15
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

from io import StringIO
from os import linesep
import random

from .. import LDAP_MAX_INT
from ..core.exceptions import LDAPLDIFError
from ..utils.conv import prepare_for_stream
from ..protocol.rfc4511 import LDAPMessage, MessageID, ProtocolOp
from ..protocol.rfc2849 import operation_to_ldif, add_ldif_header
from ..protocol.convert import build_controls_list
from .base import BaseStrategy


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
        self.pooled = False
        self.can_stream = True
        self.line_separator = linesep
        self.all_base64 = False
        self.stream = None
        self.order = dict()
        self._header_added = False
        random.seed()

    def _start_listen(self):
        self.connection.listening = True
        self.connection.closed = False
        self._header_added = False
        if not self.stream or (isinstance(self.stream, StringIO) and self.stream.closed):
            self.set_stream(StringIO())

    def _stop_listen(self):
        self.stream.close()
        self.connection.listening = False
        self.connection.closed = True

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
            ldif_lines = operation_to_ldif(self.connection.request['type'], request, self.all_base64, self.order.get(self.connection.request['type']))
            if self.stream and ldif_lines and not self.connection.closed:
                self.accumulate_stream(self.line_separator.join(ldif_lines))
            ldif_lines = add_ldif_header(ldif_lines)
            self.connection.response = self.line_separator.join(ldif_lines)
            return self.connection.response

        return None

    def post_send_search(self, message_id):
        raise LDAPLDIFError('LDIF-CONTENT cannot be produced for Search Operations')

    def _get_response(self, message_id):
        pass

    def accumulate_stream(self, fragment):
        if not self._header_added and self.stream.tell() == 0:
            self._header_added = True
            header = add_ldif_header(['-'])[0]
            self.stream.write(prepare_for_stream(header + self.line_separator + self.line_separator))
        self.stream.write(prepare_for_stream(fragment + self.line_separator + self.line_separator))

    def get_stream(self):
        return self.stream

    def set_stream(self, value):
        error = False
        try:
            if not value.writable():
                error = True
        except (ValueError, AttributeError):
            error = True

        if error:
            raise LDAPLDIFError('stream must be writable')

        self.stream = value
