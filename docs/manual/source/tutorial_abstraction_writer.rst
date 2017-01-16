Tutorial: ldap3 Abstraction Layer - Writing data
################################################

Writing entries
---------------

Modifying data on an LDAP server is easy with the Abstraction Layer, just add a new Entry with its Attribute values (or change the Attribute
values of an existing Entry) and commit the pending changes to the DIT via the Writer cursor. You can obtain a Writer cursor in a number of ways:

* from a Reader Cursor, using the ``Writer.from_cursor()`` static method that populates the ``entries`` collection with a copy of the Entries
  from the Reader cursor.

* from a Search response, using the ``Writer.from_response()`` static method, that populates the ``entries`` collection with a copy of the Entries
  from the Search response.

* from a single Entry in a Reader cursor, using the ``entry_writable()`` method of the Entry, that returns a new Writable
  Entry (and also creates its Writer cursor).

* from a single Entry in a Search response, using the ``entry_writable()`` method of the Entry, that returns a new Writable
  Entry (and also creates its Writer cursor)

* as a new instance of the ldap3.abstract.Writer class, using ``Writer()`` that creates a new Writer cursor with an empty ``entries``
  collection. With this cursor you can only create new Entries.

Let's obtain a Writer cursor from the inetOrgPerson Reader we used in the previous chapter::

    >>> r = Reader(conn, obj_inetorgperson, 'ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org')
    >>> r.search()
    >>> w = Writer.from_cursor(r)
    >>> w
    CURSOR : Writer
    CONN   : ldap://ipa.demo1.freeipa.org:389 - cleartext - user: uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org - not lazy - bound - open - <local: 10.3.9.227:29872 - remote: 209.132.178.99:389> - tls not started - listening - SyncStrategy - internal decoder
    DEFS   : ['inetOrgPerson'] [audio, businessCategory, carLicense, cn, departmentNumber, description, destinationIndicator, displayName, employeeNumber, employeeType, facsimileTelephoneNumber, givenName, homePhone, homePostalAddress, initials, internationalISDNNumber, jpegPhoto, l, labeledURI, mail, manager, mobile, o, objectClass, ou, pager, photo, physicalDeliveryOfficeName, postOfficeBox, postalAddress, postalCode, preferredDeliveryMethod, preferredLanguage, registeredAddress, roomNumber, secretary, seeAlso, sn, st, street, telephoneNumber, teletexTerminalIdentifier, telexNumber, title, uid, userCertificate, userPKCS12, userPassword, userSMIMECertificate, x121Address, x500UniqueIdentifier]
    ATTRS  : ['audio', 'businessCategory', 'carLicense', 'cn', 'departmentNumber', 'description', 'destinationIndicator', 'displayName', 'employeeNumber', 'employeeType', 'facsimileTelephoneNumber', 'givenName', 'homePhone', 'homePostalAddress', 'initials', 'internationalISDNNumber', 'jpegPhoto', 'l', 'labeledURI', 'mail', 'manager', 'mobile', 'o', 'objectClass', 'ou', 'pager', 'photo', 'physicalDeliveryOfficeName', 'postOfficeBox', 'postalAddress', 'postalCode', 'preferredDeliveryMethod', 'preferredLanguage', 'registeredAddress', 'roomNumber', 'secretary', 'seeAlso', 'sn', 'st', 'street', 'telephoneNumber', 'teletexTerminalIdentifier', 'telexNumber', 'title', 'uid', 'userCertificate', 'userPKCS12', 'userPassword', 'userSMIMECertificate', 'x121Address', 'x500UniqueIdentifier']
    ENTRIES: 3 [executed at: 2016-11-09T14:24:49.374675]

Entries in a Writer cursor are standard Python object, so you can modify them with standard Python code::

    >>> w[0]
    DN: cn=b.young,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org - STATUS: Writable - READ TIME: 2016-11-09T14:26:03.866351
        cn: b.young
        departmentNumber: DEV
        givenName: Beatrix
        objectClass: inetOrgPerson
                     organizationalPerson
                     person
                     top
        sn: Young
        telephoneNumber: 1111

The entry is in **Writable** status now, so you can try to update some values. All modifications are stored in memory until committed or the entry
is returned to its original values::

    >>> w[0].sn += 'Smyth'  # Add 'Smith' value from the sn
    >>> w[0].sn += 'Johnson'  # Add 'Johnson' value from the sn
    >>> w[0].sn -= 'Young'  # remove the 'Young' value from the sn

Now let's revise the modifications we have requested::

    >>> w[0].entry_changes
    OrderedDict([('sn', [('MODIFY_ADD', ['Smyth']), ('MODIFY_ADD', ['Johnson']), ('MODIFY_DELETE', ['Young'])])])

Modifications to an Entry are stored in a way (OrderedDict) that preserves the insertion sequence. This can be helpful with specific LDAP
operations that request that an attribute is modified before an other one in the same LDAP operation

We made a typo so discard the changes and insert the correct values:

    >>> w[0].sn.discard()
    >>> w[0].sn += ['Smith', 'Johnson']  # add a list of values
    >>> w[0].sn -= 'Young'  # remove the 'Young' value from the sn
    >>> w[0]
    DN: cn=b.young,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org - STATUS: Writable, Pending changes - READ TIME: 2016-11-09T14:30:43.181520
        cn: b.young
        departmentNumber: DEV
        givenName: Beatrix
        objectClass: inetOrgPerson
                     organizationalPerson
                     person
                     top
        sn: Young
            CHANGES: [('MODIFY_ADD', ['Smith', 'Johnson']), ('MODIFY_DELETE', ['Young'])]
        telephoneNumber: 1111

Entry status is set to *Writable, Pending changes*, this means that mandatory Attributes are set and the Entry can be written in the DIT::

    >>> w.commit()  # commit all entries with pending changes
    >>> w[0]
    DN: cn=b.young,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org - STATUS: Writable, Committed - READ TIME: 2016-11-09T14:32:14.377498
        cn: b.young
        departmentNumber: DEV
        givenName: Beatrix
        objectClass: inetOrgPerson
                     organizationalPerson
                     person
                     top
        sn: Smith
            Johnson
        telephoneNumber: 1111

Entry has been written on the DIT and its state is now *Writable, Committed*. If you look at the original Entry in the Reader you will find that
it's been updated with the new values::

    >>> r[0]
    DN: cn=b.young,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org - STATUS: Read - READ TIME: 2016-11-09T14:32:14.377498
        cn: b.young
        departmentNumber: DEV
        givenName: Beatrix
        objectClass: inetOrgPerson
                     organizationalPerson
                     person
                     top
        sn: Smith
            Johnson
        telephoneNumber: 1111

Refreshing of the original Entry is triggered only if both cursors are using the same Server object. If you use the Writer cursor to copy Entries
to another LDAP server refreshing of the original Entry is not executed.

For specific types (boolean, integers and dates) you can set the value to the relevant Python type. The ldap3 library will perform the necessary
conversion to the value expected from the LDAP server.
