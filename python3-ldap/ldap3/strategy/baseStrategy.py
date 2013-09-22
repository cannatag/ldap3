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

from pyasn1.codec.ber import encoder

from ldap3.protocol.rfc4511 import LDAPMessage, ProtocolOp, MessageID
from ldap3.operation.add import addResponseToDict, addRequestToDict
from ldap3.operation.modify import modifyRequestToDict, modifyResponseToDict
from ldap3.operation.search import searchResultReferenceResponseToDict, searchResultDoneResponseToDict, searchResultEntryResponseToDict, \
    searchRequestToDict
from ldap3.operation.bind import bindResponseToDict, bindRequestToDict
from ldap3.operation.compare import compareResponseToDict, compareRequestToDict
from ldap3.operation.extended import extendedRequestToDict, extendedResponseToDict, intermediateResponseToDict
from ldap3 import SESSION_TERMINATED_BY_SERVER, RESPONSE_SLEEPTIME, RESPONSE_WAITING_TIMEOUT, \
    SEARCH_SCOPE_BASE_OBJECT, SEARCH_SCOPE_WHOLE_SUBTREE, SEARCH_SCOPE_SINGLE_LEVEL, STRATEGY_SYNC, AUTH_ANONYMOUS
from ldap3.server import Server
from ldap3.operation.modifyDn import modifyDnRequestToDict, modifyDnResponseToDict
from ldap3.operation.delete import deleteResponseToDict, deleteRequestToDict
from ldap3.protocol.convert import prepareChangesForRequest, buildControlsList
from ldap3.operation.abandon import abandonRequestToDict
from ldap3.tls import Tls


