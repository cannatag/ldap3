"""
"""

# Created on 2016.08.11
#
# Author: Giovanni Cannata
#
# Copyright 2016 Giovanni Cannata
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

from .reader import Reader
from .writableEntry import WritableEntry
from .writableAttribute import WritableAttribute


class Writer(Reader):
    entry_class = WritableEntry
    attribute_class = WritableAttribute

    def commit(self, controls):
        for entry in self.entries:
            entry.entry_commit(controls)

    def discard(self):
        for entry in self.entries:
            entry.entry_discard()
