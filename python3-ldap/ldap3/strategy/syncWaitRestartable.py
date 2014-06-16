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
from sys import exc_info

from time import sleep

from .. import RESTARTABLE_SLEEPTIME, RESTARTABLE_TRIES
from ..core.exceptions import communication_exception_factory
from .syncWait import SyncWaitStrategy
from ..core.exceptions import LDAPSocketOpenError, LDAPSocketSendError, LDAPOperationResult, LDAPRestartableTriesReachedError


# noinspection PyBroadException
class SyncWaitRestartableStrategy(SyncWaitStrategy):
    def __init__(self, ldap_connection):
        SyncWaitStrategy.__init__(self, ldap_connection)
        self.sync = True
        self.no_real_dsa = False
        self.pooled = False
        self.can_stream = False
        self.restartable_sleep_time = RESTARTABLE_SLEEPTIME
        self.restartable_tries = RESTARTABLE_TRIES
        self._restarting = False
        self._last_bind_controls = None
        self._current_message_type = None
        self._current_request = None
        self._current_controls = None
        self._restart_tls = None
        self.exceptions_history = list()

    def open(self, reset_usage=False):
        SyncWaitStrategy.open(self, reset_usage)

    def _open_socket(self, use_ssl=False):
        """
        Try to open and connect a socket to a Server
        raise LDAPExceptionError if unable to open or connect socket
        if connection is restartable tries for the number of restarting requested or forever
        """
        try:
            print('try _open_socket, use_ssl=', use_ssl)
            return SyncWaitStrategy._open_socket(self, use_ssl)  # try to open socket using SyncWait
        except Exception:  # machinery for restartable connection
            print('except:', 1)
            self._add_exception_to_history()

        if not self._restarting:  # if not already performing a restart
            self._reset_exception_history()
            self._restarting = True

            counter = self.restartable_tries
            while counter > 0:
                print('counter: ', counter)
                sleep(self.restartable_sleep_time)
                if not self.connection.closed:
                    try:  # resetting connection
                        print('try close, use_ssl=', use_ssl)
                        self.connection.close()
                    except Exception:
                        print('except:', 2)
                        self._add_exception_to_history()

                try:  # reissuing same operation
                    print('trying operation, use_ssl=', use_ssl)
                    if self.connection.server_pool:
                        new_server = self.connection.server_pool.get_server(self.connection)  # get a server from the server_pool if available
                        if self.connection.server != new_server:
                            self.connection.server = new_server
                            if self.connection._usage:
                                self.connection._usage.servers_from_pool += 1
                    SyncWaitStrategy._open_socket(self, use_ssl)  # calls super (not restartable) _open_socket()
                    if self.connection._usage:
                        self.connection._usage.restartable_successes += 1
                    self.connection.closed = False
                    self._restarting = False
                    return
                except Exception:
                    print('except:', 3)
                    self._add_exception_to_history()
                    if self.connection._usage:
                        self.connection._usage.restartable_failures += 1
                if not isinstance(counter, bool):
                    counter -= 1
            self._restarting = False
        self.connection.last_error = 'restartable connection strategy failed while opening socket'
        print('raise', 1)
        raise LDAPRestartableTriesReachedError(self.connection.last_error)

    def send(self, message_type, request, controls=None):
        print('entering send', message_type, request)
        self._current_message_type = message_type
        self._current_request = request
        self._current_controls = controls
        if not self._restart_tls:  # RFCs doesn't define how to stop tls once started
            self._restart_tls = self.connection.tls_started
        if message_type == 'bindRequest':  # store controls used in bind to be used again when restarting the connection
            self._last_bind_controls = controls

        try:
            print('try send, message_type=', message_type)
            return SyncWaitStrategy.send(self, message_type, request, controls)  # try to send using SyncWait
        except Exception:
            print('except:', 4)
            self._add_exception_to_history()
        if not self._restarting:  # machinery for restartable connection
            self._reset_exception_history()
            self._restarting = True
            counter = self.restartable_tries
            while counter > 0:
                print('counter:', counter)
                sleep(self.restartable_sleep_time)
                if not self.connection.closed:
                    try:  # resetting connection
                        print('try close, message_type=', message_type)
                        self.connection.close()
                    except Exception:
                        print('except:', 5)
                        self._add_exception_to_history()
                failure = False
                try:  # reopening connection
                    print('try reopen, message_type=', message_type)
                    self.connection.open(reset_usage=False)
                    print('check restart_tls', self._restart_tls)
                    if self._restart_tls:  # restart tls if start_tls was previously used
                        print('try restart_tls, message_type=', message_type)
                        self.connection.start_tls()
                    if message_type != 'bindRequest':
                        print('try rebind, message_type=', message_type)
                        self.connection.bind(self._last_bind_controls)  # binds with previously used controls unless the request is already a bindRequest
                except Exception:
                    print('except:', 6)
                    self._add_exception_to_history()
                    failure = True

                if not failure:
                    try:  # reissuing same operation
                        print('try resend, message_type=', message_type)
                        ret_value = self.connection.send(message_type, request, controls)
                        if self.connection._usage:
                            self.connection._usage.restartable_successes += 1
                        self._restarting = False

                        return ret_value  # successful send
                    except Exception:
                        print('except:', 7)
                        self._add_exception_to_history()
                        failure = True

                if failure and self.connection._usage:
                    self.connection._usage.restartable_failures += 1

                if not isinstance(counter, bool):
                    counter -= 1

            self._restarting = False

        self.connection.last_error = 'restartable connection failed to send'
        print('raise', 2)
        raise LDAPRestartableTriesReachedError(self.connection.last_error)

    def post_send_single_response(self, message_id):
        try:
            print('try post_send_single_response, message_id=', message_id)
            return SyncWaitStrategy.post_send_single_response(self, message_id)
        except Exception:
            print('except:', 8)
            self._add_exception_to_history()

        # if an LDAPExceptionError is raised then resend the request
        exc = None
        try:
            print('try repost_send_single_response, message_id=', message_id)
            return SyncWaitStrategy.post_send_single_response(self, self.send(self._current_message_type, self._current_request, self._current_controls))
        except Exception as e:
            print('except:', 9)
            self._add_exception_to_history()
            exc = e

        if exc:
            if isinstance(exc, LDAPOperationResult):
                print('raise', 3)
                raise exc
            else:
                self.connection.last_error = 'restartable connection strategy failed in post_send_single_response'
                print('raise', 4)
                raise communication_exception_factory(LDAPSocketSendError, exc)(self.connection.last_error)

    def post_send_search(self, message_id):
        try:
            print('try post_send_search, message_id=', message_id)
            return SyncWaitStrategy.post_send_search(self, message_id)
        except Exception:
            print('except:', 10)
            self._add_exception_to_history()

        exc = None
        # if an LDAPExceptionError is raised then resend the request
        try:
            print('try repost_send_single_response, message_id=', message_id)
            return SyncWaitStrategy.post_send_search(self, self.connection.send(self._current_message_type, self._current_request, self._current_controls))
        except Exception as e:
            print('except:', 11)
            self._add_exception_to_history()
            exc = e

        if exc:
            if isinstance(exc, LDAPOperationResult):
                print('raise', 5)
                raise exc
            else:
                #self.connection.last_error = 'restartable connection strategy failed in post_send_search'
                self.connection.last_error = exc.args
                print('raise', 6)
                # raise communication_exception_factory(LDAPSocketSendError, exc)(self.connection.last_error)
                raise exc

    def _add_exception_to_history(self):
        if exc_info() == (None, None, None):
            return

        self.exceptions_history.append(exc_info()[:2])

    def _reset_exception_history(self):
        """
        resets the exception list keepeing the last one
        """
        if self.exceptions_history:
            self.exceptions_history = self.exceptions_history[:-1]
