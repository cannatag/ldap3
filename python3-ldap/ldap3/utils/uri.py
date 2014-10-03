"""
"""

# Created on 2014.09.08
#
# Author: Giovanni Cannata
#
# Copyright 2014 Giovanni Cannata
#
# This file is part of python3-ldap.
#
# python3-ldap is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python3-ldap is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with python3-ldap in the COPYING and COPYING.LESSER files.
# If not, see <http://www.gnu.org/licenses/>.

from .. import SEARCH_SCOPE_WHOLE_SUBTREE, SEARCH_SCOPE_BASE_OBJECT, SEARCH_SCOPE_SINGLE_LEVEL


def parse_uri(uri):
    """
    Decode LDAP URI as specified in RFC 4516 relaxing specifications
    permitting 'ldaps' as scheme for ssl-ldap
    """

    # ldapurl     = scheme COLON SLASH SLASH [host [COLON port]]
    # [SLASH dn [QUESTION [attributes]
    #                [QUESTION [scope] [QUESTION [filter]
    #                [QUESTION extensions]]]]]
    #                               ; <host> and <port> are defined
    #                               ;   in Sections 3.2.2 and 3.2.3
    #                               ;   of [RFC3986].
    #                               ; <filter> is from Section 3 of
    #                               ;   [RFC4515], subject to the
    #                               ;   provisions of the
    #                               ;   "Percent-Encoding" section
    #                               ;   below.
    #
    # scheme      = "ldap" / "ldaps"  <== not RFC4516 compliant (original is 'scheme      = "ldap"')
    # dn          = distinguishedName ; From Section 3 of [RFC4514],
    #                               ; subject to the provisions of
    #                               ; the "Percent-Encoding"
    #                               ; section below.
    #
    # attributes  = attrdesc *(COMMA attrdesc)
    # attrdesc    = selector *(COMMA selector)
    # selector    = attributeSelector ; From Section 4.5.1 of
    #                               ; [RFC4511], subject to the
    #                               ; provisions of the
    #                               ; "Percent-Encoding" section
    #                               ; below.
    #
    # scope       = "base" / "one" / "sub"
    # extensions  = extension *(COMMA extension)
    # extension   = [EXCLAMATION] extype [EQUALS exvalue]
    # extype      = oid               ; From section 1.4 of [RFC4512].
    #
    # exvalue     = LDAPString        ; From section 4.1.2 of
    #                               ; [RFC4511], subject to the
    #                               ; provisions of the
    #                               ; "Percent-Encoding" section
    #                               ; below.
    #
    # EXCLAMATION = %x21              ; exclamation mark ("!")
    # SLASH       = %x2F              ; forward slash ("/")
    # COLON       = %x3A              ; colon (":")
    # QUESTION    = %x3F              ; question mark ("?")

    uri_components = dict()
    parts = uri.split('?')
    scheme, sep, remain = parts[0].partition('://')
    if sep != '://' or scheme not in ['ldap', 'ldaps']:
        return None

    address, _, uri_components['base'] = remain.partition('/')

    uri_components['ssl'] = True if scheme == 'ldaps' else False
    uri_components['host'], sep, uri_components['port'] = address.partition(':')
    if sep != ':':
        uri_components['port'] = None
    else:
        if not uri_components['port'].isdigit() or not (0 < int(uri_components['port']) < 65536):
            return None
        else:
            uri_components['port'] = int(uri_components['port'])

    uri_components['attributes'] = parts[1].split(',') if len(parts) > 1 else None
    uri_components['scope'] = parts[2] if len(parts) > 2 else None
    if uri_components['scope'] == 'base':
        uri_components['scope'] = SEARCH_SCOPE_BASE_OBJECT
    elif uri_components['scope'] == 'sub':
        uri_components['scope'] = SEARCH_SCOPE_WHOLE_SUBTREE
    elif uri_components['scope'] == 'one':
        uri_components['scope'] = SEARCH_SCOPE_SINGLE_LEVEL
    elif uri_components['scope']:
        return None

    uri_components['filter'] = parts[3] if len(parts) > 3 else None
    uri_components['extensions'] = parts[3].split(',') if len(parts) > 4 else None

    return uri_components