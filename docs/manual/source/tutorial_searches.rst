################################
Tutorial: searching LDAP entries
################################

.. warning:: **A more pythonic LDAP**: LDAP operations are clumsy and hard-to-use because reflect the old-age idea that most time-consuming operations
    should be done on the client to not clutter and hog the server with unneeded elaboration. ldap3 includes a fully functional **Abstraction
    Layer** that lets you interact with the DIT in a modern and *pythonic* way. With the Abstraction Layer you don't need to directly issue any
    LDAP operation at all.

Finding entries
===============

To find entries in the DIT you must use the **Search** operation. This operation has a number of parameters, but only two of them are mandatory:

* ``search_base``: the location in the DIT where the search will start
* ``search_filter``: a string that describes what you are searching

Search filters are based on assertions and look odd when you're unfamiliar with their syntax. One *assertion* is a bracketed expression
that affirms something about an attribute and its values, as ``(givenName=John)`` or ``(maxRetries>=10)``. Each assertion resolves
to True, False or Undefined (that is treated as False) for one or more entries in the DIT. Assertions can be grouped in boolean groups
where all assertions (**and** group, specified with ``&``) or at least one assertion (**or** group, specified with ``|``) must be True. A single
assertion can be negated (**not** group, specified with ``!``). Each group must be bracketed, allowing for recursive filters.
Operators allowed in an assertion are ``=`` (**equal**), ``<=`` (**less than or equal**), ``>=`` (**greater than or equal**), ``=*`` (**present**), ``~=``
(**aproximate**) and ``:=`` (**extensible**). Surprisingly the *less than* and the *greater than* operators don't exist in the LDAP filter syntax.
The *aproximate* and the *extensible* are someway obscure and seldom used. In an equality filter you can use the ``*`` character as a wildcard.

For example, to search for all users named John with an email ending with '@example.org' the filter will be ``(&(givenName=John)(mail=*@example.org))``,
to search for all users named John or Fred with an email ending in '@example.org' the filter will be
``(&(|(givenName=Fred)(givenName=John))(mail=*@example.org))``, while to search for all users that have a givenName different from Smith the filter
will be ``(!(givenName=Smith))``.

Long search filters can easily become hard to understand so it may be useful to divide the text on multiple indented lines::

    (&
        (|
            (givenName=Fred)
            (givenName=John)
        )
        (mail=*@example.org)
    )


Let's search all users in the FreeIPA demo LDAP server::

    >>> from ldap3 import Server, Connection, ALL
    >>> server = Server('ipa.demo1.freeipa.org', get_info=ALL)
    >>> conn = Connection(server, 'uid=admin, cn=users, cn=accounts, dc=demo1, dc=freeipa, dc=org', 'Secret123', auto_bind=True)
    >>> conn.search('dc=demo1, dc=freeipa, dc=org', '(objectclass=person)')
    True
    >>> conn.entries
    [DN: uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org
    , DN: uid=manager,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org
    , DN: uid=employee,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org
    , DN: uid=helpdesk,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org
    ]

Here you request all the entries of class *person*, starting from the *dc=demo1, dc=freeipa, dc=org* context with the default subtree scope.
You have not requested any attribute, so in the response we get only the Distinguished Name of the found entries.

.. note:: response vs result: in ldap3 every operation has a *result* that is stored in the ``result`` attribute of the Connection in sync strategies.
    Search operations store the entries found in the ``response`` attribute of the Connection object. For async strategies you must use the ``get_response(id)`` method
    that returns a tuple in the form of (response, result).

Now let's try to request some attributes from the admin user::

    >>> conn.search('dc=demo1, dc=freeipa, dc=org', '(&(objectclass=person)(uid=admin))', attributes=['sn', 'krbLastPwdChange', 'objectclass'])
    True
    >>> conn.entries[0]
    DN: uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org - STATUS: Read - READ TIME: 2016-10-09T20:39:32.711000
    krbLastPwdChange: 2016-10-09 10:01:18+00:00
    objectclass: top
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

.. note::
    When using attributes in a search filter it's a good habit to always request for the *structural class* of the objects you expect to retrieve.
    You cannot be sure that the attribute you're serching for is not used is some other object class, and even if you are sure that no other
    object class uses it this could always change in the future when someone extends the schema with an object class that uses that very
    same attribute, and your program suddenly breaks with no apparent reason.


