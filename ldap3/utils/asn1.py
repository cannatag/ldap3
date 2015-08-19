"""
"""

# Created on 2015.08.19
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

from pyasn1.codec.ber.encoder import tagMap, BooleanEncoder
from pyasn1.type.univ import Boolean
from pyasn1.compat.octets import ints2octs


# Monkeypatching of pyasn1 for encoding Boolean with the value 0xFF for TRUE
class BooleanCEREncoder(BooleanEncoder):
    _true = ints2octs((255,))

tagMap[Boolean.tagSet] = BooleanCEREncoder()

from pyasn1.codec.ber import encoder, decoder
