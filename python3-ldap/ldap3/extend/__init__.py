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
from ..extend.whoAmI import who_am_i
from ..extend.getBindDn import get_bind_dn
from ..extend.modifyPassword import modify_password


class ExtendedOperationsContainer(object):
    class StandardExtendedOperations(object):
        def __init__(self, container):
            self.container = container
        
        def who_am_i(self):
            return who_am_i(self.container.connection)

        def modify_password(self, old_password, new_password):
            return modify_password(self.container.connection, old_password, new_password)

    class NovellExtendedOperations(object):
        def __init__(self, container):
            self.container = container
            
        def get_bind_dn(self):
            return get_bind_dn(self.container.connection)

    def __init__(self, connection):
        self.connection = connection
        self.novell = self.NovellExtendedOperations(self)
        self.standard = self.StandardExtendedOperations(self)