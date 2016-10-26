Tutorial: ldap3 Abstraction Layer - Reading data
################################################

Reading entries
---------------

Let's define a Reader cursor to get all the entries of class 'inetOrgPerson' in the 'ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org' context::

    >>> r = Reader(conn, obj_person, None, 'ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org')
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
    CONN   : ldap://ipa.demo1.freeipa.org:389 - cleartext - user: uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org - not lazy - bound - open - <local: 10.3.9.227:17296 - remote: 209.132.178.99:389> - tls not started - listening - SyncStrategy - internal decoder
    DEFS   : ['inetOrgPerson'] [audio, businessCategory, carLicense, cn, departmentNumber, description, destinationIndicator, displayName, employeeNumber, employeeType, facsimileTelephoneNumber, givenName, homePhone, homePostalAddress, initials, internationalISDNNumber, jpegPhoto, l, labeledURI, mail, manager, mobile, o, objectClass, ou, pager, photo, physicalDeliveryOfficeName, postOfficeBox, postalAddress, postalCode, preferredDeliveryMethod, preferredLanguage, registeredAddress, roomNumber, secretary, seeAlso, sn, st, street, telephoneNumber, teletexTerminalIdentifier, telexNumber, title, uid, userCertificate, userPKCS12, userPassword, userSMIMECertificate, x121Address, x500UniqueIdentifier]
    ATTRS  : ['audio', 'businessCategory', 'carLicense', 'cn', 'departmentNumber', 'description', 'destinationIndicator', 'displayName', 'employeeNumber', 'employeeType', 'facsimileTelephoneNumber', 'givenName', 'homePhone', 'homePostalAddress', 'initials', 'internationalISDNNumber', 'jpegPhoto', 'l', 'labeledURI', 'mail', 'manager', 'mobile', 'o', 'objectClass', 'ou', 'pager', 'photo', 'physicalDeliveryOfficeName', 'postOfficeBox', 'postalAddress', 'postalCode', 'preferredDeliveryMethod', 'preferredLanguage', 'registeredAddress', 'roomNumber', 'secretary', 'seeAlso', 'sn', 'st', 'street', 'telephoneNumber', 'teletexTerminalIdentifier', 'telexNumber', 'title', 'uid', 'userCertificate', 'userPKCS12', 'userPassword', 'userSMIMECertificate', 'x121Address', 'x500UniqueIdentifier']
    BASE   : 'ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org' [SUB]
    FILTER : '(objectClass=inetOrgPerson)'
    ENTRIES: 3 [executed at: 2016-10-26T09:26:41.698313]