class BaseStrategy(object):
    """
    Base class for connection strategy
    """

    def __init__(self, ldapConnection):
        self.connection = ldapConnection
        self._outstanding = None
        self._referrals = []

    def open(self, startListening = True):
        """
        Open a socket to a server
        """
        self._outstanding = dict()
        self._openSocket(self.connection.server.ssl)
        if self.connection.usage:
            self.connection.usage.start()

        if startListening:
            self._startListen()
        self.connection.refreshDsaInfo()

    def close(self):
        """
        Close connection
        """
        if not self.connection.closed:
            self._stopListen()
            self._closeSocket()
            self.connection.bound = False
            self.connection.request = None
            self.connection.response = None
            self._outstanding = None
            self._referrals = []
            if self.connection.usage:
                self.connection.usage.stop()

    def _openSocket(self, useSsl = False):
        """
        Try to open and connect a socket to a Server
        Raise exception if unable to open or connect socket
        """
        try:
            self.connection.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except Exception as e:
            self.connection.lastError = 'socket creation error: ' + str(e)
            raise Exception(self.connection.lastError)

        try:
            self.connection.socket.connect((self.connection.server.host, self.connection.server.port))
        except socket.error as e:
            self.connection.lastError = 'socket connection error: ' + str(e)
            raise Exception(self.connection.lastError)

        if useSsl:
            try:
                self.connection.socket = self.connection.server.tls.wrapSocket(self.connection.socket,
                                                                               doHandshake = True)
            except Exception as e:
                self.connection.lastError = 'socket ssl wrapping error: ' + str(e)
                raise Exception(self.connection.lastError)

        self.connection.closed = False

    def _closeSocket(self):
        """
        Try to close a socket
        Raise exception if unable to close socket
        """
        try:
            self.connection.socket.shutdown(socket.SHUT_RDWR)
            self.connection.socket.close()
        except Exception as e:
            self.connection.lastError = 'socket closing error' + str(e)
            raise Exception(self.connection.lastError)
        self.connection.socket = None
        self.connection.closed = True

    def _stopListen(self):
        self.connection.listening = False

    def send(self, messageType, request, controls = None):
        """
        Send an LDAP message
        Returns the messageId
        """
        self.connection.request = None
        if self.connection.listening:
            if self.connection.saslInProgress and messageType not in ['bindRequest']:  # as per rfc 4511 (4.2.1)
                self.connection.lastError = 'cannot send operation requests while SASL bind is in progress'
                raise Exception(self.connection.lastError)
            messageId = self.connection.server.nextMessageId()
            ldapMessage = LDAPMessage()
            ldapMessage['messageID'] = MessageID(messageId)
            ldapMessage['protocolOp'] = ProtocolOp().setComponentByName(messageType, request)
            messageControls = buildControlsList(controls)
            if messageControls is not None:
                ldapMessage['controls'] = messageControls

            try:
                encodedMessage = encoder.encode(ldapMessage)
                self.connection.socket.sendall(encodedMessage)
            except socket.error as e:
                self.connection.lastError = 'socket sending error' + str(e)
                raise Exception(self.connection.lastError)

            self.connection.request = BaseStrategy.decodeRequest(ldapMessage)
            self._outstanding[messageId] = self.connection.request
            if self.connection.usage:
                self.connection.usage.transmittedMessage(self.connection.request, len(encodedMessage))
        else:
            self.connection.lastError = 'unable to send message, socket is not open'
            raise Exception(self.connection.lastError)

        return messageId

    def getResponse(self, messageId, timeout = RESPONSE_WAITING_TIMEOUT):
        """
        Get response LDAP messages
        Responses are returned by the underlying connection strategy
        Check if messageId LDAP message is still outstanding and wait for timeout to see if it appears in _getResponse
        All response messages are returned
        Result is stored in connection.result
        Responses without result is stored in connection.response
        """
        response = None
        self.connection.response = None
        self.connection.result = None
        if self._outstanding and messageId in self._outstanding:
            while timeout >= 0:  # waiting for completed message to appear in _responses
                responses = self._getResponse(messageId)
                if responses == SESSION_TERMINATED_BY_SERVER:
                    self.connection.close()
                    self.connection.lastError = 'session terminated by server'
                    raise Exception(self.connection.lastError)
                if not responses:
                    sleep(RESPONSE_SLEEPTIME)
                    timeout -= RESPONSE_SLEEPTIME
                else:
                    timeout = -1
                    if responses:
                        self._outstanding.pop(messageId)
                        self.connection.response = responses[:-2] if len(responses) > 2 else []
                        self.connection.result = responses[-2]
                        response = [responses[0]] if len(responses) == 2 else responses[
                                                                              :-1]  # remove the response complete flag
        return response



    @classmethod
    def computeLDAPMessageSize(cls, data):
        """
        Compute LDAP Message size according to BER definite length rules
        Returns -1 if too few data to compute message length
        """
        if isinstance(data, str):  # fix for python2
            data = bytearray(data)
        retValue = -1
        if len(data) > 2:
            if data[1] <= 127:  # BER definite length - short form. Highest bit of byte 1 is 0, message length is in the last 7 bits - Value can be up to 127 bytes long
                retValue = data[1] + 2
            else:  # BER definite length - long form. Highest bit of byte 1 is 1, last 7 bits counts the number of following octets containing the value length
                bytesLength = data[1] - 128
                if len(data) >= bytesLength + 2:
                    valueLength = 0
                    cont = bytesLength
                    for byte in data[2:2 + bytesLength]:
                        cont -= 1
                        valueLength += byte * (256 ** cont)
                    retValue = valueLength + 2 + bytesLength

        return retValue

    @classmethod
    def decodeResponse(cls, ldapMessage):
        """
        Convert received LDAPMessage to a dict
        """
        messageType = ldapMessage.getComponentByName('protocolOp').getName()
        component = ldapMessage['protocolOp'].getComponent()
        if messageType == 'bindResponse':
            result = bindResponseToDict(component)
        elif messageType == 'searchResEntry':
            result = searchResultEntryResponseToDict(component)
        elif messageType == 'searchResDone':
            result = searchResultDoneResponseToDict(component)
        elif messageType == 'searchResRef':
            result = searchResultReferenceResponseToDict(component)
        elif messageType == 'modifyResponse':
            result = modifyResponseToDict(component)
        elif messageType == 'addResponse':
            result = addResponseToDict(component)
        elif messageType == 'delResponse':
            result = deleteResponseToDict(component)
        elif messageType == 'modDNResponse':
            result = modifyDnResponseToDict(component)
        elif messageType == 'compareResponse':
            result = compareResponseToDict(component)
        elif messageType == 'extendedResp':
            result = extendedResponseToDict(component)
        elif messageType == 'intermediateResponse':
            result = intermediateResponseToDict(component)
        else:
            raise Exception('unknown response')
        result['type'] = messageType
        return result

    @classmethod
    def decodeRequest(cls, ldapMessage):
        messageType = ldapMessage.getComponentByName('protocolOp').getName()
        component = ldapMessage['protocolOp'].getComponent()
        if messageType == 'bindRequest':
            result = bindRequestToDict(component)
        elif messageType == 'unbindRequest':
            result = dict()
        elif messageType == 'addRequest':
            result = addRequestToDict(component)
        elif messageType == 'compareRequest':
            result = compareRequestToDict(component)
        elif messageType == 'delRequest':
            result = deleteRequestToDict(component)
        elif messageType == 'extendedReq':
            result = extendedRequestToDict(component)
        elif messageType == 'modifyRequest':
            result = modifyRequestToDict(component)
        elif messageType == 'modDNRequest':
            result = modifyDnRequestToDict(component)
        elif messageType == 'searchRequest':
            result = searchRequestToDict(component)
        elif messageType == 'abandonRequest':
            result = abandonRequestToDict(component)
        else:
            raise Exception('unknown request')
        result['type'] = messageType
        return result

    def validReferralList(self, referrals):
        referralList = []
        for referral in referrals:
            candidateReferral = BaseStrategy.decodeReferral(referral)
            if candidateReferral:
                for refHost in self.connection.server.allowedReferralHosts:
                    if refHost[0] == candidateReferral['host'] or refHost[0] == '*':
                        if candidateReferral['host'] not in self._referrals:
                            candidateReferral['anonymousBindOnly'] = not refHost[1]
                            referralList.append(candidateReferral)
                            break

        return referralList

    @classmethod
    def decodeReferral(cls, uri):
        """
        Decoce referral URI as specified in RFC 4516 relaxing specifications
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

    def doOperationOnReferral(self, request, referrals):
        validReferralList = self.validReferralList(referrals)
        if validReferralList:
            preferredReferralList = [referral for referral in validReferralList if
                                     referral['ssl'] == self.connection.server.ssl]
            selectedReferral = choice(preferredReferralList) if preferredReferralList else choice(validReferralList)

            referralServer = Server(
                host = selectedReferral['host'],
                port = selectedReferral['port'] or self.connection.server.port,
                useSsl = selectedReferral['ssl'],
                allowedReferralHosts = self.connection.server.allowedReferralHosts,
                tls = Tls(
                    localPrivateKeyFile = self.connection.server.tls.privateKeyFile,
                    localCertificateFile = self.connection.server.tls.certificateFile,
                    validate = self.connection.server.tls.validate,
                    version = self.connection.server.tls.version,
                    caCertsFile = self.connection.server.tls.caCertsFile
                )
            )
            from ldap3.connection import Connection
            referralConnection = Connection(
                server = referralServer,
                user = self.connection.user if not selectedReferral['anonymousBindOnly'] else None,
                password = self.connection.password if not selectedReferral['anonymousBindOnly'] else None,
                version = self.connection.version,
                authentication = self.connection.authentication if not selectedReferral[
                    'anonymousBindOnly'] else AUTH_ANONYMOUS,
                clientStrategy = STRATEGY_SYNC,
                autoReferrals = True
            )

            referralConnection.open()
            referralConnection.strategy._referrals = self._referrals
            if self.connection.bound:
                referralConnection.bind()

            if request['type'] == 'searchRequest':
                referralConnection.search(
                    selectedReferral['base'] or request['base'],
                    selectedReferral['filter'] or request['filter'],
                    selectedReferral['scope'] or request['scope'],
                    request['dereferenceAlias'],
                    selectedReferral['attributes'] or request['attributes'],
                    request['sizeLimit'],
                    request['timeLimit'],
                    request['typeOnly']
                )
            elif request['type'] == 'addRequest':
                referralConnection.add(
                    selectedReferral['base'] or request['entry'],
                    None,
                    request['attributes']
                )
            elif request['type'] == 'compareRequest':
                referralConnection.compare(
                    selectedReferral['base'] or request['entry'],
                    request['attribute'],
                    request['value']
                )
            elif request['type'] == 'delRequest':
                referralConnection.delete(
                    selectedReferral['base'] or request['entry'],
                )
            elif request['type'] == 'extendedRequest':
                # tbd
                raise NotImplemented()
            elif request['type'] == 'modifyRequest':
                referralConnection.modify(
                    selectedReferral['base'] or request['entry'],
                    prepareChangesForRequest(request['changes'])
                )
            elif request['type'] == 'modDNRequest':
                referralConnection.modifyDn(
                    selectedReferral['base'] or request['entry'],
                    request['newRdn'],
                    request['deleteOldRdn'],
                    request['newSuperior']
                )
            else:
                raise Exception('referral operation not permitted')

            response = referralConnection.response
            result = referralConnection.result
            referralConnection.close()
        else:
            response = None
            result = None

        return response, result

    def _startListen(self):
        #overridden on strategy class
        pass

    def _getResponse(self, messageId):
        # overridden in strategy class
        pass
