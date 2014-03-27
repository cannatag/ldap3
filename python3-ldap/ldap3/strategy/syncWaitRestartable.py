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

from time import sleep

from ldap3 import LDAPException, RESTARTABLE_SLEEPTIME, RESTARTABLE_TRIES
from .syncWait import SyncWaitStrategy


class SyncWaitRestartableStrategy(SyncWaitStrategy):
    def __init__(self, ldap_connection):
        SyncWaitStrategy.__init__(self, ldap_connection)
        self.sync = True
        self.no_real_dsa = False
        self.restartable_sleep_time = RESTARTABLE_SLEEPTIME
        self.restartable_tries = RESTARTABLE_TRIES
        self._restarting = False
        print('A', self._restarting)
        self._last_bind_controls = None
        self._current_message_type = None
        self._current_request = None
        self._current_controls = None
        self._restart_tls = None

    def open(self, reset_usage=False):
        SyncWaitStrategy.open(self, reset_usage)

    def _open_socket(self, use_ssl=False):
        """
        Try to open and connect a socket to a Server
        raise LDAPException if unable to open or connect socket
        if connection is restartable tries for the number of restarting requested or forever
        """
        print('_open_socket in Restartable')
        try:
            print(50)
            return SyncWaitStrategy._open_socket(self, use_ssl)  # try to open socket using SyncWait
        except Exception:  # machinery for restartable connection
            print(51)
            pass

        if not self._restarting:  # if not already performing a restart
            print(52)
            self._restarting = True
            print('B', self._restarting)

            counter = self.restartable_tries
            while counter > 0:
                sleep(self.restartable_sleep_time)
                print('_open_socket in Restartable again')
                if not self.connection.closed:
                    try:  # resetting connection
                        print(54)
                        self.connection.close()
                    except Exception:
                        print(55)
                        pass

                try:  # reissuing same operation
                    print(56)
                    if self.connection.server_pool:
                        print(57)
                        new_server = self.connection.server_pool.get_server(self.connection)  # get a server from the server_pool if available
                        if self.connection.server != new_server:
                            print(58)
                            self.connection.server = new_server
                            if self.connection.usage:
                                self.connection.usage.servers_from_pool += 1
                    print(59)
                    SyncWaitStrategy._open_socket(self, use_ssl)  # calls super (not restartable) _open_socket()
                    if self.connection.usage:
                        self.connection.usage.restartable_successes += 1
                    print(60)
                    self.connection.closed = False
                    self._restarting = False
                    print('C', self._restarting)
                    print(self.connection.server)
                    print('lazy', self.connection.lazy)
                    return
                except Exception:
                    print(61)
                    if self.connection.usage:
                        self.connection.usage.restartable_failures += 1
                if not isinstance(counter, bool):
                    print(62)
                    counter -= 1
            self._restarting = False
            print('D', self._restarting)
        print(63)
        raise LDAPException('restartable connection strategy failed in _open_socket')

    def send(self, message_type, request, controls=None):
        self._current_message_type = message_type
        self._current_request = request
        self._current_controls = controls
        self._restart_tls = self.connection.tls_started
        if message_type == 'bindRequest':  # store controls used in bind to be used again when restarting the connection
            self._last_bind_controls = controls

        try:
            print(1)
            print(self._restarting)
            return SyncWaitStrategy.send(self, message_type, request, controls)  # try to send using SyncWait
        except Exception as e:
            print(e)
            print(2)
            pass
        print('_restarting', self._restarting)
        if not self._restarting:  # machinery for restartable connection
            print(3)
            self._restarting = True
            print('E', self._restarting)
            counter = self.restartable_tries
            while counter > 0:
                sleep(self.restartable_sleep_time)
                print(4)
                if not self.connection.closed:
                    try:  # resetting connection
                        print(5)
                        self.connection.close()
                    except Exception:
                        print(6)
                        pass
                failure = False
                try:  # reopening connection
                    print(7)
                    self.connection.open(reset_usage=False)
                    print(8)
                    if self._restart_tls:  # restart tls if start_tls was previously used
                        print(9)
                        self.connection.start_tls()
                    if message_type != 'bindRequest':
                        print(10)
                        self.connection.bind(self._last_bind_controls)  # binds with previously used controls unless the request is already a bindRequest
                except Exception:
                    print(11)
                    failure = True

                if not failure:
                    print(12)
                    try:  # reissuing same operation
                        print('sending. Lazy:', self.connection.lazy )

                        ret_value = self.connection.send(message_type, request, controls)
                        if self.connection.usage:
                            self.connection.usage.restartable_successes += 1
                        self._restarting = False
                        print('F', self._restarting)

                        print(13)
                        return ret_value  # successful send
                    except Exception:
                        print(14)
                        failure = True

                if failure and self.connection.usage:
                    self.connection.usage.restartable_failures += 1

                if not isinstance(counter, bool):
                    print(15)
                    counter -= 1

            self._restarting = False
            print('G', self._restarting)

            print(16)
        print(17)
        raise LDAPException('restartable connection strategy failed in send')

    def post_send_single_response(self, message_id):
        try:
            return SyncWaitStrategy.post_send_single_response(self, message_id)
        except Exception:
            pass

        # if an LDAPException is raised then resend the request
        try:
            return SyncWaitStrategy.post_send_single_response(self, self.send(self._current_message_type, self._current_request, self._current_controls))
        except Exception:
            pass

        raise LDAPException('restartable connection strategy failed in post_send_single_response')

    def post_send_search(self, message_id):
        try:
            return SyncWaitStrategy.post_send_search(self, message_id)
        except Exception:
            pass

        # if an LDAPException is raised then resend the request
        try:
            return SyncWaitStrategy.post_send_search(self, self.connection.send(self._current_message_type, self._current_request, self._current_controls))
        except Exception:
            pass

        raise LDAPException('restartable connection strategy failed in post_send_search')
