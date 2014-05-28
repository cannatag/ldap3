###################################
LDIF (LDAP Data Interchange Format)
###################################

LDIF is a data interchange format for LDAP. It is defined in RFC2849 (June 2000) in two different flavours: *LDIF-CONTENT* and *LDIF-CHANGE*.
LDIF-CONTENT is used to describe LDAP entries in an ASCII stream (i.e. a file), while LDIF-CHANGEe is used to describe Add, Delete, Modify and
ModifyDn operations. *These two formats have different purposes and cannot be mixed in the same stream.*
If the DN of the entry or an attribute value contains any unicode character the value must be base64 encoded, as specified in RFC2849.
python3-ldap is compliant to the latest LDIF format (version: 1).

LDIF-CONTENT
============

You can use the LDIF-CONTENT flavour with any search result::

    ...
    # request a few objects from the ldap server
    result = c.search('o=test','(cn=test-ldif*)', SEARCH_SCOPE_WHOLE_SUBTREE, attributes = ['sn', 'objectClass'])
    ldif_output = c.response_to_ldif()
    ...


ldif_output will contain::

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

you can even request a LDIF-CONTENT for a response you saved early::

        # request a few objects from the ldap server
        response1 = c.search('o=test','(cn=test-ldif*)', SEARCH_SCOPE_WHOLE_SUBTREE, attributes = ['sn', 'objectClass'])
        response2 = c.search('o=test','(!(cn=test-ldif*))', SEARCH_SCOPE_WHOLE_SUBTREE, attributes = ['sn', 'objectClass'])
        ldif_output = c.response_to_ldif(response1)

ldif_output will contain the LDIF representation of the response entries.

LDIF-CHANGE
===========

To get the LDIF representation of Add, Modify, Delete and ModifyDn operation you must use the LDIF_PRODUCER strategy. With this strategy operations are
not executed on an LDAP server but are converted to an LDIF-CHANGE format that can be sent to an LDAP server.

For example::

    from ldap3 import Connection, STRATEGY_LDIF_PRODUCER
    connection = Connection(server = None, client_strategy = STRATEGY_LDIF_PRODUCER)  # no need of real LDAP server
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

Streaming the output to a file
==============================
When producing LDIF-CONTENT output you can have all operation results in a single stream. To get this simply set the stream attribute of the Connection to a stream object (for example to a file) and  *open* the connection.
If you don't specify the stream object a StringIO will be used. You can get the value with the c.stream.getvalue() method::

    from ldap3 import Connection, STRATEGY_LDIF_PRODUCER
    c = Connection(None, client_strategy=STRATEGY_LDIF_PRODUCER)
    with c:
        c.delete('cn=test1, o=test')
        c.delete('cn=test2, o=test')
        result = c.stjream.getvalue()  # needed because the stream is closed when the connection exits the context

result will be::

    version: 1

    dn: cn=test1,o=test
    changetype: delete

    dn: cn=test2,o=test
    changetype: delete


If you just define a file object as stream you'll find the output in the file::

    c = Connection(None, client_strategy=STRATEGY_LDIF_PRODUCER)
    c.stream = open('output.ldif', 'w')
    with c:
        c.delete('cn=test1, o= test')
        c.delete('cn=test2, o=test')

you will find the LDIF output in the output.ldif file.


When producing LDIF-CONTENT you can pass an existing stream object to the response_to_ldif() method to add the LDIF output to the stream. If the stream is empty the ldif version header will be added.

Custom line separator
=====================
The LDIF stream uses the default line separator (os.linesep) of the system where python3-ldap is running as line separator in the LDIF stream.
If you need a different line separator you can specify it in the *c.strategy.line_separator* attribute::

    c.strategy.line_separator = '\\r\\n'


Customizable descriptor order
=============================
RFC 2849 doesn't specify any specific order for the lines in the LDIF output except than *version: 1* in the first line of the stream.
The library starts any new record with the dn and all subsequent *descriptor: value* lines are in the order they are received by the library.
This should no be an issue with an LDIF import in another system, but if you have problems you can force a specific order for the descriptors in any of the LDIF operation:
To achieve this you must set the c.strategy.order attribute to a dict where the keys are set to the names of the operations you want their resulting descriptor order is changed
and the value to a list of descriptor. The LDIF output lines will be ordered following the order of the descriptor in the list.
For example if you add to the previous code::

    c.strategy.order = dict(delRequest = ['changetype:', 'dn:'])

you will get::

    version: 1

    changetype: delete
    dn: cn=test1,o=test

    changetype: delete
    dn: cn=test2,o=test

The possible operation names are: addRequest, delRequest, modifyRequest, modDNRequest.

To change the order of a searchRequest just pass the list