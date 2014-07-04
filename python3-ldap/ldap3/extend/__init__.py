"""
Created on 2014.04.28

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
from .novell.getBindDn import GetBindDn
from .novell.nmasGetUniversalPassword import NmasGetUniversalPassword
from .standard.whoAmI import WhoAmI
from .standard.modifyPassword import ModifyPassword


class ExtendedOperationsContainer(object):
    class StandardExtendedOperations(object):
        def __init__(self, container):
            self._container = container

        def who_am_i(self):
            return WhoAmI(self._container.connection).send()

        def modify_password(self, user=None, old_password=None, new_password=None):
            return ModifyPassword(self._container.connection, user, old_password, new_password).send()

    class NovellExtendedOperations(object):
        def __init__(self, container):
            self._container = container

        def get_bind_dn(self):
            return GetBindDn(self._container.connection).send()

        def nmas_get_universal_password(self, user):
            return NmasGetUniversalPassword(self._container.connection, user).send()

    def __init__(self, connection):
        self.connection = connection
        self.novell = self.NovellExtendedOperations(self)
        self.standard = self.StandardExtendedOperations(self)