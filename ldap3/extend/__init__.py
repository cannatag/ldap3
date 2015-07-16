"""
"""

# Created on 2014.04.28
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

from os import linesep

from .. import SUBTREE, DEREF_ALWAYS
from .novell.partition_entry_count import PartitionEntryCount
from .novell.replicaInfo import ReplicaInfo
from .novell.listReplicas import ListReplicas
from .novell.getBindDn import GetBindDn
from .novell.nmasGetUniversalPassword import NmasGetUniversalPassword
from .novell.nmasSetUniversalPassword import NmasSetUniversalPassword
from .standard.whoAmI import WhoAmI
from .standard.modifyPassword import ModifyPassword
from .standard.PagedSearch import paged_search_generator, paged_search_accumulator


class ExtendedOperationContainer(object):
    def __init__(self, connection):
        self._connection = connection

    def __repr__(self):
        return linesep.join(['  ' + element for element in dir(self) if element[0] != '_'])

    def __str__(self):
        return self.__repr__()


class StandardExtendedOperations(ExtendedOperationContainer):
    def who_am_i(self):
        return WhoAmI(self._connection).send()

    def modify_password(self,
                        user=None,
                        old_password=None,
                        new_password=None,
                        hashed=None):

        return ModifyPassword(self._connection, user, old_password, new_password, hashed).send()

    def paged_search(self,
                     search_base,
                     search_filter,
                     search_scope=SUBTREE,
                     dereference_aliases=DEREF_ALWAYS,
                     attributes=None,
                     size_limit=0,
                     time_limit=0,
                     types_only=False,
                     get_operational_attributes=False,
                     controls=None,
                     paged_size=100,
                     paged_criticality=False,
                     generator=True):

        if generator:
            return paged_search_generator(self._connection, search_base, search_filter, search_scope, dereference_aliases, attributes, size_limit, time_limit, types_only, get_operational_attributes, controls, paged_size, paged_criticality)
        else:
            return paged_search_accumulator(self._connection, search_base, search_filter, search_scope, dereference_aliases, attributes, size_limit, time_limit, types_only, get_operational_attributes, controls, paged_size, paged_criticality)


class NovellExtendedOperations(ExtendedOperationContainer):
    def get_bind_dn(self):
        return GetBindDn(self._connection).send()

    def get_universal_password(self, user):
        return NmasGetUniversalPassword(self._connection, user).send()

    def set_universal_password(self, user, new_password=None):
        return NmasSetUniversalPassword(self._connection, user, new_password).send()

    def list_replicas(self, server_dn):
        return ListReplicas(self._connection, server_dn).send()

    def partition_entry_count(self, partition_dn):
        return PartitionEntryCount(self._connection, partition_dn).send()

    def replica_info(self, server_dn, partition_dn):
        return ReplicaInfo(self._connection, server_dn, partition_dn).send()


class MicrosoftExtendedOperations(ExtendedOperationContainer):
    pass


class ExtendedOperationsRoot(ExtendedOperationContainer):
    def __init__(self, connection):
        ExtendedOperationContainer.__init__(self, connection)  # calls super
        self.standard = StandardExtendedOperations(self._connection)
        self.novell = NovellExtendedOperations(self._connection)
        self.microsoft = MicrosoftExtendedOperations(self._connection)
