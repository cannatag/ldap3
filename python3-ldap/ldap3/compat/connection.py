"""
Created on 2013.05.31

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

from ..connection import Connection as newConnection
from ldap3 import SEARCH_SCOPE_WHOLE_SUBTREE, SEARCH_DEREFERENCE_ALWAYS, STRATEGY_SYNC


class Connection(newConnection):
    """
    Proxy class 8with camel case parameters) to new Connection class (pep8 compliant)
    """

    def __init__(self, server, user=None, password=None, autoBind=False, version=3, authentication=None, clientStrategy=STRATEGY_SYNC, autoReferrals=True, saslMechanism=None, saslCredentials=None, collectUsage=False, readOnly=False):
        newConnection.__init__(self, server, user, password, autoBind, version, authentication, clientStrategy, autoReferrals, saslMechanism, saslCredentials, collectUsage, readOnly)

    def search(self, searchBase, searchFilter, searchScope=SEARCH_SCOPE_WHOLE_SUBTREE, dereferenceAliases=SEARCH_DEREFERENCE_ALWAYS, attributes=None, sizeLimit=0, timeLimit=0, typesOnly=False, getOperationalAttributes=False, controls=None,
               pagedSize=None, pagedCriticality=False, pagedCookie=None):
        return newConnection.search(self, searchBase, searchFilter, searchScope, dereferenceAliases, attributes, sizeLimit, timeLimit, typesOnly, getOperationalAttributes, controls, pagedSize, pagedCriticality, pagedCookie)

    def add(self, dn, objectClass, attributes=None, controls=None):
        """
        add dn to the dib, objectClass is None, a class name or a list of class names,
        attributes is a dictionary in the form 'attr': 'val'
        or 'attr': ['val1', 'val2', 'valN'] for multivalued types
        """
        return newConnection.add(dn, objectClass, attributes, controls)

    def modifyDn(self, dn, relativeDn, deleteOldDn=True, newSuperior=None, controls=None):
        """
        Modify dn of the entry and optionally performs a move of the entry in the dib
        """
        return newConnection.modify_dn(self, dn, relativeDn, deleteOldDn, newSuperior, controls)

    def abandon(self, messageId, controls=None):
        """
        Abandon the operation indicated by messageId
        """
        return newConnection.abandon(self, messageId, controls)

    def extended(self, requestName, requestValue=None, controls=None):
        """
        Perform an extended operation
        """
        return newConnection.extended(self, requestName, requestValue, controls)

    def startTls(self):
        return newConnection.start_tls(self)

    def doSaslBind(self, controls):
        return newConnection.do_sasl_bind(self, controls)

    def refreshDsaInfo(self):
        return newConnection.refresh_dsa_info(self)

    def responseToLdif(self, searchResult=None, allBase64=False):
        return newConnection.response_to_ldif(self, searchResult, allBase64)
