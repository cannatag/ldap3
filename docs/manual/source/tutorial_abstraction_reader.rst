Tutorial: ldap3 Abstraction Layer - Reading data
################################################

Reading entries
---------------
Let's define a Reader cursor to get all the entries of class 'inetOrgPerson' in the 'ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org' context::

    >>> obj_inetorgperson = ObjectDef('inetOrgPerson', conn)
    >>> r = Reader(conn, obj_inetorgperson, 'ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org')
    >>> r
    CURSOR : Reader
    CONN   : ldap://ipa.demo1.freeipa.org:389 - cleartext - user: uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org - not lazy - bound - open - <local: 10.3.9.227:17296 - remote: 209.132.178.99:389> - tls not started - listening - SyncStrategy - internal decoder
    DEFS   : ['inetOrgPerson'] [audio, businessCategory, carLicense, cn, departmentNumber, description, destinationIndicator, displayName, employeeNumber, employeeType, facsimileTelephoneNumber, givenName, homePhone, homePostalAddress, initials, internationalISDNNumber, jpegPhoto, l, labeledURI, mail, manager, mobile, o, objectClass, ou, pager, photo, physicalDeliveryOfficeName, postOfficeBox, postalAddress, postalCode, preferredDeliveryMethod, preferredLanguage, registeredAddress, roomNumber, secretary, seeAlso, sn, st, street, telephoneNumber, teletexTerminalIdentifier, telexNumber, title, uid, userCertificate, userPKCS12, userPassword, userSMIMECertificate, x121Address, x500UniqueIdentifier]
    ATTRS  : ['audio', 'businessCategory', 'carLicense', 'cn', 'departmentNumber', 'description', 'destinationIndicator', 'displayName', 'employeeNumber', 'employeeType', 'facsimileTelephoneNumber', 'givenName', 'homePhone', 'homePostalAddress', 'initials', 'internationalISDNNumber', 'jpegPhoto', 'l', 'labeledURI', 'mail', 'manager', 'mobile', 'o', 'objectClass', 'ou', 'pager', 'photo', 'physicalDeliveryOfficeName', 'postOfficeBox', 'postalAddress', 'postalCode', 'preferredDeliveryMethod', 'preferredLanguage', 'registeredAddress', 'roomNumber', 'secretary', 'seeAlso', 'sn', 'st', 'street', 'telephoneNumber', 'teletexTerminalIdentifier', 'telexNumber', 'title', 'uid', 'userCertificate', 'userPKCS12', 'userPassword', 'userSMIMECertificate', 'x121Address', 'x500UniqueIdentifier']
    BASE   : 'ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org' [SUB]
    FILTER : '(objectClass=inetOrgPerson)'

We didn't provide any filter, but the Reader automatically uses the ObjectDef class to read entries of the requested object class.
Now you can ask the Reader to execute the search, fetching the results in its ``entries`` property::

    >>> r.search()
    >>> r
    CURSOR : Reader
    CONN   : ldap://ipa.demo1.freeipa.org:389 - cleartext - user: uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org - not lazy - bound - open - <local: 10.3.9.227:27370 - remote: 209.132.178.99:389> - tls not started - listening - SyncStrategy - internal decoder
    DEFS   : ['inetOrgPerson'] [audio, businessCategory, carLicense, cn, departmentNumber, description, destinationIndicator, displayName, employeeNumber, employeeType, facsimileTelephoneNumber, givenName, homePhone, homePostalAddress, initials, internationalISDNNumber, jpegPhoto, l, labeledURI, mail, manager, mobile, o, objectClass, ou, pager, photo, physicalDeliveryOfficeName, postOfficeBox, postalAddress, postalCode, preferredDeliveryMethod, preferredLanguage, registeredAddress, roomNumber, secretary, seeAlso, sn, st, street, telephoneNumber, teletexTerminalIdentifier, telexNumber, title, uid, userCertificate, userPKCS12, userPassword, userSMIMECertificate, x121Address, x500UniqueIdentifier]
    ATTRS  : ['audio', 'businessCategory', 'carLicense', 'cn', 'departmentNumber', 'description', 'destinationIndicator', 'displayName', 'employeeNumber', 'employeeType', 'facsimileTelephoneNumber', 'givenName', 'homePhone', 'homePostalAddress', 'initials', 'internationalISDNNumber', 'jpegPhoto', 'l', 'labeledURI', 'mail', 'manager', 'mobile', 'o', 'objectClass', 'ou', 'pager', 'photo', 'physicalDeliveryOfficeName', 'postOfficeBox', 'postalAddress', 'postalCode', 'preferredDeliveryMethod', 'preferredLanguage', 'registeredAddress', 'roomNumber', 'secretary', 'seeAlso', 'sn', 'st', 'street', 'telephoneNumber', 'teletexTerminalIdentifier', 'telexNumber', 'title', 'uid', 'userCertificate', 'userPKCS12', 'userPassword', 'userSMIMECertificate', 'x121Address', 'x500UniqueIdentifier']
    BASE   : 'ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org' [SUB]
    FILTER : '(objectClass=inetOrgPerson)'
    ENTRIES: 3 [executed at: 2016-11-09T09:33:00.342762]

