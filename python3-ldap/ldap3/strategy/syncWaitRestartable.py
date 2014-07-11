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
import socket
from datetime import datetime

from .. import RESTARTABLE_SLEEPTIME, RESTARTABLE_TRIES
from .syncWait import SyncWaitStrategy
from ..core.exceptions import LDAPSocketOpenError, LDAPOperationResult, LDAPMaximumRetriesError


# noinspection PyBroadException,PyProtectedMember
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
        self.exception_history = []

    def open(self, reset_usage=False):
        SyncWaitStrategy.open(self, reset_usage)

    def _open_socket(self, use_ssl=False):
        """
        Try to open and connect a socket to a Server
        raise LDAPExceptionError if unable to open or connect socket
        if connection is restartable tries for the number of restarting requested or forever
        """
        try:
            SyncWaitStrategy._open_socket(self, use_ssl)  # try to open socket using SyncWait
            self._reset_exception_history()
            return
        except Exception:  # machinery for restartable connection
            self._add_exception_to_history()

        if not self._restarting:  # if not already performing a restart
            self._restarting = True
            counter = self.restartable_tries
            while counter > 0:
                sleep(self.restartable_sleep_time)
                if not self.connection.closed:
                    try:  # resetting connection
                        self.connection.close()
                    except (socket.error, LDAPSocketOpenError):  # don't trace catch socket errors because socket could already be closed
                        pass
                    except Exception:
                        self._add_exception_to_history()
                try:  # reissuing same operation
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
                    self._reset_exception_history()
                    return
                except Exception:
                    self._add_exception_to_history()
                    if self.connection._usage:
                        self.connection._usage.restartable_failures += 1
                if not isinstance(self.restartable_tries, bool):
                    counter -= 1
            self._restarting = False
            self.connection.last_error = 'restartable connection strategy failed while opening socket'
            raise LDAPMaximumRetriesError(self.connection.last_error, self.exception_history, self.restartable_tries)

    def send(self, message_type, request, controls=None):
        self._current_message_type = message_type
        self._current_request = request
        self._current_controls = controls
        if not self._restart_tls:  # RFCs doesn't define how to stop tls once started
            self._restart_tls = self.connection.tls_started
        if message_type == 'bindRequest':  # store controls used in bind to be used again when restarting the connection
            self._last_bind_controls = controls

        try:
            message_id = SyncWaitStrategy.send(self, message_type, request, controls)  # try to send using SyncWait
            self._reset_exception_history()
            return message_id
        except Exception:
            self._add_exception_to_history()
        if not self._restarting:  # machinery for restartable connection
            self._restarting = True
            counter = self.restartable_tries
            while counter > 0:
                sleep(self.restartable_sleep_time)
                if not self.connection.closed:
                    try:  # resetting connection
                        self.connection.close()
                    except (socket.error, LDAPSocketOpenError):  # don't trace socket errrors because socket could already be closed
                        pass
                    except Exception:
                        self._add_exception_to_history()
                failure = False
                try:  # reopening connection
                    self.connection.open(reset_usage=False)
                    if self._restart_tls:  # restart tls if start_tls was previously used
                        self.connection.start_tls()
                    if message_type != 'bindRequest':
                        self.connection.bind(self._last_bind_controls)  # binds with previously used controls unless the request is already a bindRequest
                except Exception:
                    self._add_exception_to_history()
                    failure = True

                if not failure:
                    try:  # reissuing same operation
                        ret_value = self.connection.send(message_type, request, controls)
                        if self.connection._usage:
                            self.connection._usage.restartable_successes += 1
                        self._restarting = False
                        self._reset_exception_history()
                        return ret_value  # successful send
                    except Exception:
                        self._add_exception_to_history()
                        failure = True

                if failure and self.connection._usage:
                    self.connection._usage.restartable_failures += 1

                if not isinstance(self.restartable_tries, bool):
                    counter -= 1

            self._restarting = False

        self.connection.last_error = 'restartable connection failed to send'
        print('b')
        raise LDAPMaximumRetriesError(self.connection.last_error, self.exception_history, self.restartable_tries)

    def post_send_single_response(self, message_id):
        try:
            ret_value = SyncWaitStrategy.post_send_single_response(self, message_id)
            self._reset_exception_history()
            return ret_value
        except Exception:
            self._add_exception_to_history()

        # if an LDAPExceptionError is raised then resend the request
        try:
            ret_value = SyncWaitStrategy.post_send_single_response(self, self.send(self._current_message_type, self._current_request, self._current_controls))
            self._reset_exception_history()
            return ret_value
        except Exception as e:
            self._add_exception_to_history()
            exc = e

        if exc:
            if not isinstance(exc, LDAPOperationResult):
                self.connection.last_error = 'restartable connection strategy failed in post_send_single_response'
            raise exc

    def post_send_search(self, message_id):
        try:
            ret_value = SyncWaitStrategy.post_send_search(self, message_id)
            self._reset_exception_history()
            return ret_value
        except Exception:
            self._add_exception_to_history()

        # if an LDAPExceptionError is raised then resend the request
        try:
            ret_value = SyncWaitStrategy.post_send_search(self, self.connection.send(self._current_message_type, self._current_request, self._current_controls))
            self._reset_exception_history()
            return ret_value
        except Exception as e:
            self._add_exception_to_history()
            exc = e

        if exc:
            if not isinstance(exc, LDAPOperationResult):
                self.connection.last_error = exc.args
            raise exc

    def _add_exception_to_history(self):
        if not isinstance(self.restartable_tries, bool):  # doesn't accumulate when restarting forever
            if not isinstance(exc_info()[1], LDAPMaximumRetriesError):  # doesn't add the LDAPMaximumRetriesError exception
                self.exception_history.append((datetime.now(), exc_info()[0], exc_info()[1]))

    def _reset_exception_history(self):
        if self.exception_history:
            self.exception_history = []
