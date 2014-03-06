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
from time import sleep
from pyasn1.codec.ber import encoder
from ldap3 import LDAPException, RESTARTABLE_SLEEPTIME, RESTARTABLE_TRIES
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
        self.restartableSleepTime = RESTARTABLE_SLEEPTIME
        self.restartableTries = RESTARTABLE_TRIES
        self._restarting = False
        self._lastBindControls = None
        self._currentMessageType = None
        self._currentRequest = None
        self._currentControls = None

    def open(self, startListening=True, resetUsage=False):
        SyncWaitStrategy.open(self, startListening, resetUsage)

    def _openSocket(self, useSsl=False):
        """
        Try to open and connect a socket to a Server
        raise LDAPException if unable to open or connect socket
        if connection is restartable tries for the number of restarting requested or forever
        """

        try:
            return SyncWaitStrategy._openSocket(self, useSsl)  # try to open socket using SyncWait
        except LDAPException:  # machinery for restartable connection
            pass

        if not self._restarting:  # if not already performing a restart
            self._restarting = True
            counter = self.restartableTries
            while counter > 0:
                sleep(self.restartableSleepTime)

                if not self.connection.closed:
                    try:  # resetting connection
                        self.connection.close()
                    except LDAPException:
                        pass

                try:  # reissuing same operation
                    SyncWaitStrategy._openSocket(self, useSsl)  # calls super (not restartable) _openSocket()
                    if self.connection.usage:
                        self.connection.usage.restartableSuccesses += 1
                    self.connection.closed = False
                    self._restarting = False
                    return
                except LDAPException:
                    if self.connection.usage:
                        self.connection.usage.restartableFailures += 1
                if not isinstance(counter, bool):
                    counter -= 1
            self._restarting = False

        raise LDAPException('restartable connection strategy failed in _openSocket')

    def send(self, messageType, request, controls=None):
        self._currentMessageType = messageType
        self._currentRequest = request
        self._currentControls = controls
        if messageType == 'bindRequest':  # store controls used in bind to be used again when restarting the connection
            self._lastBindControls = controls

        try:
            return SyncWaitStrategy.send(self, messageType, request, controls)  # try to send using SyncWait
        except LDAPException as e:
            pass

        if not self._restarting:  # machinery for restartable connection
            self._restarting = True
            counter = self.restartableTries
            while counter > 0:
                sleep(self.restartableSleepTime)
                failure = False
                try:  # resetting connection
                    self.connection.close()
                    self.connection.open(resetUsage = False)
                    if messageType != 'bindRequest':
                        self.connection.bind(self._lastBindControls)  # binds with previously used controls unless the request is already a bindRequest
                except LDAPException as e:
                    failure = True

                if not failure:
                    try:  # reissuing same operation
                        ret_value = self.connection.send(messageType, request, controls)
                        if self.connection.usage:
                            self.connection.usage.restartableSuccesses += 1
                        self._restarting = False
                        return ret_value  # successful send
                    except LDAPException as e:
                        failure = True

                if failure and self.connection.usage:
                    self.connection.usage.restartableFailures += 1

                if not isinstance(counter, bool):
                    counter -= 1

            self._restarting = False
        raise LDAPException('restartable connection strategy failed in send')

    def postSendSingleResponse(self, messageId):
        try:
            return SyncWaitStrategy.postSendSingleResponse(self, messageId)
        except LDAPException:
            pass

        try:
            return SyncWaitStrategy.postSendSingleResponse(self, self.send(self._currentMessageType, self._currentRequest, self._currentControls))
        except LDAPException:
            pass

        raise LDAPException('restartable connection strategy failed in postSendSingleResponse')

    def postSendSearch(self, messageId):
        try:
            return SyncWaitStrategy.postSendSearch(self, messageId)
        except LDAPException:
            pass

        try:
            return SyncWaitStrategy.postSendSearch(self, self.connection.send(self._currentMessageType, self._currentRequest, self._currentControls))
        except LDAPException:
            pass

        raise LDAPException('restartable connection strategy failed in postSendSearch')
