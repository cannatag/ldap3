#################################
Tutorial: ldap3 Abstraction Layer
#################################

A more pythonic LDAP
====================

LDAP was developed in the late '70s when hosts were very expensive. Elaboration was slow and so the LDAP protocol was developed
with the idea of shifting the burden of computing on the client side. So LDAP operations are crude and rough, and the client
must perform a lot of pre-elaboration before sending the request to the server. This is quite different from what you would
expect from any modern API where you send your request to the server withouth knowing almost anything about its internal work.

.. note:: An example of this approach is in the Search operation: one would expect that the filter string is parsed on the
server, instead any LDAP client must parse the filter, break it down to its elementary assertions and build a recursive
representation (similar to an AST) of the filter that is sent to the server in a quite complex binary format.

Following the KISS (Keep it simple stupid!) and the DRY (Don't repeat yourself) principles the ldap3 library includes an Abstraction Layer
that let you interact with the Entries in the DIT in a pythonic way, this means simple, consistent and easy to remember behaviour. Using the
Abstraction Layer you get an ORM (Object Relational Mapping) that links standard Python objects (Entry) to entries stored
in the DIT. Each Entry object refers to an Object Class Definition (ObjectDef) that describes the relation between the Attributes
stored in the Entry and the attributes values stored in the DIT for that entry. With the ORM you can perform all the CRUD
(Create, Read, Update, Delete) operations and can also move an entry or rename it without using LDAP at all.

.. note:: In this tutorial we refer to Python objects with an uppercase leading character (Entry, Entries, Attribute, Attributes)
word, while refer to objects on the LDAP server with lowercase words (entry, entries, attribute, attributes). An attribute of a generic Python
object is referred to as 'property'.

With the Abstraction Layer you describe LDAP entries as standard Python objects and access the LDAP server via a *Cursor* in a read-only
or read-write mode. Optionally you can use a Simplified Query Language instead of the standard LDAP filter syntax.

There are two kind of **Cursor** in the Abstraction Layer, **Reader** and **Writer**. This mitigates the risk of accidentally changing
values when you're just reading them when your application uses LDAP only for reading. A Writer cursor cannot read data
from the DIT as well, Writer cursors are only used for modifying the DIT. So reading and writing of data is kept strictly separated.

Cursors contains Entries. An **Entry** is the Python representation of an entry stored in the LDAP DIT. There are two types of Entries,
**Read** and **Writable**. Each Entry has a status that identify it's current state.

Entries are returned as the result of a LDAP Search operation or of a Reader search operation. Entries are made of Attributes.
An **Attribute** is stored in an internal dictionary with case insensitive access by the key defined in the Attribute definition.
You can access Entry Attributes either as a dictionary or as properties: ``entry['CommonName']`` is the same of ``entry.Common
Name``, of ``entry.CommonName``, of ``entry.commonName`` and of ``entry.commonname``. Only Attributes of a Writable Entry can be modified.

Modifications to a Writable Entry are kept in memory until the Entry changes are committed to the DIT. Changes can be discarded
before committed. Modification are declared with the standard *augmented assignments* ``+=`` and ``-=`` or with explicit methods of the
Attribute as ``add()``, ``set()``, ``delete()`` and ``remove()``.

When creating Entries or assigning new Attribute values the new generated objects are flagged ad **Virtual** to indicate that they
are still not present in the DIT.

Let's try the same operations we did in the previous chapters of this tutorial. First youmust open the
connection to the LDAP server as usual:

    >>> from ldap3 import Server, Connection, ObjectDef, AttrDef, Reader, Writer, ALL
    >>> server = Server('ipa.demo1.freeipa.org', get_info=ALL)
    >>> conn = Connection(server, 'uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org', 'Secret123', auto_bind=True)

Then you must define the kind of entry we want to work with. We can take advantage of the schema information read by
the Server object asking the ldap3 library to automatically build an ObjectDef for the *person* object class, walking up to the root
class and reading all the mandatory and optional attributes in the LDAP schema hierarchy::

    >>> obj_person = ObjectDef('person', conn)

The ``obj_person`` object now contains the definition of the LDAP *person* object class as an ObjectDef and includes its attributes
as a collection ofAttrDef::

    >>> obj_person
    OBJ : person [person OID: 2.5.6.6, top OID: 2.5.6.0]
    MUST: cn, objectClass, sn
    MAY : description, seeAlso, telephoneNumber, userPassword
    >>> obj_person.sn
    ATTR: sn - mandatory: True - single_value: False
      Attribute type: 2.5.4.4
        Short name: sn, surName
        Single value: False
        Superior: name
        Equality rule: caseIgnoreMatch
        Syntax: 1.3.6.1.4.1.1466.115.121.1.15 [('1.3.6.1.4.1.1466.115.121.1.15', 'LDAP_SYNTAX', 'Directory String', 'RFC4517')]
        Mandatory in: person
        Optional in: RFC822localPart, mozillaAbPersonAlpha
        Extensions:
          X-ORIGIN: RFC 4519
          X-DEPRECATED: surName
        OidInfo: ('2.5.4.4', 'ATTRIBUTE_TYPE', ['sn', 'surname'], 'RFC4519')

As you can see *person* is a subclass of *top* in the LDAP schema hierarchy. Mandatory (MUST) Attributes are listed separately
from optional (MAY) Attributes. You can also access the Attribute definitions (AttrDef) as if they were standard
properties of the ``obj_person`` object.

Let's now define a Reader cursor to get all the entries of class 'person' in the 'dc=demo1,dc=freeipa,dc=org' context::
    >>> r = Reader(conn, obj_person, None, 'dc=demo1,dc=freeipa,dc=org')
    >>> r
    CONN   : ldap://ipa.demo1.freeipa.org:389 - cleartext - user: uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org - not lazy - bound - open - <local: 10.3.9.227:2770 - remote: 209.132.178.99:389> - tls not started - listening - SyncStrategy - internal decoder
    BASE   : 'dc=demo1,dc=freeipa,dc=org' [SUB]
    DEFS   : ['person'] [cn, description, objectClass, seeAlso, sn, telephoneNumber, userPassword]
    ATTRS  : ['cn', 'description', 'objectClass', 'seeAlso', 'sn', 'telephoneNumber', 'userPassword']
    FILTER : '(objectClass=person)'

We didn't provide any filter, but the Reader automatically uses the ObjectDef class to read only entries of the requested objectclass.
Now you can ask the Reader to execute the search fetching the results in its ``entries`` property::

    >>> e = r.search()
    >>> r
    CONN   : ldap://ipa.demo1.freeipa.org:389 - cleartext - user: uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org - not lazy - bound - open - <local: 10.3.9.227:18059 - remote: 209.132.178.99:389> - tls not started - listening - SyncStrategy - internal decoder
    BASE   : 'dc=demo1,dc=freeipa,dc=org' [SUB]
    DEFS   : ['person'] [cn, description, objectClass, seeAlso, sn, telephoneNumber, userPassword]
    ATTRS  : ['cn', 'description', 'objectClass', 'seeAlso', 'sn', 'telephoneNumber', 'userPassword']
    FILTER : '(objectClass=person)'
    ENTRIES: 17 [SUB] [executed at: 2016-10-20T08:51:31.574345]

As you can see there are now a number of entries in the Reader. An Entry has some interesting features accessible from its properties
and methods. Because Attribute names are used as Entry class properties all the "operational" properties and methods of an Entry start
with the **entry_** prefix (the underscore is an invalid character in an attribute name). It's easy to get a useful representation of an Entry::

    >>> e[0]
    DN: uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org - STATUS: Read - READ TIME: 2016-10-20T08:51:31.574345
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

Let's explore some of them::

    >>> # get the DN of an entry
    >>> e[0].entry_dn
    'uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org'
    >>>
    >>> # query the attributes in the Entry as a list of names
    >>> e[0].entry_attributes
    >>>
    >>> # query the attributes in the Entry as a dict of key/value pairs
    >>> e[0].entry_attributes_as_dict
    {'cn': ['Administrator'], 'sn': ['Administrator'], 'userPassword': [], 'telephoneNumber': [], 'seeAlso': [], 'description': [], 'objectClass':
    ['top', 'person', 'posixaccount', 'krbprincipalaux', 'krbticketpolicyaux', 'inetuser', 'ipaobject', 'ipasshuser', 'ipaSshGroupOfPubKeys', 'ipaNTUserAttrs']}
    >>> # let's check which attributes are mandatory
    >>> e[0].entry_mandatory_attributes
    ['cn', 'sn', 'objectClass']
    >>>
    >>> convert the Entry to LDIF
    >>> print(e[0].entry_to_ldif())
    version: 1
    dn: uid=manager,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org
    objectClass: top
    objectClass: person
    objectClass: organizationalperson
    objectClass: inetorgperson
    objectClass: inetuser
    objectClass: posixaccount
    objectClass: krbprincipalaux
    objectClass: krbticketpolicyaux
    objectClass: ipaobject
    objectClass: ipasshuser
    objectClass: ipaSshGroupOfPubKeys
    objectClass: mepOriginEntry
    objectClass: ipantuserattrs
    objectClass: ipauserauthtypeclass
    mail: manager@demo1.freeipa.org
    uid: manager
    sn: Manager
    displayName: Test Manager
    cn: Test Manager
    initials: TM
    givenName: Test
    # total number of entries: 1
    >>>
    >>> print(e[0].entry_to_json(include_empty=False))  # Use include_empty=True to include empty attributes
    {
        "attributes": {
            "cn": [
                "Administrator"
            ],
            "objectClass": [
                "top",
                "person",
                "posixaccount",
                "krbprincipalaux",
                "krbticketpolicyaux",
                "inetuser",
                "ipaobject",
                "ipasshuser",
                "ipaSshGroupOfPubKeys",
                "ipaNTUserAttrs"
            ],
            "sn": [
                "Administrator"
            ]
        },
        "dn": "uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org"
    }

You can see that this Entry has additional auxiliary object classes attached. This means that there can be other attributes stored in the entry. Let's try
to define an ObjectDef that also requests the 'krbprincipalaux'::

    >>> obj_person = ObjectDef(['person', 'krbprincipalaux'], conn)
    OBJ : person, krbPrincipalAux [person OID: 2.5.6.6, top OID: 2.5.6.0, krbPrincipalAux OID: 2.16.840.1.113719.1.301.6.8.1]
    MUST: cn, objectClass, sn
    MAY : description, krbAllowedToDelegateTo, krbCanonicalName, krbExtraData, krbLastAdminUnlock, krbLastFailedAuth, krbLastPwdChange,
    krbLastSuccessfulAuth, krbLoginFailedCount, krbPasswordExpiration, krbPrincipalAliases, krbPrincipalAuthInd, krbPrincipalExpiration, krbPrincipalKey,
    krbPrincipalName, krbPrincipalType, krbPwdHistory, krbPwdPolicyReference, krbTicketPolicyReference, krbUPEnabled, seeAlso, telephoneNumber, userPassword

As you can see the ObjectDef now includes all Attributes from both classes. To see the additional data try to refresh the Reader::

    >>> e = r.search()
    >>> e[0]
    DN: uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org - STATUS: Read - READ TIME: 2016-10-20T16:22:11.095592
        cn: Administrator
        krbExtraData: b'\x00\x02t[\xffWroot/admin@DEMO1.FREEIPA.ORG\x00'
        krbLastFailedAuth: 2016-10-20 10:26:57+00:00
        krbLastPwdChange: 2016-10-13 10:01:24+00:00
        krbLastSuccessfulAuth: 2016-10-20 14:06:29+00:00
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
