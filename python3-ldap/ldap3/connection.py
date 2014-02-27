"""
Created on 2013.05.31

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

from threading import Lock
from datetime import datetime
from os import linesep

from pyasn1.codec.ber import encoder

from ldap3 import AUTH_ANONYMOUS, AUTH_SIMPLE, AUTH_SASL, MODIFY_ADD, MODIFY_DELETE, MODIFY_REPLACE, SEARCH_DEREFERENCE_ALWAYS, SEARCH_SCOPE_WHOLE_SUBTREE, STRATEGY_ASYNC_THREADED, STRATEGY_SYNC, CLIENT_STRATEGIES, RESULT_SUCCESS, RESULT_COMPARE_TRUE, NO_ATTRIBUTES, ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES, MODIFY_INCREMENT, STRATEGY_LDIF_PRODUCER, SASL_AVAILABLE_MECHANISMS, \
    LDAPException

from .operation.abandon import abandonOperation
from .operation.add import addOperation
from .operation.bind import bindOperation
from .operation.compare import compareOperation
from .operation.delete import deleteOperation
from .operation.extended import extendedOperation
from .operation.modify import modifyOperation
from .operation.modifyDn import modifyDnOperation
from .operation.search import searchOperation
from .protocol.rfc2849 import toLdif
from .protocol.sasl.digestMd5 import saslDigestMd5
from .protocol.sasl.external import saslExternal
from .strategy.asyncThreaded import AsyncThreadedStrategy
from .strategy.ldifProducer import LdifProducerStrategy
from .strategy.syncWait import SyncWaitStrategy
from .operation.unbind import unbindOperation
from .protocol.rfc2696 import RealSearchControlValue, Cookie, Size


class ConnectionUsage(object):
    """
    Collect statistics on connection usage
    """

    def reset(self):
        self.connectionStartTime = None
        self.connectionStopTime = None
        self.bytesTransmitted = 0
        self.bytesReceived = 0
        self.messagesTransmitted = 0
        self.messagesReceived = 0
        self.operations = 0
        self.abandonOperations = 0
        self.addOperations = 0
        self.bindOperations = 0
        self.compareOperations = 0
        self.deleteOperations = 0
        self.extendedOperations = 0
        self.modifyOperations = 0
        self.modifyDnOperations = 0
        self.searchOperations = 0
        self.unbindOperations = 0

    def __init__(self):
        self.connectionStartTime = None
        self.connectionStopTime = None
        self.bytesTransmitted = 0
        self.bytesReceived = 0
        self.messagesTransmitted = 0
        self.messagesReceived = 0
        self.operations = 0
        self.abandonOperations = 0
        self.addOperations = 0
        self.bindOperations = 0
        self.compareOperations = 0
        self.deleteOperations = 0
        self.extendedOperations = 0
        self.modifyOperations = 0
        self.modifyDnOperations = 0
        self.searchOperations = 0
        self.unbindOperations = 0

    def __repr__(self):
        r = 'Connection Usage:' + linesep
        r += '  Time: [elapsed: ' + str(self.elapsedTime) + ']' + linesep
        r += '    Start Time: ' + (str(self.connectionStartTime.ctime()) if self.connectionStartTime else '') + linesep
        r += '    Stop Time: ' + (str(self.connectionStopTime.ctime()) if self.connectionStopTime else '') + linesep
        r += '  Bytes: ' + str(self.bytesTransmitted + self.bytesReceived) + linesep
        r += '    Transmitted: ' + str(self.bytesTransmitted) + linesep
        r += '    Received: ' + str(self.bytesReceived) + linesep
        r += '  Messages:' + str(self.messagesTransmitted + self.messagesReceived) + linesep
        r += '    Trasmitted: ' + str(self.messagesTransmitted) + linesep
        r += '    Received: ' + str(self.messagesReceived) + linesep
        r += '  Operations: ' + str(self.operations) + linesep
        r += '    Abandon: ' + str(self.abandonOperations) + linesep
        r += '    Bind: ' + str(self.bindOperations) + linesep
        r += '    Compare: ' + str(self.compareOperations) + linesep
        r += '    Delete: ' + str(self.deleteOperations) + linesep
        r += '    Extended: ' + str(self.extendedOperations) + linesep
        r += '    Modify: ' + str(self.modifyOperations) + linesep
        r += '    ModifyDn: ' + str(self.modifyDnOperations) + linesep
        r += '    Search: ' + str(self.searchOperations) + linesep
        r += '    Unbind: ' + str(self.unbindOperations) + linesep

        return r

    def transmittedMessage(self, message, length):
        self.bytesTransmitted += length
        self.operations += 1
        self.messagesTransmitted += 1
        if message['type'] == 'abandonRequest':
            self.abandonOperations += 1
        elif message['type'] == 'addRequest':
            self.addOperations += 1
        elif message['type'] == 'bindRequest':
            self.bindOperations += 1
        elif message['type'] == 'compareRequest':
            self.compareOperations += 1
        elif message['type'] == 'delRequest':
            self.deleteOperations += 1
        elif message['type'] == 'extendedReq':
            self.extendedOperations += 1
        elif message['type'] == 'modifyRequest':
            self.modifyOperations += 1
        elif message['type'] == 'modDNRequest':
            self.modifyDnOperations += 1
        elif message['type'] == 'searchRequest':
            self.searchOperations += 1
        elif message['type'] == 'unbindRequest':
            self.unbindOperations += 1
        else:
            raise LDAPException('unable to collect usage for unknown message type')

    def receivedMessage(self, length):
        self.bytesReceived += length
        self.messagesReceived += 1

    def start(self):
        self.reset()
        self.connectionStartTime = datetime.now()

    def stop(self):
        if self.connectionStartTime:
            self.connectionStopTime = datetime.now()

    @property
    def elapsedTime(self):
        if self.connectionStopTime:
            return self.connectionStopTime - self.connectionStartTime
        else:
            return datetime.now() - self.connectionStartTime if self.connectionStartTime else 'not started'


class Connection(object):
    """
    Main ldap connection class
    controls, if used, must be a list of tuples. Each tuple must have 3 elements,
    the control OID, a boolean meaning if the control is critical, a value
    If the boolean is set to True the server must honorate the control or refuse the operation
    Mixing controls must be defined in controls specification (as per rfc 4511)
    """

    def __init__(self, server, user = None, password = None, autoBind = False, restartable = False, version = 3, authentication = None, clientStrategy = STRATEGY_SYNC,
                 autoReferrals = True, saslMechanism = None, saslCredentials = None, collectUsage = False, readOnly = False):
        """
        Constructor
        """
        if clientStrategy not in CLIENT_STRATEGIES:
            self.lastError = 'unknown client connection strategy'
            raise LDAPException(self.lastError)

        self.strategyType = clientStrategy
        if self.strategyType == STRATEGY_SYNC:
            self.strategy = SyncWaitStrategy(self)
        elif self.strategyType == STRATEGY_ASYNC_THREADED:
            self.strategy = AsyncThreadedStrategy(self)
        elif self.strategyType == STRATEGY_LDIF_PRODUCER:
            self.strategy = LdifProducerStrategy(self)

        else:
            self.strategy = None

        self.user = user
        self.password = password
        if self.user and self.password and not authentication:
            self.authentication = AUTH_SIMPLE
        elif not authentication:
            self.authentication = AUTH_ANONYMOUS
        elif authentication in [AUTH_SIMPLE, AUTH_ANONYMOUS, AUTH_SASL]:
            self.authentication = authentication
        else:
            raise LDAPException('unknown authentication method')

        self.autoReferrals = True if autoReferrals else False

        # map strategy functions to connection functions
        self.send = self.strategy.send
        self.open = self.strategy.open
        self.getResponse = self.strategy.getResponse
        self.postSendSingleResponse = self.strategy.postSendSingleResponse
        self.postSendSearch = self.strategy.postSendSearch

        self.request = None
        self.response = None
        self.result = None
        self.lock = Lock()
        self.bound = False
        self.listening = False
        self.closed = True
        self.lastError = None
        self.autoBind = True if autoBind else False
        self.saslMechanism = saslMechanism
        self.saslCredentials = saslCredentials
        self.authorizationState = None
        self.usage = ConnectionUsage() if collectUsage else None
        self.socket = None
        self.tlsStarted = False
        self.saslInProgress = False
        self.readOnly = readOnly
        self.restartable = restartable
        self._contextState = []
        self._bindControls = None

        if not self.strategy.noRealDSA and server.isValid():
            self.server = server
            self.version = version
            if self.autoBind:
                self.open()
                self.bind()
                if not self.bound:
                    raise LDAPException('autoBind not successful')
        elif self.strategy.noRealDSA:
            self.server = None
            self.version = None
        else:
            self.lastError = 'invalid ldap server'
            raise LDAPException(self.lastError)

    def __str__(self):
        return (str(self.server) if self.server.isValid else 'None') + ' - ' + 'user: ' + str(self.user) + ' - version ' + str(self.version) + ' - ' + (
            'bound' if self.bound else 'unbound') + ' - ' + ('closed' if self.closed else 'open') + ' - ' + ('listening' if self.listening else 'not listening') + ' - ' + self.strategy.__class__.__name__

    def __repr__(self):
        r = 'Connection(server={0.server!r}'.format(self)
        r += '' if self.user is None else ', user={0.user!r}'.format(self)
        r += '' if self.password is None else ', password={0.password!r}'.format(self)
        r += '' if self.autoBind is None else ', autoBind={0.autoBind!r}'.format(self)
        r += '' if self.restartable is None else ', restartable={0.restartable!r}'.format(self)
        r += '' if self.version is None else ', version={0.version!r}'.format(self)
        r += '' if self.authentication is None else ', authentication={0.authentication!r}'.format(self)
        r += '' if self.strategyType is None else ', clientStrategy={0.strategyType!r}'.format(self)
        r += '' if self.autoReferrals is None else ', autoReferrals={0.autoReferrals!r}'.format(self)
        r += ')'

        return r

    def __enter__(self):
        self._contextState.append((self.bound, self.closed))  # save status out of context as a tuple in a list
        if self.closed:
            self.open()
        if not self.bound:
            self.bind()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        contextBound, contextClosed = self._contextState.pop()
        if not contextBound and self.bound:  # restore status prior to entering context
            self.unbind()

        if not contextClosed and self.closed:
            self.open()

        if not exc_type is None:
            return False  # reraise LDAPException

    def bind(self, forceBind = False, controls = None):
        """
        Bind to ldap with the user defined in Server object
        set forceBind to True to repeat bind (if you set different credentials in connection object)
        """
        self._bindControls = controls  # needed for restarting connection (if restartable)

        if not self.bound or forceBind:
            if self.authentication == AUTH_ANONYMOUS:
                request = bindOperation(self.version, self.authentication, '', '')
                response = self.postSendSingleResponse(self.send('bindRequest', request, controls))
            elif self.authentication == AUTH_SIMPLE:
                request = bindOperation(self.version, self.authentication, self.user, self.password)
                response = self.postSendSingleResponse(self.send('bindRequest', request, controls))
            elif self.authentication == AUTH_SASL:
                if self.saslMechanism in SASL_AVAILABLE_MECHANISMS:
                    response = self.doSaslBind(controls)
                else:
                    self.lastError = 'requested sasl mechanism not supported'
                    raise LDAPException(self.lastError)
            else:
                self.lastError = 'unknown authentication method'
                raise LDAPException(self.lastError)

            if isinstance(response, int):  # get response if async
                self.getResponse(response)

            if response is None:
                self.bound = False
            else:
                self.bound = True if self.result['result'] == RESULT_SUCCESS else False

            if self.bound:
                self.refreshDsaInfo()

        return self.bound

    def _rebind(self):
        try:
            self.close()
        except LDAPException:
            pass

        self.open()
        self.bind(forceBind = True, controls = self._controls)

    def unbind(self, controls = None):
        """
        Unbinds the connected user
        Unbind implies closing session as per rfc 4511 (4.3)
        """
        if not self.closed:
            request = unbindOperation()
            self.send('unbindRequest', request, controls)
            self.strategy.close()

        return True

    def close(self):
        """
        Alias for unbind operation
        """
        self.unbind()

    def search(self, searchBase, searchFilter, searchScope = SEARCH_SCOPE_WHOLE_SUBTREE, dereferenceAliases = SEARCH_DEREFERENCE_ALWAYS, attributes = None,
               sizeLimit = 0, timeLimit = 0, typesOnly = False, getOperationalAttributes = False, controls = None, pagedSize = None, pagedCriticality = False,
               pagedCookie = None):
        """
        Perform an ldap search
        if attributes is empty no attribute is returned
        if attributes is ALL_ATTRIBUTES all attributes are returned
        if pagedSize is an int greater than 0 a simple paged search is tried as described in rfc 2696 with the specified size
        if paged is 0 and cookie is present the search is abandoned on server
        cookie is an opaque string received in the last paged search and must be used on the next paged search response
        """
        if not attributes:
            attributes = [NO_ATTRIBUTES]
        elif attributes == ALL_ATTRIBUTES:
            attributes = ['*']

        if getOperationalAttributes:
            attributes.append(ALL_OPERATIONAL_ATTRIBUTES)

        if isinstance(pagedSize, int):
            realSearchControlValue = RealSearchControlValue()
            realSearchControlValue['size'] = Size(pagedSize)
            realSearchControlValue['cookie'] = Cookie(pagedCookie) if pagedCookie else Cookie('')
            if controls is None:
                controls = []
            controls.append(('1.2.840.113556.1.4.319', pagedCriticality if isinstance(pagedCriticality, bool) else False, encoder.encode(realSearchControlValue)))

        request = searchOperation(searchBase, searchFilter, searchScope, dereferenceAliases, attributes, sizeLimit, timeLimit, typesOnly)

        response = self.postSendSearch(self.send('searchRequest', request, controls))
        if isinstance(response, int):
            return response

        if self.result['type'] == 'searchResDone' and len(response) > 0:
            return True

        return False

    def compare(self, dn, attribute, value, controls = None):
        """
        Perform a compare operation
        """
        request = compareOperation(dn, attribute, value)
        response = self.postSendSingleResponse(self.send('compareRequest', request, controls))
        if isinstance(response, int):
            return response
        return True if self.result['type'] == 'compareResponse' and self.result['result'] == RESULT_COMPARE_TRUE else False

    def add(self, dn, objectClass, attributes = None, controls = None):
        """
        add dn to the dib, objectClass is None, a class name or a list of class names,
        attributes is a dictionary in the form 'attr': 'val'
        or 'attr': ['val1', 'val2', 'valN'] for multivalued types
        """
        attrObjectClass = []
        if objectClass is None:
            parmObjectClass = []
        else:
            parmObjectClass = objectClass if isinstance(objectClass, list) else [objectClass]

        if attributes:
            if 'objectClass' in attributes:
                attrObjectClass = attributes['objectClass'] if isinstance(attributes['objectClass'], list) else [attributes['objectClass']]
        else:
            attributes = dict()

        attributes['objectClass'] = list(set([objectClass.lower() for objectClass in parmObjectClass + attrObjectClass]))  # remove duplicate objectClass
        if not attributes['objectClass']:
            self.lastError = 'objectClass is mandatory'
            raise LDAPException(self.lastError)

        request = addOperation(dn, attributes)
        response = self.postSendSingleResponse(self.send('addRequest', request, controls))

        if isinstance(response, int) or isinstance(response, str):
            return response

        return True if self.result['type'] == 'addResponse' and self.result['result'] == RESULT_SUCCESS else False

    def delete(self, dn, controls = None):
        """
        Delete in the dib the entry identified by dn
        """
        if self.readOnly:
            raise LDAPException('Connetion is in read-only mode')

        request = deleteOperation(dn)
        response = self.postSendSingleResponse(self.send('delRequest', request, controls))

        if isinstance(response, int) or isinstance(response, str):
            return response

        return True if self.result['type'] == 'delResponse' and self.result['result'] == RESULT_SUCCESS else False

    def modify(self, dn, changes, controls = None):
        """
        Modify attributes of entry
        Changes is a dictionary in the form {'attribute1': [(operation, [val1, val2])], 'attribute2': [(operation, [val1, val2])]}
        Operation is 0 (MODIFY_ADD), 1 (MODIFY_DELETE), 2 (MODIFY_REPLACE), 3 (MODIFY_INCREMENT)
        """
        if self.readOnly:
            raise LDAPException('Connetion is in read-only mode')

        if not isinstance(changes, dict):
            self.lastError = 'changes must be a dictionary'
            raise LDAPException(self.lastError)

        for change in changes:
            if len(changes[change]) != 2:
                self.lastError = 'malformed change'
                raise LDAPException(self.lastError)
            elif changes[change][0] not in [MODIFY_ADD, MODIFY_DELETE, MODIFY_REPLACE, MODIFY_INCREMENT]:
                self.lastError = 'unknown change type'
                raise LDAPException(self.lastError)
        if not changes:
            self.lastError = 'no changes in modify request'
            raise LDAPException(self.lastError)

        request = modifyOperation(dn, changes)
        response = self.postSendSingleResponse(self.send('modifyRequest', request, controls))

        if isinstance(response, int) or isinstance(response, str):
            return response

        return True if self.result['type'] == 'modifyResponse' and self.result['result'] == RESULT_SUCCESS else False

    def modifyDn(self, dn, relativeDn, deleteOldDn = True, newSuperior = None, controls = None):
        """
        Modify dn of the entry and optionally performs a move of the entry in the dib
        """

        if self.readOnly:
            raise LDAPException('Connetion is in read-only mode')

        if newSuperior and not dn.startswith(relativeDn):  # as per rfc 4511 (4.9)
            raise LDAPException('dn cannot change while moving object')

        request = modifyDnOperation(dn, relativeDn, deleteOldDn, newSuperior)
        response = self.postSendSingleResponse(self.send('modDNRequest', request, controls))

        if isinstance(response, int) or isinstance(response, str):
            return response

        return True if self.result['type'] == 'modDNResponse' and self.result['result'] == RESULT_SUCCESS else False

    def abandon(self, messageId, controls = None):
        """
        Abandon the operation indicated by messageId
        """
        if messageId in self.strategy._outstanding and self.strategy._outstanding[messageId]['type'] not in ['abandonRequest', 'bindRequest', 'unbindRequest']:
            request = abandonOperation(messageId)
            self.send('abandonRequest', request, controls)
            self.response = None
            self.result = None
            return True

        return False

    def extended(self, requestName, requestValue = None, controls = None):
        """
        Perform an extended operation
        """
        request = extendedOperation(requestName, requestValue)
        response = self.postSendSingleResponse(self.send('extendedReq', request, controls))
        if isinstance(response, int):
            return response
        return True if self.result['type'] == 'extendedResp' and self.result['result'] == RESULT_SUCCESS else False

    def startTls(self):  # as per rfc 4511. Removal of TLS is defined as MAY in rfc 4511 so the client can't implement a generic StopTls method
        if self.server.tls:
            if self.server.tls.startTls(self):
                self.refreshDsaInfo()  # refresh server info as per rfc 4515 (3.1.5)
                return True

        return False

    def doSaslBind(self, controls):
        response = None
        if not self.saslInProgress:
            self.saslInProgress = True
            if self.saslMechanism == 'EXTERNAL':
                response = saslExternal(self, controls)
            elif self.saslMechanism == 'DIGEST-MD5':
                response = saslDigestMd5(self, controls)

            self.saslInProgress = False

        return response

    def refreshDsaInfo(self):
        if not self.closed:
            self.server.getInfoFromServer(self)

    def responseToLdif(self, searchResult = None, allBase64 = False):
        if searchResult is None:
            searchResult = self.response

        if isinstance(searchResult, list):
            searchResultToLdif = toLdif('searchResponse', searchResult, allBase64)
        else:
            searchResultToLdif = None

        return searchResultToLdif
