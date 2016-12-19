"""
"""

# Created on 2016.12.19
#
# Author: Giovanni Cannata
#
# Copyright 2014, 2015, 2016 Giovanni Cannata
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


from ... import NO_ATTRIBUTES, ALL_ATTRIBUTES
from ...operation.search import build_attribute_selection
from ...protocol.controls import build_control


def __read_control(oid, attributes, criticality=False):
    if not attributes:
        attributes = [NO_ATTRIBUTES]
    elif attributes == ALL_ATTRIBUTES:
        attributes = [ALL_ATTRIBUTES]

    value = build_attribute_selection(attributes, None)
    return build_control(oid, criticality, value)


def pre_read_control(attributes, criticality=False):
    """Create a pre-read control for a request.

    When passed as a control to the controls parameter of an operation, it will
    return the value in `Connection.result` before the operation took place.
    """
    return __read_control('1.3.6.1.1.13.1', attributes, criticality)


def post_read_control(attributes, criticality=False):
    """Create a post-read control for a request.

    When passed as a control to the controls parameter of an operation, it will
    return the value in `Connection.result` after the operation took place.
    """
    return __read_control('1.3.6.1.1.13.2', attributes, criticality)
