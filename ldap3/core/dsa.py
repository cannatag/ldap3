"""
"""

# Created on 2015.02.06
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
from os import linesep
from threading import Lock
from datetime import datetime
from pyasn1.codec.ber import encoder

from .exceptions import LDAPExceptionError, LDAPUnknownRequestError
from ldap3 import RESULT_OPERATIONS_ERROR, RESULT_SUCCESS, RESULT_AUTH_METHOD_NOT_SUPPORTED, RESULT_INVALID_CREDENTIALS, \
    SIMPLE, ANONYMOUS, RESTARTABLE, RESULT_PROTOCOL_ERROR
from ..operation.bind import bind_response_operation
from ..strategy.base import BaseStrategy
from ..utils.ciDict import CaseInsensitiveDict
from ..protocol.rfc4511 import LDAPMessage, MessageID


class TreeNode(object):
    def __init__(self, tag=None, assertion=None):
        self.tag = tag
        self.parent = None
        self.assertion = assertion
        self.elements = []

    def append(self, filter_node):
        filter_node.parent = self
        self.elements.append(filter_node)
        return filter_node

    def __str__(self, pos=0):
        self.__repr__(pos)

    def __repr__(self, pos=0):
        node_tags = ['ROOT', 'AND', 'OR', 'NOT', 'MATCH_APPROX', 'MATCH_GREATER_OR_EQUAL', 'MATCH_LESS_OR_EQUAL', 'MATCH_EXTENSIBLE', 'MATCH_PRESENT', 'MATCH_SUBSTRING', 'MATCH_EQUAL']
        representation = ' ' * pos + 'tag: ' + node_tags[self.tag] + ' - assertion: ' + str(self.assertion)
        if self.elements:
            representation += ' - elements: ' + str(len(self.elements))
            for element in self.elements:
                representation += linesep + ' ' * pos + element.__repr__(pos + 2)
        return representation
class Client(object):
    def __init__(self, connection, authentication_type, user=None):
        self.bind_time = datetime.now()
        self.auth_type = authentication_type
        self.user = user
        self.connection = connection


class Dsa(object):
    def __init__(self, server):
        self.database = CaseInsensitiveDict()
        self.connections = dict()
        self.ready_to_send = dict()
        self.lock = Lock()
        self.server = server

    def produce_response(self, connection_id):
        message_id = min(self.ready_to_send.keys())
        print('SERVER: processing response', message_id)
        if message_id in self.ready_to_send:
            ldap_message = LDAPMessage()
            ldap_message['messageID'] = MessageID(message_id)
            ldap_message['protocolOp'] = self.ready_to_send.pop(message_id)
            encoded_message = encoder.encode(ldap_message)
            with self.lock:
                return encoded_message
        else:
            raise LDAPExceptionError('response not ready in mock server')

    def accept_request(self, connection_id, ldap_message):
        request = BaseStrategy.decode_request(ldap_message)
        print('SERVER: processing request', request, 'for', connection_id)

        response = None
        if request['type'] == 'bindRequest':
            response = self.do_bind(connection_id, request)
        elif request['type'] == 'unbindRequest':
            self.do_unbind(connection_id, request)
            pass  # unbind doesn't return anything
        elif request['type'] == 'addRequest':
            response = self.do_add(connection_id, request)
        elif request['type'] == 'compareRequest':
            response = self.do_compare(connection_id, request)
        elif request['type'] == 'delRequest':
            response = self.do_delete(connection_id, request)
        elif request['type'] == 'extendedReq':
            response = self.do_extended(connection_id, request)
        elif request['type'] == 'modifyRequest':
            response = self.do_modify(connection_id, request)
        elif request['type'] == 'modDNRequest':
            response = self.do_modify_dn(connection_id, request)
        elif request['type'] == 'searchRequest':
            response = self.do_search(connection_id, request)
        elif request['type'] == 'abandonRequest':
            response = self.do_abandon(connection_id, request)
        else:
            raise LDAPUnknownRequestError('unknown request')

        if response:
            self.ready_to_send[int(ldap_message['messageID'])] = response

    def do_open(self, connection_id):
        client = Client(connection=connection_id, authentication_type=ANONYMOUS)
        with self.lock:
            self.connections[connection_id] = client

    def do_bind(self, connection_id, request):
        if request['version'] == 3:
            if 'simple' in request['authentication']:
                if request['authentication']['simple'] == 'mock_password':
                    result_code = RESULT_SUCCESS
                    diagnostic_message='bind successful'
                    if connection_id in self.connections:
                        with self.lock:
                            self.connections[connection_id].user = request['name']
                    else:
                        result_code = RESULT_PROTOCOL_ERROR
                        diagnostic_message = 'connection not open'
                else:
                    result_code = RESULT_INVALID_CREDENTIALS
                    diagnostic_message = 'bind unsuccessful'
            else:
                result_code = RESULT_AUTH_METHOD_NOT_SUPPORTED
                diagnostic_message = 'only simple authentication allowed'
        else:
            result_code = RESULT_OPERATIONS_ERROR
            diagnostic_message = 'only version 3 of LDAP protocol is supported'

        response = bind_response_operation(result_code=result_code, diagnostic_message=diagnostic_message)
        return response

    def do_unbind(self, connection_id, request):
        with self.lock:
            del self.connections[connection_id]

    def do_add(self, connection_id, request):
        with self.lock:
            result = None
            return result

    def do_compare(self, connection_id, request):
        with self.lock:
            result = None
            return result

    def do_delete(self, connection_id, request):
        with self.lock:
            result = None
            return result

    def do_modify(self, connection_id, request):
        with self.lock:
            result = None
            return result

    def do_modify_dn(self, connection_id, request):
        with self.lock:
            result = None
            return result

    def do_search(self, connection_id, request):
        with self.lock:
            response = None
            return response

    def do_abandon(self, connection_id, request):
        with self.lock:
            result = None
            return result

    def do_extended(self, connection_id, request):
        with self.lock:
            result = None
            return result