Note that the ``entries`` attribute of the Connection object is derived from the ldap3 *Abstraction Layer* and it's specially crafted to be used in interactive mode
at the ``>>>`` prompt. It gives a visual representation of the entry data structure where each value is, according to the schema, properly formatted
(the date value in krbLastPwdChange is actually stored as ``b'20161009010118Z'``, but it's shown as a Python date object). Attributes can be queried
either as a class or a dict, with some additional features as case-insensitivity and blank-insensitivity. You can get the formatted
value and the raw value (the value actually returned by the server) in the ``values`` and ``raw_values`` attributes::

    >>> entry = entries[0]
    >>> entry.krbLastPwdChange
    krbLastPwdChange: 2016-10-09 10:01:18+00:00
    >>> entry.KRBLastPwdCHANGE
    krbLastPwdChange: 2016-10-09 10:01:18+00:00
    >>> entry['krbLastPwdChange']
    krbLastPwdChange: 2016-10-09 10:01:18+00:00
    >>> entry['KRB LAST PWD CHANGE']
    krbLastPwdChange 2016-10-09 10:01:18+00:00

    >>> entry.krbLastPwdChange.values
    [datetime.datetime(2016, 10, 9, 10, 1, 18, tzinfo=OffsetTzInfo(offset=0, name='UTC'))]
    >>> entry.krbLastPwdChange.raw_values
    [b'20161009010118Z']


Note that the entry status is *Read*. This is not relevant if you only need to retrive the entries from the DIT but it's vital if you want to take advantage
of the ldap3 Abstraction Layer making it *Writable* and change or delete its content via the Abstraction Layer. The Abstraction Layer also records the time
of the last data read operation for the entry.

In the previous search operations you specified ``dc=demo1, dc=freeipa, dc=org`` as the base of our search, but the entries we got back were in the
``cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org`` context of the DIT. So the server has, with no apparent reason, walked down every context under
the base applying the filter to each of the entries in the sub-containers. The server actually performed a *whole subtree* search. Other possible kinds
of searches are the *single level* search (that searches only in the level specified in the base) and the *base object* search (that searches only in the
attributes of the entry specified in the base). What changes in this different kinds of search is the 'breath' of the portion of the DIT that is searched.
This breath is called the **scope** of the search and can be specified with the ``search_scope`` parameter of the search operation. It can take three
different values: ``BASE``, ``LEVEL`` and ``SUBTREE``. The latter value is the default for the search opertion, so this clarifies why you got back all the
entries in the sub-containers of the base in previous searches.

You can have a LDIF representation of the response of a search with::

    >>> conn.entries[0].entry_to_ldif()
    version: 1
    dn: uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org
    objectclass: top
    objectclass: person
    objectclass: posixaccount
    objectclass: krbprincipalaux
    objectclass: krbticketpolicyaux
    objectclass: inetuser
    objectclass: ipaobject
    objectclass: ipasshuser
    objectclass: ipaSshGroupOfPubKeys
    krbLastPwdChange: 20161009010118Z
    sn: Administrator
    # total number of entries: 1

.. note:: LDIF
    LDIF stands for LDAP Data Interchange Format and is a textual standard used to describe two different aspects of LDAP: the content of an entry (**LDIF-CONTENT**)
    or the changes performed on an entry with an LDAP operation (**LDIF-CHANGE**). LDIF-CONTENT is used to describe LDAP entries in an stream (i.e. a file or a socket),
    while LDIF-CHANGE is used to describe the Add, Delete, Modify and ModifyDn operations.

    *These two formats have different purposes and cannot be mixed in the same stream.*

or you can save the response to a JSON string::

    >>> entry.entry_to_json()
    {
        "attributes": {
            "krbLastPwdChange": [
                "2016-10-09 10:01:18+00:00"
            ],
            "objectclass": [
                "top",
                "person",
                "posixaccount",
                "krbprincipalaux",
                "krbticketpolicyaux",
                "inetuser",
                "ipaobject",
                "ipasshuser",
                "ipaSshGroupOfPubKeys"
            ],
            "sn": [
                "Administrator"
            ]
        },
        "dn": "uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org"

Searching for binary values
===========================
To search for a binary value you must use the RFC4515 ASCII escape sequence for each unicode point in the search assertion. ldap3 provides the helper function
*escape_bytes(byte_value)* in ldap3.utils.conv to properly escape a byte sequence::

    >>> from ldap3.utils.conv import escape_bytes
    >>> unique_id = b'\xca@\xf2k\x1d\x86\xcaL\xb7\xa2\xca@\xf2k\x1d\x86'
    >>> search_filter = '(nsUniqueID=' + escape_bytes(unique_id) + ')'
    >>> conn.search('dc=demo1, dc=freeipa, dc=org', search_filter, attributes=['nsUniqueId'])

``search_filter`` will contain ``(guid=\\ca\\40\\f2\\6b\\1d\\86\\ca\\4c\\b7\\a2\\ca\\40\\f2\\6b\\1d\\86)``. The \xx escaping format is specific to the LDAP protocol.