There are now three Entries in the Reader. An Entry has some interesting features accessible from its properties and methods. Because
Attribute names are used as Entry properties all the "operational" properties and methods of an Entry start with the **entry_** prefix
(the underscore is an invalid character in an attribute name, so there can't be an attribute with that name). It's easy to get a useful
representation of an Entry::

    >>> r[0]
    DN: cn=b.young,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org - STATUS: Read - READ TIME: 2016-10-26T09:26:41.691314
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

    >>> # query the attributes in the Entry as a dict of key/value pairs
    >>> r[0].entry_attributes_as_dict
    {'cn': ['Administrator'], 'sn': ['Administrator'], 'userPassword': [], 'telephoneNumber': [], 'seeAlso': [], 'description': [], 'objectClass':
    ['top', 'person', 'posixaccount', 'krbprincipalaux', 'krbticketpolicyaux', 'inetuser', 'ipaobject', 'ipasshuser', 'ipaSshGroupOfPubKeys', 'ipaNTUserAttrs']}

    >>> # let's check which attributes are mandatory
    >>> r[0].entry_mandatory_attributes
    ['cn', 'sn', 'objectClass']

    >>> convert the Entry to LDIF
    >>> print(r[0].entry_to_ldif())
    version: 1
    dn: cn=b.young,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org
    objectClass: top
    objectClass: person
    objectClass: organizationalPerson
    objectClass: inetOrgPerson
    sn: Young
    cn: b.young
    # total number of entries: 1

    >>> print(r[0].entry_to_json(include_empty=False))  # Use include_empty=True to include empty attributes
    {
        "attributes": {
            "cn": [
                "b.young"
            ],
            "objectClass": [
                "top",
                "person",
                "organizationalPerson",
                "inetOrgPerson"
            ],
            "sn": [
                "Young"
            ]
        },
        "dn": "cn=b.young,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org"
    }

As you can see this Entry has additional auxiliary object classes attached. This means that there can be other attributes stored in the entry. Let's try
to define an ObjectDef that also requests the 'krbprincipalaux'::

    >>> obj_person = ObjectDef(['person', 'krbprincipalaux'], conn)
    OBJ : person, krbPrincipalAux [person (Structural) 2.5.6.6, top (Abstract) 2.5.6.0, krbPrincipalAux (Auxiliary) 2.16.840.1.113719.1.301.6.8.1]
    MUST: cn, objectClass, sn
    MAY : description, krbAllowedToDelegateTo, krbCanonicalName, krbExtraData, krbLastAdminUnlock, krbLastFailedAuth, krbLastPwdChange, krbLastSuccessfulAuth,
    krbLoginFailedCount, krbPasswordExpiration, krbPrincipalAliases, krbPrincipalAuthInd, krbPrincipalExpiration, krbPrincipalKey, krbPrincipalName, krbPrincipalType,
     krbPwdHistory, krbPwdPolicyReference, krbTicketPolicyReference, krbUPEnabled, seeAlso, telephoneNumber, userPassword

As you can see the ObjectDef now includes all Attributes from the *person*, *top* and *krbPrincipalAux* classes. Now create a new Reader::

    >>> r = Reader(conn, obj_person, None, 'dc=demo1,dc=freeipa,dc=org')
    >>> e = r.search()
    >>> e[0]
    DN: uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org - STATUS: Read - READ TIME: 2016-10-20T20:40:50.735314
        cn: Administrator
        krbExtraData: b'\x00\x02t[\xffWroot/admin@DEMO1.FREEIPA.ORG\x00'
        krbLastFailedAuth: 2016-10-20 10:26:57+00:00
        krbLastPwdChange: 2016-10-13 10:01:24+00:00
        krbLastSuccessfulAuth: 2016-10-20 18:33:16+00:00
        krbLoginFailedCount: 0
        krbPasswordExpiration: 2017-10-13 10:01:24+00:00
        krbPrincipalName: admin@DEMO1.FREEIPA.ORG
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

    >>> type(e[0].krblastpwdchange.value)
    <class 'datetime.datetime'>

.. note::
    Attributes have three properties for getting their value: the ``values`` property returns always a list containing all values (even in
    a single-valued attribute; ``value`` returns the same list in a multi-valued attribute and the value in a single-valued attribute.
    ``raw_attributes`` always returns a list of the binary values received in the LDAP response. When the schema is available the ``values``
    and ``value`` properties are properly formatted as standard Python types. You can add additional custom formatters with the ``formatter``
    parameter of the Server object.

If you look at the raw data read from the server, you get the values actually stored in the DIT::

    >>> e[0].krblastpwdchange.raw_values
    [b'20161013100124Z']

Similar formatting is applied to other well-known attribute types, for example GUID or SID in Active Directory. Numbers are returned as ``int``::

    >>> e[0].krbloginfailedcount.value
    krbLoginFailedCount: 0
    >>> type(e[0].krbloginfailedcount.value)
    <class 'int'>
    >>> e[0].krbloginfailedcount.raw_values
    [b'0']

Search scope
------------
By default the Reader searchs the whole sub tree starting from the specified base. If you want to search entries only in the base, you can pass the
``sub_tree=False`` parameter in the Reader definition. You can also override the default scope with the ``search_level()``, ``search_object()`` and
``search_subtree()`` methods of the Reader object::

    >>> r.search_level()  # search only at the 'dc=demo1,dc=freeipa,dc=org' context
    >>> print(len(r))
    8
    >>> r.search_subtree()  # search walking down from the 'dc=demo1,dc=freeipa,dc=org' context
    >>> print(len(r))
    20