There are now three Entries in the Reader. An Entry has some interesting features accessible from its properties and methods. Because
Attribute names are used as Entry properties all the "operational" properties and methods of an Entry start with the **entry_** prefix
(the underscore is an invalid character in an attribute name, so there can't be an attribute with that name). It's easy to get a useful
representation of an Entry::

    >>> r[0]
    DN: cn=b.young,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org - STATUS: Read - READ TIME: 2016-11-09T09:35:02.739203
        cn: b.young
        departmentNumber: DEV
        givenName: Beatrix
        objectClass: inetOrgPerson
                     organizationalPerson
                     person
                     top
        sn: Young
        telephoneNumber: 1111

Let's explore some of them::

    >>> # get the DN of an entry
    >>> r[0].entry_dn
    'cn=b.young,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org'

    >>> # query the attributes in the Entry as a list of names
    >>> r[0].entry_attributes
    ['destinationIndicator', 'x500UniqueIdentifier', 'audio', 'photo', 'uid', 'l', 'pager', 'carLicense', 'street', 'teletexTerminalIdentifier', 'o', 'st', 'homePostalAddress', 'preferredDeliveryMethod', 'roomNumber', 'sn', 'homePhone', 'x121Address', 'displayName', 'userSMIMECertificate', 'userPassword', 'title', 'physicalDeliveryOfficeName', 'mail', 'initials', 'ou', 'businessCategory', 'seeAlso', 'jpegPhoto', 'registeredAddress', 'facsimileTelephoneNumber', 'postalAddress', 'telephoneNumber', 'mobile', 'labeledURI', 'postalCode', 'objectClass', 'employeeNumber', 'secretary', 'employeeType', 'description', 'cn', 'userCertificate', 'userPKCS12', 'postOfficeBox', 'departmentNumber', 'givenName', 'internationalISDNNumber', 'preferredLanguage', 'telexNumber', 'manager']

    >>> # query the attributes in the Entry as a dict of key/value pairs
    >>> r[0].entry_attributes_as_dict
    {'destinationIndicator': [], 'x500UniqueIdentifier': [], 'audio': [], 'photo': [], 'uid': [], 'l': [], 'pager': [], 'carLicense': [], 'street': [], 'teletexTerminalIdentifier': [], 'o': [], 'homePostalAddress': [], 'preferredDeliveryMethod': [], 'roomNumber': [], 'st': [], 'homePhone': [], 'x121Address': [], 'displayName': [], 'userSMIMECertificate': [], 'userPassword': [], 'title': [], 'physicalDeliveryOfficeName': [], 'mail': [], 'preferredLanguage': [], 'initials': [], 'internationalISDNNumber': [], 'ou': [], 'businessCategory': [], 'seeAlso': [], 'jpegPhoto': [], 'registeredAddress': [], 'facsimileTelephoneNumber': [], 'postalAddress': [], 'telephoneNumber': ['1111'], 'mobile': [], 'labeledURI': [], 'postalCode': [], 'objectClass': ['inetOrgPerson', 'organizationalPerson', 'person', 'top'], 'employeeNumber': [], 'description': [], 'employeeType': [], 'secretary': [], 'cn': ['b.young'], 'userPKCS12': [], 'postOfficeBox': [], 'departmentNumber': ['DEV'], 'givenName': ['Beatrix'], 'sn': ['Young'], 'userCertificate': [], 'telexNumber': [], 'manager': []}


    >>> # let's check which attributes are mandatory
    >>> r[0].entry_mandatory_attributes
    ['sn', 'objectClass', 'cn']

    >>> # convert the Entry to LDIF
    >>> print(r[0].entry_to_ldif())
    version: 1
    dn: cn=b.young,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org
    objectClass: inetOrgPerson
    objectClass: organizationalPerson
    objectClass: person
    objectClass: top
    sn: Young
    telephoneNumber: 1111
    cn: b.young
    departmentNumber: DEV
    givenName: Beatrix
    # total number of entries: 1

    >>> print(r[0].entry_to_json(include_empty=False))  # Use include_empty=True to include empty attributes
    {
        "attributes": {
            "cn": [
                "b.young"
            ],
            "departmentNumber": [
                "DEV"
            ],
            "givenName": [
                "Beatrix"
            ],
            "objectClass": [
                "inetOrgPerson",
                "organizationalPerson",
                "person",
                "top"
            ],
            "sn": [
                "Young"
            ],
            "telephoneNumber": [
                "1111"
            ]
        },
        "dn": "cn=b.young,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org"
    }

If you search for the uid=admin entry there are some auxiliary classes attached to it. The uid=admin entry is not an *inetOrgPerson* but a *person*,
so you must use the ``obj_person`` defined in the previous chapter of this tutorial::

    >>> obj_person
    OBJ : person [person (Structural) 2.5.6.6, top (Abstract) 2.5.6.0]
    MUST: cn, objectClass, sn
    MAY : description, seeAlso, telephoneNumber, userPassword

This ObjectDef lacks the *uid* attributes, used for naming the admin entry, so we must add it to the Object definition:

    >>> obj_person += 'uid'  # implicitly creates a new AttrDef
    >>> obj_person
    OBJ : person [person (Structural) 2.5.6.6, top (Abstract) 2.5.6.0]
    MUST: cn, objectClass, sn
    MAY : description, seeAlso, telephoneNumber, uid, userPassword

Now let's build the Reader cursor, using the Simplified Query Language, note how the filter is converted::

    >>> r = Reader(conn, obj_person, 'cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org', 'uid:=admin')
    >>> r
    CURSOR : Reader
    CONN   : ldap://ipa.demo1.freeipa.org:389 - cleartext - user: uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org - not lazy - bound - open - <local: 10.3.9.227:27438 - remote: 209.132.178.99:389> - tls not started - listening - SyncStrategy - internal decoder
    DEFS   : ['person'] [cn, description, objectClass, seeAlso, sn, telephoneNumber, uid, userPassword]
    ATTRS  : ['cn', 'description', 'objectClass', 'seeAlso', 'sn', 'telephoneNumber', 'uid', 'userPassword']
    BASE   : 'cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org' [SUB]
    QUERY  : 'uid:=admin' [AND]
    PARSED : 'uid: =admin' [AND]
    FILTER : '(&(objectClass=person)(uid=admin))'

And finally perform the search operation::
    >>> r.search()
    [DN: uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org - STATUS: Read - READ TIME: 2016-11-09T09:59:56.393112
        cn: Administrator
        objectClass: top
                     person
                     posixaccount
                     krbprincipalaux
                     krbticketpolicyaux
                     inetuser
                     ipaobject
                     ipasshuser
                     ipaSshGroupOfPubKeys
                     ipaNTUserAttrs
        sn: Administrator
        uid: admin]

Only one entry is found. As you can see this Entry has additional auxiliary object classes attached. This means that there can be other
attributes stored in the entry. Let's define an ObjectDef that also requests the 'posixAccount' and the 'krbprincipalaux' object classes::

    >>> obj_person = ObjectDef(['person', 'posixAccount', 'krbprincipalaux'], conn)
    OBJ : person, posixAccount, krbPrincipalAux [person (Structural) 2.5.6.6, top (Abstract) 2.5.6.0, posixAccount (Auxiliary) 1.3.6.1.1.1.2.0, top (Abstract) 2.5.6.0, krbPrincipalAux (Auxiliary) 2.16.840.1.113719.1.301.6.8.1]
    MUST: cn, gidNumber, homeDirectory, objectClass, sn, uid, uidNumber
    MAY : description, gecos, krbAllowedToDelegateTo, krbCanonicalName, krbExtraData, krbLastAdminUnlock, krbLastFailedAuth, krbLastPwdChange, krbLastSuccessfulAuth, krbLoginFailedCount, krbPasswordExpiration, krbPrincipalAliases, krbPrincipalAuthInd, krbPrincipalExpiration, krbPrincipalKey, krbPrincipalName, krbPrincipalType, krbPwdHistory, krbPwdPolicyReference, krbTicketPolicyReference, krbUPEnabled, loginShell, seeAlso, telephoneNumber, userPassword

As you can see the ObjectDef now includes all Attributes from the *person*, *top*, *posixAccount* and *krbPrincipalAux* classes. Now create a new Reader, its
filter will automatically includes all the requested object classes::

    >>> r = Reader(conn, obj_person, 'dc=demo1,dc=freeipa,dc=org', 'uid:=admin')
    >>> r
    CURSOR : Reader
    CONN   : ldap://ipa.demo1.freeipa.org:389 - cleartext - user: uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org - not lazy - bound - open - <local: 10.3.9.227:29283 - remote: 209.132.178.99:389> - tls not started - listening - SyncStrategy - internal decoder
    DEFS   : ['person', 'posixAccount', 'krbPrincipalAux'] [cn, description, gecos, gidNumber, homeDirectory, krbAllowedToDelegateTo, krbCanonicalName, krbExtraData, krbLastAdminUnlock, krbLastFailedAuth, krbLastPwdChange, krbLastSuccessfulAuth, krbLoginFailedCount, krbPasswordExpiration, krbPrincipalAliases, krbPrincipalAuthInd, krbPrincipalExpiration, krbPrincipalKey, krbPrincipalName, krbPrincipalType, krbPwdHistory, krbPwdPolicyReference, krbTicketPolicyReference, krbUPEnabled, loginShell, objectClass, seeAlso, sn, telephoneNumber, uid, uidNumber, userPassword]
    ATTRS  : ['cn', 'description', 'gecos', 'gidNumber', 'homeDirectory', 'krbAllowedToDelegateTo', 'krbCanonicalName', 'krbExtraData', 'krbLastAdminUnlock', 'krbLastFailedAuth', 'krbLastPwdChange', 'krbLastSuccessfulAuth', 'krbLoginFailedCount', 'krbPasswordExpiration', 'krbPrincipalAliases', 'krbPrincipalAuthInd', 'krbPrincipalExpiration', 'krbPrincipalKey', 'krbPrincipalName', 'krbPrincipalType', 'krbPwdHistory', 'krbPwdPolicyReference', 'krbTicketPolicyReference', 'krbUPEnabled', 'loginShell', 'objectClass', 'seeAlso', 'sn', 'telephoneNumber', 'uid', 'uidNumber', 'userPassword']
    BASE   : 'dc=demo1,dc=freeipa,dc=org' [SUB]
    QUERY  : 'uid:=admin' [AND]
    PARSED : 'uid: =admin' [AND]
    FILTER : '(&(&(objectClass=person)(objectClass=posixAccount)(objectClass=krbPrincipalAux))(uid=admin))'

    >>> r.search()
    >>> r[0]
    DN: uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org - STATUS: Read - READ TIME: 2016-11-09T10:03:47.741382
        cn: Administrator
        gecos: Administrator
        gidNumber: 1120000000
        homeDirectory: /home/admin
        krbExtraData: b'\x00\x02\xd2\xad"Xroot/admin@DEMO1.FREEIPA.ORG\x00'
        krbLastFailedAuth: 2016-11-09 06:22:15+00:00
        krbLastPwdChange: 2016-11-09 05:02:10+00:00
        krbLastSuccessfulAuth: 2016-11-09 09:03:49+00:00
        krbLoginFailedCount: 0
        krbPasswordExpiration: 2017-11-09 05:02:10+00:00
        krbPrincipalName: admin@DEMO1.FREEIPA.ORG
        loginShell: /bin/bash
        objectClass: top
                     person
                     posixaccount
                     krbprincipalaux
                     krbticketpolicyaux
                     inetuser
                     ipaobject
                     ipasshuser
                     ipaSshGroupOfPubKeys
                     ipaNTUserAttrs
        sn: Administrator
        uid: admin
        uidNumber: 1120000000

Note that Attribute are properly formatted thanks to information read in the server schema. For example the krbLastPwdChange is stored as
a date (Generalized Time, a standard LDAP data type)::

    >>> obj_person.krblastpwdchange
    ATTR: krbLastPwdChange - mandatory: False - single_value: True
      Attribute type: 2.16.840.1.113719.1.301.4.45.1
        Short name: krbLastPwdChange
        Single value: True
        Equality rule: generalizedTimeMatch
        Syntax: 1.3.6.1.4.1.1466.115.121.1.24 [('1.3.6.1.4.1.1466.115.121.1.24', 'LDAP_SYNTAX', 'Generalized Time', 'RFC4517')]
        Optional in: krbPrincipalAux

So the ldap3 library returns it as a DateTime object (with time zone info)::

    >>> type(r[0].krblastpwdchange.value)
    <class 'datetime.datetime'>

.. warning::
   The ldap3 library returns dates with Time Zone info. These dates can be compared only with dates with Time Zone. You can't compare them
   with a "naive" date object.

.. note::
    Attributes have three properties for getting their values: the ``values`` property returns always a list containing all values, even in
    a single-valued attribute; the ``value`` property returns the very same list in a multi-valued attribute or the value in a single-valued attribute.
    ``raw_attributes`` always returns a list of the binary values received in the LDAP response. When the schema is available the ``values``
    and ``value`` properties are properly formatted as standard Python types. You can add additional custom formatters with the ``formatter``
    parameter of the Server object.

If you look at the raw data read from the server, you get the values actually stored in the DIT::

    >>> r[0].krblastpwdchange.raw_values
    [b'20161109050210Z']

Similar formatting is applied to other well-known attribute types, for example GUID or SID in Active Directory. Numbers are returned as ``int``::

    >>> e[0].krbloginfailedcount.value
    krbLoginFailedCount: 0
    >>> type(e[0].krbloginfailedcount.value)
    <class 'int'>
    >>> e[0].krbloginfailedcount.raw_values
    [b'0']

Search scope
------------
By default the Reader searches the whole sub tree starting from the specified base. If you want to search entries only in the base, you can pass the
``sub_tree=False`` parameter in the Reader definition. You can also override the default scope with the ``search_level()``, ``search_object()`` and
``search_subtree()`` methods of the Reader object::

    >>> r.search_level()  # search only at the 'dc=demo1,dc=freeipa,dc=org' context
    >>> print(len(r))  # the admin entry in in the cn=users,cn=account container, so no entry is found
    0
    >>> r.search_subtree()  # search walking down from the 'dc=demo1,dc=freeipa,dc=org' context
    >>> print(len(r))
    1

Matching entries in cursor results
----------------------------------
Once a cursor is populated with entries you can get a specific entry with the standard index feature of List object: ``r.entries[0]`` returns the first entry
found, ``r.entries[1]`` returns he second one and any subsequent entry is returned by the relevant index number. The Cursor object has a shortcut
for this operation: you can use ``r[0]``, ``r[1]`` (and so on) to perform the same operation. Furthermore, the Cursor object has an useful feature that helps you to
find a specific entry without knowing its index: when you use a string as the Cursor index the text will be searched in all entry DNs.
If only one entry matches it is returned, if more than one entry match the text a KeyError exception is raised. You can also use the ``r.match_dn(dn)``
method to return all entries with the specified text in the DN and ``r.match(attributes, value)`` to return all entries that contain the ``value`` in any
of the specified ``attributes`` where you can pass a single attribute name or a list of attribute names. When searching for values the either the formatted attribute
and the raw value are checked.
