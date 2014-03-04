"""
Created on 2014.03.04

@author: Giovanni Cannata

Copyright 2014 Giovanni Cannata

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
from socket import socket
from pyasn1.codec.ber import encoder
from ldap3 import LDAPException, RESTARTABLE_SLEEPTIME
from ..protocol.convert import buildControlsList
from ..protocol.rfc4511 import MessageID, ProtocolOp
from .baseStrategy import BaseStrategy
from .syncWait import SyncWaitStrategy


class SyncWaitRestartableStrategy(SyncWaitStrategy):
    def __init__(self, ldapConnection):
        SyncWaitStrategy.__init__(self, ldapConnection)
        self.sync = True
        self.noRealDSA = False
        self.restartable = True

    def _openSocketNew(self, useSsl=False):
        """
        Try to open and connect a socket to a Server
        raise LDAPException if unable to open or connect socket
        if connection is restartable tries for the number of restarting requested or forever
        """
        if self.connection._restartableTries == 0:
            self.connection._restartableTries = self.connection.restartable

        restarted = False
        restart = True
        while restart:
            localException = None
            print('openSocket, restartable tries:', self.connection._restartableTries)
            try:
                self.connection.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            except Exception as e:
                self.connection.lastError = 'socket creation error: ' + str(e)
                localException = e
            try:
                self.connection.socket.connect((self.connection.server.host, self.connection.server.port))
            except socket.error as e:
                self.connection.lastError = 'socket connection error: ' + str(e)
                localException = e

            if useSsl:
                try:
                    self.connection.socket = self.connection.server.tls.wrapSocket(self.connection.socket, doHandshake=True)
                except Exception as e:
                    self.connection.lastError = 'socket ssl wrapping error: ' + str(e)
                    localException = e

            restart = False
            if localException:
                if isinstance(self.connection._restartableTries, int):
                    self.connection._restartableTries -= 1

                if self.connection._restartableTries > 0:  # wait for retrying connection, always for True
                    self.connection._restart()
                    restart = True
                    restarted = True

        if localException:
            raise localException
        elif restarted:  # successful restarted
            self.connection._restarted()

        self.connection.closed = False


def _restartableSend(self, messageType, request, controls=None):
    try:
        return self.send(messageType, request, controls)  # try to send as usual
    except LDAPException as e:  # machinery for restartable connection
        if self.connection.restartable:
            counter = self.connection.restartable
            while counter > 0:
                print('sleep...')
                sleep(RESTARTABLE_SLEEPTIME)  # defined in __init__.py

                try:
                    print('try close/open connection')
                    self.close()
                    self.open()
                    if self.connection.request.type != 'bindRequest':
                        self.bind(True, self.connection._bindControls)  # force bind with previously used controls unless the request is already a bindRequest
                except Exception as e:
                    print('close/open/bind exception', e)

                try:
                    print('try:', counter)
                    ret_value = self.send(messageType, request, controls)
                    if self.connection.usage:
                        self.connection.usage.restartableSuccesses += 1
                    return ret_value  # successful send
                except LDAPException as e:
                    if self.connection.usage:
                        self.connection.usage.restartableFailures += 1

                if not isinstance(counter, bool):
                    counter -= 1

    raise e  # re-raise same exception


def sendNew(self, messageType, request, controls=None):
    """
    Send an LDAP message
    Returns the messageId
    """
    if self.connection._restartableTries == 0:
        self.connection._restartableTries = self.connection.restartable

    restart = True
    while restart:
        print('enter send loop')
        localException = None
        self.connection.request = None
        if self.connection.listening:
            if self.connection.saslInProgress and messageType not in ['bindRequest']:  # as per rfc 4511 (4.2.1)
                self.connection.lastError = 'cannot send operation requests while SASL bind is in progress'
                raise LDAPException(self.connection.lastError)
            messageId = self.connection.server.nextMessageId()
            ldapMessage = ldapMessage()
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
                localException = e

            self.connection.request = BaseStrategy.decodeRequest(ldapMessage)
            self.connection.request['controls'] = controls
            self._outstanding[messageId] = self.connection.request
            if self.connection.usage:
                self.connection.usage.transmittedMessage(self.connection.request, len(encodedMessage))
        else:
            self.connection.lastError = 'unable to send message, socket is not open'
            localException = LDAPException(self.connection.lastError)

        restart = False
        if localException:
            if isinstance(self.connection._restartableTries, int):
                self.connection._restartableTries -= 1

            print(localException)
            if self.connection._restartableTries > 0:  # wait for retrying connection, always for True
                self.connection._restart(request)
                restart = True
        print(restart)

    if localException:
        raise localException

    return messageId

