"""
Created on 15/lug/2013

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

import socket
from time import sleep
from random import choice

from pyasn1.codec.ber import encoder, decoder

from .. import SESSION_TERMINATED_BY_SERVER, RESPONSE_SLEEPTIME, RESPONSE_WAITING_TIMEOUT, SEARCH_SCOPE_BASE_OBJECT, SEARCH_SCOPE_WHOLE_SUBTREE, SEARCH_SCOPE_SINGLE_LEVEL, STRATEGY_SYNC, AUTH_ANONYMOUS, DO_NOT_RAISE_EXCEPTIONS
from ..core.exceptions import LDAPOperationResult, LDAPSASLBindInProgressError, LDAPSocketOpenError, LDAPSessionTerminatedByServer, LDAPUnknownResponseError, LDAPUnknownRequestError, LDAPReferralError, communication_exception_factory, \
    LDAPSocketSendError, LDAPExceptionError, LDAPSocketCloseError
from ..protocol.rfc4511 import LDAPMessage, ProtocolOp, MessageID
from ..operation.add import add_response_to_dict, add_request_to_dict
from ..operation.modify import modify_request_to_dict, modify_response_to_dict
from ..operation.search import search_result_reference_response_to_dict, search_result_done_response_to_dict, search_result_entry_response_to_dict, search_request_to_dict
from ..operation.bind import bind_response_to_dict, bind_request_to_dict
from ..operation.compare import compare_response_to_dict, compare_request_to_dict
from ..operation.extended import extended_request_to_dict, extended_response_to_dict, intermediate_response_to_dict
from ..core.server import Server
from ..operation.modifyDn import modify_dn_request_to_dict, modify_dn_response_to_dict
from ..operation.delete import delete_response_to_dict, delete_request_to_dict
from ..protocol.convert import prepare_changes_for_request, build_controls_list
from ..operation.abandon import abandon_request_to_dict
from ..core.tls import Tls
from ..protocol.oid import Oids
from ..protocol.rfc2696 import RealSearchControlValue


# noinspection PyProtectedMember
class BaseStrategy(object):
    """
    Base class for connection strategy
    """

    def __init__(self, ldap_connection):
        self.connection = ldap_connection
        self._outstanding = dict()
        self._referrals = []
        self.sync = None  # indicates a synchronous connection
        self.no_real_dsa = None  # indicates a connection to a fake LDAP server
        self.pooled = None  # Indicates a connection with a connection pool
        self.can_stream = False  # indicate if a strategy keep a stream of responses (i.e. LDIFProducer can accumulate responses with a single header). Stream must be initilized and closed in _start_listen() and _stop_listen()

    def open(self, reset_usage=True):
        """
        Open a socket to a server. Choose a server from the server pool if available
        """
        if self.connection.lazy and not self.connection._executing_deferred:
            self.connection._deferred_open = True
            self.connection.closed = False
        else:
            if not self.connection.closed and not self.connection._executing_deferred:  # try to close connection if still open
                self.close()

            self._outstanding = dict()
            if self.connection._usage:
                if reset_usage or not self.connection._usage.initial_connection_start_time:
                    self.connection._usage.start()

            if self.connection.server_pool:
                new_server = self.connection.server_pool.get_server(self.connection)  # get a server from the server_pool if available
                if self.connection.server != new_server:
                    self.connection.server = new_server
                    if self.connection._usage:
                        self.connection._usage.servers_from_pool += 1

            if not self.no_real_dsa:
                self._open_socket(self.connection.server.ssl)

            self.connection._deferred_open = False
            self._start_listen()

    def close(self):
        """
        Close connection
        """
        if self.connection.lazy and not self.connection._executing_deferred and (self.connection._deferred_bind or self.connection._deferred_open):
            self.connection.listening = False
            self.connection.closed = True
        else:
            if not self.connection.closed:
                self._stop_listen()
                if not self. no_real_dsa:
                    self._close_socket()

        self.connection.bound = False
        self.connection.request = None
        self.connection.response = None
        self.connection.tls_started = False
        self._outstanding = dict()
        self._referrals = []
        if self.connection._usage:
            self.connection._usage.stop()

    def _open_socket(self, use_ssl=False):
        """
        Tries to open and connect a socket to a Server
        raise LDAPExceptionError if unable to open or connect socket
        """
        exc = None
        try:
            self.connection.socket = socket.socket(*self.connection.server.address_info[0][:3])
        except Exception as e:
            self.connection.last_error = 'socket creation error: ' + str(e)
            exc = e

        if exc:
            raise communication_exception_factory(LDAPSocketOpenError, exc)(self.connection.last_error)

        try:
            self.connection.socket.connect(self.connection.server.address_info[0][4])
        except socket.error as e:
            self.connection.last_error = 'socket connection error: ' + str(e)
            exc = e

        if exc:
            raise communication_exception_factory(LDAPSocketOpenError, exc)(self.connection.last_error)

        if use_ssl:
            try:
                self.connection.server.tls.wrap_socket(self.connection, do_handshake=True)
                if self.connection._usage:
                    self.connection._usage.wrapped_sockets += 1
            except Exception as e:
                self.connection.last_error = 'socket ssl wrapping error: ' + str(e)
                exc = e

            if exc:
                raise communication_exception_factory(LDAPSocketOpenError, exc)(self.connection.last_error)

        if self.connection._usage:
            self.connection._usage.opened_sockets += 1

        self.connection.closed = False

    def _close_socket(self):
        """
        Try to close a socket
        raise LDAPExceptionError if unable to close socket
        """
        exc = None

        try:
            self.connection.socket.shutdown(socket.SHUT_RDWR)
            self.connection.socket.close()
        except Exception as e:
            self.connection.last_error = 'socket closing error' + str(e)
            exc = e

        if exc:
            raise communication_exception_factory(LDAPSocketCloseError, exc)(self.connection.last_error)

        self.connection.socket = None
        self.connection.closed = True

        if self.connection._usage:
            self.connection._usage.closed_sockets += 1

    def _stop_listen(self):
        self.connection.listening = False

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
            ldap_message = LDAPMessage()
            ldap_message['messageID'] = MessageID(message_id)
            ldap_message['protocolOp'] = ProtocolOp().setComponentByName(message_type, request)
            message_controls = build_controls_list(controls)
            if message_controls is not None:
                ldap_message['controls'] = message_controls

            try:
                encoded_message = encoder.encode(ldap_message)
                self.connection.socket.sendall(encoded_message)
            except socket.error as e:
                self.connection.last_error = 'socket sending error' + str(e)
                encoded_message = None
                exc = e

            if exc:
                raise communication_exception_factory(LDAPSocketSendError, exc)(self.connection.last_error)

            self.connection.request = BaseStrategy.decode_request(ldap_message)
            self.connection.request['controls'] = controls
            self._outstanding[message_id] = self.connection.request
            if self.connection._usage:
                self.connection._usage.transmitted_message(self.connection.request, len(encoded_message))
        else:
            self.connection.last_error = 'unable to send message, socket is not open'
            raise LDAPSocketOpenError(self.connection.last_error)

        return message_id

    def get_response(self, message_id, timeout=RESPONSE_WAITING_TIMEOUT):
        """
        Get response LDAP messages
        Responses are returned by the underlying connection strategy
        Check if message_id LDAP message is still outstanding and wait for timeout to see if it appears in _get_response
        Result is stored in connection.result
        Responses without result is stored in connection.response
        A tuple (responses, result) is returned
        """
        response = None
        result = None
        if self._outstanding and message_id in self._outstanding:
            while timeout >= 0:  # waiting for completed message to appear in responses
                responses = self._get_response(message_id)
                if responses == SESSION_TERMINATED_BY_SERVER:
                    try:  # try to close the session but don't raise any error if server has already closed the session
                        self.close()
                    except (socket.error, LDAPExceptionError):
                        pass
                    self.connection.last_error = 'session terminated by server'
                    raise LDAPSessionTerminatedByServer(self.connection.last_error)
                if not responses:
                    sleep(RESPONSE_SLEEPTIME)
                    timeout -= RESPONSE_SLEEPTIME
                else:
                    if responses:
                        self._outstanding.pop(message_id)
                        result = responses[-2]
                        response = responses[:-2]
                        self.connection.result = result
                        self.connection.response = None
                    break
            if self.connection.raise_exceptions and result and result['result'] not in DO_NOT_RAISE_EXCEPTIONS:
                raise LDAPOperationResult(result=result['result'], description=result['description'], dn=result['dn'], message=result['message'], response_type=result['type'], response=response)

        return response, result

    @classmethod
    def compute_ldap_message_size(cls, data):
        """
        Compute LDAP Message size according to BER definite length rules
        Returns -1 if too few data to compute message length
        """
        if isinstance(data, str):  # fix for Python 2, data is string not bytes
            data = bytearray(data)  # Python 2 bytearray is equivalent to Python 3 bytes

        ret_value = -1
        if len(data) > 2:
            if data[1] <= 127:  # BER definite length - short form. Highest bit of byte 1 is 0, message length is in the last 7 bits - Value can be up to 127 bytes long
                ret_value = data[1] + 2
            else:  # BER definite length - long form. Highest bit of byte 1 is 1, last 7 bits counts the number of following octets containing the value length
                bytes_length = data[1] - 128
                if len(data) >= bytes_length + 2:
                    value_length = 0
                    cont = bytes_length
                    for byte in data[2:2 + bytes_length]:
                        cont -= 1
                        value_length += byte * (256 ** cont)
                    ret_value = value_length + 2 + bytes_length

        return ret_value

    # @classmethod
    def decode_response(self, ldap_message):
        """
        Convert received LDAPMessage to a dict
        """
        message_type = ldap_message.getComponentByName('protocolOp').getName()
        component = ldap_message['protocolOp'].getComponent()
        controls = ldap_message['controls']
        if message_type == 'bindResponse':
            result = bind_response_to_dict(component)
        elif message_type == 'searchResEntry':
            result = search_result_entry_response_to_dict(component, self.connection.server.schema, self.connection.server.custom_formatter, self.connection.check_names)
        elif message_type == 'searchResDone':
            result = search_result_done_response_to_dict(component)
        elif message_type == 'searchResRef':
            result = search_result_reference_response_to_dict(component)
        elif message_type == 'modifyResponse':
            result = modify_response_to_dict(component)
        elif message_type == 'addResponse':
            result = add_response_to_dict(component)
        elif message_type == 'delResponse':
            result = delete_response_to_dict(component)
        elif message_type == 'modDNResponse':
            result = modify_dn_response_to_dict(component)
        elif message_type == 'compareResponse':
            result = compare_response_to_dict(component)
        elif message_type == 'extendedResp':
            result = extended_response_to_dict(component)
        elif message_type == 'intermediateResponse':
            result = intermediate_response_to_dict(component)
        else:
            raise LDAPUnknownResponseError('unknown response')
        result['type'] = message_type
        if controls:
            result['controls'] = dict()
            for control in controls:
                decoded_control = self.decode_control(control)
                result['controls'][decoded_control[0]] = decoded_control[1]
        return result

    @classmethod
    def decode_control(cls, control):
        """
        decode control, return a 2-element tuple where the first element is the control oid
        and the second element is a dictionary with description (from Oids), criticality and decoded control value
        """
        control_type = str(control['controlType'])
        criticality = bool(control['criticality'])
        control_value = bytes(control['controlValue'])
        if control_type == '1.2.840.113556.1.4.319':  # simple paged search as per RFC2696
            control_resp, unprocessed = decoder.decode(control_value, asn1Spec=RealSearchControlValue())
            control_value = dict()
            control_value['size'] = int(control_resp['size'])
            control_value['cookie'] = bytes(control_resp['cookie'])

        return control_type, {'description': Oids.get(control_type, ''), 'criticality': criticality, 'value': control_value}

    @classmethod
    def decode_request(cls, ldap_message):
        message_type = ldap_message.getComponentByName('protocolOp').getName()
        component = ldap_message['protocolOp'].getComponent()
        if message_type == 'bindRequest':
            result = bind_request_to_dict(component)
        elif message_type == 'unbindRequest':
            result = dict()
        elif message_type == 'addRequest':
            result = add_request_to_dict(component)
        elif message_type == 'compareRequest':
            result = compare_request_to_dict(component)
        elif message_type == 'delRequest':
            result = delete_request_to_dict(component)
        elif message_type == 'extendedReq':
            result = extended_request_to_dict(component)
        elif message_type == 'modifyRequest':
            result = modify_request_to_dict(component)
        elif message_type == 'modDNRequest':
            result = modify_dn_request_to_dict(component)
        elif message_type == 'searchRequest':
            result = search_request_to_dict(component)
        elif message_type == 'abandonRequest':
            result = abandon_request_to_dict(component)
        else:
            raise LDAPUnknownRequestError('unknown request')
        result['type'] = message_type
        return result

    def valid_referral_list(self, referrals):
        referral_list = []
        for referral in referrals:
            candidate_referral = BaseStrategy.decode_referral(referral)
            if candidate_referral:
                for ref_host in self.connection.server.allowed_referral_hosts:
                    if ref_host[0] == candidate_referral['host'] or ref_host[0] == '*':
                        if candidate_referral['host'] not in self._referrals:
                            candidate_referral['anonymousBindOnly'] = not ref_host[1]
                            referral_list.append(candidate_referral)
                            break

        return referral_list

    @classmethod
    def decode_referral(cls, uri):
        """
        Decode referral URI as specified in RFC 4516 relaxing specifications
        permitting 'ldaps' as scheme meaning ssl-ldap

        ldapurl     = scheme COLON SLASH SLASH [host [COLON port]]
                       [SLASH dn [QUESTION [attributes]
                       [QUESTION [scope] [QUESTION [filter]
                       [QUESTION extensions]]]]]
                                      ; <host> and <port> are defined
                                      ;   in Sections 3.2.2 and 3.2.3
                                      ;   of [RFC3986].
                                      ; <filter> is from Section 3 of
                                      ;   [RFC4515], subject to the
                                      ;   provisions of the
                                      ;   "Percent-Encoding" section
                                      ;   below.

        scheme      = "ldap" / "ldaps"  <== not RFC4516 compliant (original is 'scheme      = "ldap"')
        dn          = distinguishedName ; From Section 3 of [RFC4514],
                                      ; subject to the provisions of
                                      ; the "Percent-Encoding"
                                      ; section below.

        attributes  = attrdesc *(COMMA attrdesc)
        attrdesc    = selector *(COMMA selector)
        selector    = attributeSelector ; From Section 4.5.1 of
                                      ; [RFC4511], subject to the
                                      ; provisions of the
                                      ; "Percent-Encoding" section
                                      ; below.

        scope       = "base" / "one" / "sub"
        extensions  = extension *(COMMA extension)
        extension   = [EXCLAMATION] extype [EQUALS exvalue]
        extype      = oid               ; From section 1.4 of [RFC4512].

        exvalue     = LDAPString        ; From section 4.1.2 of
                                      ; [RFC4511], subject to the
                                      ; provisions of the
                                      ; "Percent-Encoding" section
                                      ; below.

        EXCLAMATION = %x21              ; exclamation mark ("!")
        SLASH       = %x2F              ; forward slash ("/")
        COLON       = %x3A              ; colon (":")
        QUESTION    = %x3F              ; question mark ("?")
        """

        referral = dict()
        parts = uri.split('?')
        scheme, sep, remain = parts[0].partition('://')
        if sep != '://' or scheme not in ['ldap', 'ldaps']:
            return None

        address, _, referral['base'] = remain.partition('/')

        referral['ssl'] = True if scheme == 'ldaps' else False
        referral['host'], sep, referral['port'] = address.partition(':')
        if sep != ':':
            referral['port'] = None
        else:
            if not referral['port'].isdigit() or not (0 < int(referral['port']) < 65536):
                return None
            else:
                referral['port'] = int(referral['port'])

        referral['attributes'] = parts[1].split(',') if len(parts) > 1 else None
        referral['scope'] = parts[2] if len(parts) > 2 else None
        if referral['scope'] == 'base':
            referral['scope'] = SEARCH_SCOPE_BASE_OBJECT
        elif referral['scope'] == 'sub':
            referral['scope'] = SEARCH_SCOPE_WHOLE_SUBTREE
        elif referral['scope'] == 'one':
            referral['scope'] = SEARCH_SCOPE_SINGLE_LEVEL
        elif referral['scope']:
            return None

        referral['filter'] = parts[3] if len(parts) > 3 else None
        referral['extensions'] = parts[3].split(',') if len(parts) > 4 else None

        return referral

    def do_operation_on_referral(self, request, referrals):
        valid_referral_list = self.valid_referral_list(referrals)
        if valid_referral_list:
            preferred_referral_list = [referral for referral in valid_referral_list if referral['ssl'] == self.connection.server.ssl]
            selected_referral = choice(preferred_referral_list) if preferred_referral_list else choice(valid_referral_list)

            referral_server = Server(host=selected_referral['host'],
                                     port=selected_referral['port'] or self.connection.server.port,
                                     use_ssl=selected_referral['ssl'],
                                     allowed_referral_hosts=self.connection.server.allowed_referral_hosts,
                                     tls=Tls(local_private_key_file=self.connection.server.tls.private_key_file,
                                             local_certificate_file=self.connection.server.tls.certificate_file,
                                             validate=self.connection.server.tls.validate,
                                             version=self.connection.server.tls.version,
                                             ca_certs_file=self.connection.server.tls.ca_certs_file) if selected_referral['ssl'] else None)

            from ..core.connection import Connection

            referral_connection = Connection(server=referral_server,
                                             user=self.connection.user if not selected_referral['anonymousBindOnly'] else None,
                                             password=self.connection.password if not selected_referral['anonymousBindOnly'] else None,
                                             version=self.connection.version,
                                             authentication=self.connection.authentication if not selected_referral['anonymousBindOnly'] else AUTH_ANONYMOUS,
                                             client_strategy=STRATEGY_SYNC,
                                             auto_referrals=True,
                                             read_only=self.connection.read_only)

            if self.connection._usage:
                self.connection._usage.referrals_followed += 1

            referral_connection.open()
            referral_connection.strategy._referrals = self._referrals
            if self.connection.bound:
                referral_connection.bind()

            if request['type'] == 'searchRequest':
                referral_connection.search(selected_referral['base'] or request['base'],
                                           selected_referral['filter'] or request['filter'],
                                           selected_referral['scope'] or request['scope'],
                                           request['dereferenceAlias'],
                                           selected_referral['attributes'] or request['attributes'],
                                           request['sizeLimit'],
                                           request['timeLimit'],
                                           request['typeOnly'],
                                           controls=request['controls'])
            elif request['type'] == 'addRequest':
                referral_connection.add(selected_referral['base'] or request['entry'],
                                        None,
                                        request['attributes'],
                                        controls=request['controls'])
            elif request['type'] == 'compareRequest':
                referral_connection.compare(selected_referral['base'] or request['entry'],
                                            request['attribute'],
                                            request['value'],
                                            controls=request['controls'])
            elif request['type'] == 'delRequest':
                referral_connection.delete(selected_referral['base'] or request['entry'],
                                           controls=request['controls'])
            elif request['type'] == 'extendedRequest':
                # TODO
                raise NotImplementedError()
            elif request['type'] == 'modifyRequest':
                referral_connection.modify(selected_referral['base'] or request['entry'],
                                           prepare_changes_for_request(request['changes']),
                                           controls=request['controls'])
            elif request['type'] == 'modDNRequest':
                referral_connection.modify_dn(selected_referral['base'] or request['entry'],
                                              request['newRdn'],
                                              request['deleteOldRdn'],
                                              request['newSuperior'],
                                              controls=request['controls'])
            else:
                self.connection.last_error = 'referral operation not permitted'
                raise LDAPReferralError(self.connection.last_error)

            response = referral_connection.response
            result = referral_connection.result
            referral_connection.unbind()
        else:
            response = None
            result = None

        return response, result

    def _start_listen(self):
        #overridden on strategy class
        raise NotImplementedError

    def _get_response(self, message_id):
        # overridden in strategy class
        raise NotImplementedError

    def receiving(self):
        # overridden in strategy class
        raise NotImplementedError

    def post_send_single_response(self, message_id):
        # overridden in strategy class
        raise NotImplementedError

    def post_send_search(self, message_id):
        # overridden in strategy class
        raise NotImplementedError

    def get_stream(self):
        raise NotImplementedError

    def set_stream(self, value):
        raise NotImplementedError
