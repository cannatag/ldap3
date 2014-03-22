"""
Created on 2013.07.15

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

from threading import Thread, Lock
from time import sleep

from pyasn1.codec.ber import decoder

from ldap3 import RESPONSE_COMPLETE, SOCKET_SIZE, RESULT_REFERRAL, LDAPException, RESTARTABLE_SLEEPTIME, RESTARTABLE_TRIES
from ..strategy.baseStrategy import BaseStrategy
from ..strategy.asyncThreaded import AsyncThreadedStrategy
from ..protocol.rfc4511 import LDAPMessage


class AsyncThreadedStrategyRestartable(AsyncThreadedStrategy):
    """
    Restartable Async Threaded Strategy
    """

    def __init__(self, ldap_connection):
        AsyncThreadedStrategy.__init__(self, ldap_connection)
        self.sync = False
        self.no_real_dsa = False
        self.restartable = True
        self.restartable_sleep_time = RESTARTABLE_SLEEPTIME
        self.restartable_tries = RESTARTABLE_TRIES
        self._restarting = False
        self._last_bind_controls = None
        self._restart_tls = None
        self._responses = None
        self.receiver = None
        self.lock = Lock()
        self.

    def open(self, start_listening=True, reset_usage=False):
        AsyncThreadedStrategy.open(self, start_listening, reset_usage)

    def _open_socket(self, use_ssl=False):
        """
        Try to open and connect a socket to a Server
        raise LDAPException if unable to open or connect socket
        if connection is restartable tries for the number of restarting requested or forever
        """

        try:
            return AsyncThreadedStrategy._open_socket(self, use_ssl)  # try to open socket using SyncWait
        except LDAPException:  # machinery for restartable connection
            pass

        if not self._restarting:  # if not already performing a restart
            self._restarting = True
            counter = self.restartable_tries
            while counter > 0:
                sleep(self.restartable_sleep_time)

                if not self.connection.closed:
                    try:  # resetting connection
                        self.connection.close()
                    except LDAPException:
                        pass

                try:  # reissuing same operation
                    if self.connection.server_pool:
                        new_server = self.connection.server_pool.get_server(self.connection)  # get a server from the server_pool if available
                        if self.connection.server != new_server:
                            self.connection.server = new_server
                            if self.connection.usage:
                                self.connection.usage.servers_from_pool += 1
                    AsyncThreadedStrategy._open_socket(self, use_ssl)  # calls super (not restartable) _open_socket()
                    if self.connection.usage:
                        self.connection.usage.restartable_successes += 1
                    self.connection.closed = False
                    self._restarting = False
                    return
                except LDAPException:
                    if self.connection.usage:
                        self.connection.usage.restartable_failures += 1
                if not isinstance(counter, bool):
                    counter -= 1
            self._restarting = False

        raise LDAPException('restartable connection strategy failed in _open_socket')

    def close(self):
        """
        Close connection and stop socket thread
        """
        with self.lock:
            AsyncThreadedStrategy.close(self)

    def _start_listen(self):
        """
        Start thread in daemon mode
        """
        if not self.connection.listening:
            self.receiver = ReceiverSocketThread(self.connection)
            self.connection.listening = True
            self.receiver.daemon = True
            self.receiver.start()

    def send(self, message_type, request, controls=None):
        self._current_message_type = message_type
        self._current_request = request
        self._current_controls = controls
        self._restart_tls = self.connection.tls_started
        if message_type == 'bindRequest':  # store controls used in bind to be used again when restarting the connection
            self._last_bind_controls = controls

        try:
            return SyncWaitStrategy.send(self, message_type, request, controls)  # try to send using SyncWait
        except LDAPException:
            pass

        if not self._restarting:  # machinery for restartable connection
            self._restarting = True
            counter = self.restartable_tries
            while counter > 0:
                sleep(self.restartable_sleep_time)
                if not self.connection.closed:
                    try:  # resetting connection
                        self.connection.close()
                    except LDAPException:
                        pass
                failure = False
                try:  # reopening connection
                    self.connection.open(reset_usage=False)
                    if self._restart_tls:  # restart tls if start_tls was previously used
                        self.connection.start_tls()
                    if message_type != 'bindRequest':
                        self.connection.bind(self._last_bind_controls)  # binds with previously used controls unless the request is already a bindRequest
                except LDAPException:
                    failure = True

                if not failure:
                    try:  # reissuing same operation
                        ret_value = self.connection.send(message_type, request, controls)
                        if self.connection.usage:
                            self.connection.usage.restartable_successes += 1
                        self._restarting = False
                        return ret_value  # successful send
                    except LDAPException:
                        failure = True

                if failure and self.connection.usage:
                    self.connection.usage.restartable_failures += 1

                if not isinstance(counter, bool):
                    counter -= 1

            self._restarting = False
        raise LDAPException('restartable connection strategy failed in send')

    def _get_response(self, message_id):
        """
        Performs the capture of LDAP response for this strategy
        Checks lock to avoid race condition with receiver thread
        """
        with self.lock:
            responses = self._responses.pop(message_id) if message_id in self._responses and self._responses[message_id][-1] == RESPONSE_COMPLETE else None

        if responses is not None and responses[-2]['result'] == RESULT_REFERRAL and self.connection.auto_referrals:
            ref_response, ref_result = self.do_operation_on_referral(self._outstanding[message_id], responses[-2]['referrals'])
            if ref_response is not None:
                responses = ref_response + [ref_result]
                responses.append(RESPONSE_COMPLETE)
            elif ref_result is not None:
                responses = [ref_result, RESPONSE_COMPLETE]

            self._referrals = []

        return responses


class ReceiverSocketThread(Thread):
    """
    The thread that actually manage the receiver socket
    """

    def __init__(self, ldap_connection):
        Thread.__init__(self)
        self.connection = ldap_connection

    def run(self):
        """
        Wait for data on socket, compute the length of the message and wait for enough bytes to decode the message
        Message are appended to strategy._responses
        """
        unprocessed = b''
        get_more_data = True
        listen = True
        data = b''
        closed_from_server = False

        while listen:
            if get_more_data:
                try:
                    data = self.connection.socket.recv(SOCKET_SIZE)
                except OSError:
                    listen = False
                if len(data) > 0:
                    unprocessed += data
                    data = b''
                else:
                    listen = False
            length = BaseStrategy.compute_ldap_message_size(unprocessed)
            if length == -1 or len(unprocessed) < length:
                get_more_data = True
            elif len(unprocessed) >= length:  # add message to message list
                if self.connection.usage:
                    self.connection.usage.received_message(length)
                ldap_resp = decoder.decode(unprocessed[:length], asn1Spec=LDAPMessage())[0]
                message_id = int(ldap_resp['messageID'])
                dict_response = BaseStrategy.decode_response(ldap_resp)
                if dict_response['type'] == 'extendedResp' and dict_response['responseName'] == '1.3.6.1.4.1.1466.20037':
                    if dict_response['result'] == 0:  # StartTls in progress
                        if self.connection.server.tls:
                            self.connection.server.tls._start_tls(self.connection)
                        else:
                            self.connection.last_error = 'no Tls object defined in server'
                            raise LDAPException(self.connection.last_error)
                    else:
                        self.connection.last_error = 'Asynchronous StartTls failed'
                        raise LDAPException(self.connection.last_error)
                if message_id != 0:  # 0 is reserved for 'Unsolicited Notification' from server as per RFC4511 (paragraph 4.4)
                    with self.connection.strategy.lock:
                        if message_id in self.connection.strategy._responses:
                            self.connection.strategy._responses[message_id].append(dict_response)
                        else:
                            self.connection.strategy._responses[message_id] = [dict_response]
                        if dict_response['type'] not in ['searchResEntry', 'searchResRef', 'intermediateResponse']:
                            self.connection.strategy._responses[message_id].append(RESPONSE_COMPLETE)

                    unprocessed = unprocessed[length:]
                    get_more_data = False if unprocessed else True
                    listen = True if self.connection.listening or unprocessed else False
                else:  # Unsolicited Notification
                    if dict_response['responseName'] == '1.3.6.1.4.1.1466.20036':  # Notice of Disconnection as per RFC4511 (paragraph 4.4.1)
                        listen = False
                        closed_from_server = True

            if not listen and not closed_from_server and not self.connection.restarting:  # socket failure, start reconnect machinery
                self.connection.restarting = True
                counter = self.restartable_tries
            elif not listen and self.connection.restarting:  # try restart
                if counter:
                    sleep(self.restartable_sleep_time)
                    if not self.connection.closed:
                        try:  # resetting connection
                            self.connection.close()
                        except LDAPException:
                            pass
                    failure = False
                    try:  # reopening connection
                        self.connection.open(reset_usage=False)
                        if self._restart_tls:  # restart tls if start_tls was previously used
                            self.connection.start_tls()
                            self.connection.bind(self._last_bind_controls)  # binds with previously used controls
                    except LDAPException:
                        failure = True

                    if not failure:
                        try:  # reissues all operations in outstanding queue
                            for request in self._outstanding:
                                self.connection.send()
                            if self.connection.usage:
                                self.connection.usage.restartable_successes += 1
                            self.connection._restarting = False
                            return ret_value  # successful send
                        except LDAPException:
                            failure = True

                    if failure and self.connection.usage:
                        self.connection.usage.restartable_failures += 1

                    if not isinstance(counter, bool):
                        counter -= 1

                    if counter != 0:
                        listen = True

        self.connection.strategy.close()
