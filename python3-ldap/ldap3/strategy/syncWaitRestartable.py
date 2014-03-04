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

    def _openSocket(self, useSsl=False):
        """
        Try to open and connect a socket to a Server
        raise LDAPException if unable to open or connect socket
        if connection is restartable tries for the number of restarting requested or forever
        """

        try:
            return SyncWaitStrategy._openSocket(self, useSsl)  # try to open socket using SyncWait
        except LDAPException as e:  # machinery for restartable connection
            if not self._restarting:  # if not already performing a restart
                e = None
                self._restarting = True
                counter = self.restartableTries
                while counter > 0:
                    print('sleeping for ', self.restartableSleepTime, 'seconds...')
                    sleep(self.restartableSleepTime)

                    try:  # resetting connection
                        print('try close socket')
                        self.connection.close()
                    except LDAPException as e:
                        print('close exception', e)

                    try:  # reissuing same operation
                        print('try _openSocket')
                        SyncWaitStrategy._openSocket(self, useSsl)  # calls super (not restartable) _openSocket()
                        if self.connection.usage:
                            self.connection.usage.restartableSuccesses += 1
                        self.connection.closed = False
                        self._restarting = False
                        return
                    except LDAPException as e:
                        print('_openSocket exception', e)
                        if self.connection.usage:
                            self.connection.usage.restartableFailures += 1
                    if not isinstance(counter, bool):
                        counter -= 1

                self._restarting = False
                raise e if e else LDAPException('restartable connection strategy failed')

    def send(self, messageType, request, controls=None):
        try:
            return SyncWaitStrategy.send(self, messageType, request, controls)  # try to send using SyncWait
        except LDAPException as e:  # machinery for restartable connection
            if not self._restarting:  # if not already performing a restart
                e = None
                self._restarting = True
                counter = self.restartableTries
                while counter > 0:
                    print('sleeping for ', self.restartableSleepTime, 'seconds...')
                    sleep(self.restartableSleepTime)

                    try:  # resetting connection
                        print('try close/open connection')
                        self.close()
                        SyncWaitStrategy.open(self)  # calls super (not restartable) open()
                        if self.connection.request.type != 'bindRequest':
                            self.bind(True, self.connection._bindControls)  # forces bind with previously used controls unless the request is already a bindRequest
                    except LDAPException as e:
                        print('close/open/bind exception', e)

                    try:  # reissuing same operation
                        print('try:', counter)
                        ret_value = self.send(messageType, request, controls)
                        if self.connection.usage:
                            self.connection.usage.restartableSuccesses += 1
                        self._restarting = False
                        return ret_value  # successful send
                    except LDAPException as e:
                        if self.connection.usage:
                            self.connection.usage.restartableFailures += 1
                    if not isinstance(counter, bool):
                        counter -= 1

                self._restarting = False
                raise e if e else LDAPException('restartable connection strategy failed')

    def postSendSingleResponse(self, messageId):
        try:
            return SyncWaitStrategy.postSendSingleResponse(self, messageId)
        except LDAPException as e:
            print('postSendSingleResponse exception', e)

        return []

    def postSendSearch(self, messageId):
        """
        To be executed after a search request
        Returns the result message and store in connection.response the objects found
        """
        try:
            return SyncWaitStrategy.postSendSearch(self, messageId)
        except LDAPException as e:
            print('postSendSearch exception', e)

        return {'type': 'failed'}
