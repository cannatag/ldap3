"""
"""

# Created on 2014.11.17
#
# Author: Giovanni Cannata
#
# Copyright 2015 Giovanni Cannata
#
# This file is part of ldap3.
#
# ldap3 is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ldap3 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ldap3 in the COPYING and COPYING.LESSER files.
# If not, see <http://www.gnu.org/licenses/>.
from random import SystemRandom
from ..core.dsa import Dsa
from ..strategy.sync import SyncStrategy


# noinspection PyProtectedMember

class MockSyncStrategy(SyncStrategy):
    """
    This strategy create a mock LDAP server, with synchronous access
    It can be useful to test LDAP without a real Server
    """
    def __init__(self, ldap_connection):
        SyncStrategy.__init__(self, ldap_connection)
        self.sync = True
        self.no_real_dsa = True
        self.pooled = False
        self.can_stream = False
        self.dsa = Dsa(ldap_connection.server)
        self.connection_id = str(SystemRandom().random())[-8:]

    def sending(self, ldap_message):
        self.dsa.accept_request(self.connection_id, ldap_message)

    def receiving(self):
        return [self.dsa.produce_response(self.connection_id)]

    def _start_listen(self):
        self.dsa.do_open(connection_id=self.connection_id)
        self.connection.listening = True
        self.connection.closed = False
        self._header_added = False
        print('start listening')

    def _stop_listen(self):
        self.connection.listening = False
        self.connection.closed = True
        print('stop listening')

