####
LDIF
####

LDIF is a data interchange format for LDAP. It is defined in RFC2849 (June 2000) in two different flavours: *ldif-content* and *ldif-change*.
ldif-content is used to describe LDAP entries in an ASCII stream (i.e. a file), while ldif-change is used to describe Add, Delete, Modify and
ModifyDn operations. *These two formats have different purposes and cannot be mixed in the same stream.*
If the DN of the entry or an attribute value that contains any unicode character the value must be base64 encoded, as specified in RFC2849.
python3-ldap is compliant to the latest LDIF format (version: 1).

LDIF-content
============

You can use the ldif-content flavour with any search result::

    ...
    # request a few objects from the ldap server
    result = c.search('o=test','(cn=test-ldif*)', SEARCH_SCOPE_WHOLE_SUBTREE, attributes = ['sn', 'objectClass'])
    ldif_stream = c.response_to_ldif()
    ...


ldifStream will contain::

    version: 1
    dn: cn=test-ldif-1,o=test
    objectClass: inetOrgPerson
    objectClass: organizationalPerson
    objectClass: Person
    objectClass: ndsLoginProperties
    objectClass: Top
    sn: test-ldif-1

    dn: cn=test-ldif-2,o=test
    objectClass: inetOrgPerson
    objectClass: organizationalPerson
    objectClass: Person
    objectClass: ndsLoginProperties
    objectClass: Top
    sn:: dGVzdC1sZGlmLTItw6DDssO5


    # total number of entries: 2

you can even request a ldif-content for a response you saved early::

        # request a few objects from the ldap server
        result1 = c.search('o=test','(cn=test-ldif*)', SEARCH_SCOPE_WHOLE_SUBTREE, attributes = ['sn', 'objectClass'])
        result2 = c.search('o=test','(!(cn=test-ldif*))', SEARCH_SCOPE_WHOLE_SUBTREE, attributes = ['sn', 'objectClass'])
        ldif_stream = c.response_to_ldif(result1)

ldifStream will contain the LDIF representation of the result entries.

LDIF-change
===========

To have the ldif representation of Add, Modify, Delete and ModifyDn operation you must use the LDIF_PRODUCER strategy. With this strategy operations are
not executed on an LDAP server but are converted to an ldif-change format that can be sent to an LDAP server.

For example::

    from ldap3 import Connection, STRATEGY_LDIF_PRODUCER
    connection = Connection(server = None, clientStrategy = STRATEGY_LDIF_PRODUCER)  # no need of real LDAP server
    connection.add('cn=test-add-operation,o=test'), 'iNetOrgPerson',
                   {'objectClass': 'iNetOrgPerson', 'sn': 'test-add', 'cn': 'test-add-operation'})

    in connection.response you will find:

    version: 1
    dn: cn=test-add-operation,o=test
    changetype: add
    objectClass: inetorgperson
    sn: test-add
    cn: test-add-operation

A more complex modify operation (from the RFC2849 examples)::

    from ldap3 import MODIFY_ADD. MODIFY_DELETE, MODIFY_REPLACE
    connection.modify('cn=Paula Jensen, ou=Product Development, dc=airius, dc=com',
        {'postaladdress': (MODIFY_ADD, ['123 Anystreet $ Sunnyvale, CA $ 94086']),
         'description': (MODIFY_DELETE, []),
         'telephonenumber': (MODIFY_REPLACE, ['+1 408 555 1234', '+1 408 555 5678']),
         'facsimiletelephonenumber': (MODIFY_DELETE, ['+1 408 555 9876'])
        })

    returns:

    version: 1
    dn: cn=Paula Jensen, ou=Product Development, dc=airius, dc=com
    changetype: modify
    add: postaladdress
    postaladdress: 123 Anystreet $ Sunnyvale, CA $ 94086
    -
    delete: description
    -
    replace: telephonenumber
    telephonenumber: +1 408 555 1234
    telephonenumber: +1 408 555 5678
    -
    delete: facsimiletelephonenumber
    facsimiletelephonenumber: +1 408 555 9876
    -
