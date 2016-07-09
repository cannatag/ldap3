"""
"""

# Created on 2016.07.08
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


from ...core.exceptions import LDAPExtensionError
from ...protocol.persistentSearch import persistent_search_control
from ... import SUBTREE, DEREF_ALWAYS, SEQUENCE_TYPES

try:
    from queue import Queue
except ImportError:  # Python 2
    # noinspection PyUnresolvedReferences
    from Queue import Queue


class PersistentSearch(object):
    def __init__(self,
                 connection,
                 search_base,
                 search_filter,
                 search_scope,
                 dereference_aliases,
                 attributes,
                 size_limit,
                 time_limit,
                 changes_only,
                 events_type,
                 notifications,
                 controls
                 ):
        if connection.strategy.sync:
            raise LDAPExtensionError('For Persistent Searches you must provide an asynchronous connection')

        self.connection = connection
        self.changes_only = changes_only
        self.notifications = notifications
        self.message_id = None
        self.base = search_base
        self.filter = search_filter
        self.scope = search_scope
        self.dereference_aliases=dereference_aliases
        self.attributes = attributes
        self.size_limit = size_limit
        self.time_limit = time_limit

        if not isinstance(controls, SEQUENCE_TYPES):
            self.controls = []
        else:
            self.controls = controls

        self.controls.append(persistent_search_control(events_type, changes_only, notifications))
        self.start()

    def start(self):
        if self.message_id: # persistent search already started
            return

        if not self.connection.bound:
            self.connection.bind()

        with self.connection.strategy.lock:
            self.message_id = self.connection.search(search_base=self.base,
                                                     search_filter=self.filter,
                                                     search_scope=self.scope,
                                                     dereference_aliases=self.dereference_aliases,
                                                     attributes=self.attributes,
                                                     size_limit=self.size_limit,
                                                     time_limit=self.time_limit,
                                                     controls=self.controls)
            self.connection.strategy.persistent_search_message_id = self.message_id

    def stop(self):
        self.connection.abandon(self.message_id)
        self.connection.unbind()
        if self.message_id in self.connection.strategy._responses:
            del self.connection.strategy._responses[self.message_id]
        self.connection.strategy.persistent_search_message_id = None
        self.message_id = None
