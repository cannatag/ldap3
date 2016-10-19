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
word, while refer to objects on the LDAP server with lowercase words (entry, entries, attribute, attributes).

With the Abstraction Layer you describe LDAP entries as standard Python objects and access the LDAP server via a *Cursor* in a read-only
or read-write mode. Optionally you can use a Simplified Query Language instead of the standard LDAP filter syntax.

There are two kind of **Cursor** in the Abstraction Layer, **Reader** and **Writer**. This mitigates the risk of accidentally changing
values when you're just reading them when your application uses LDAP only for reading. A Writer cursor cannot read data
from the DIT as well, Writer cursors are only used for modifying the DIT. So reading and writing of data is kept strictly separated.

Cursors contains Entries. An **Entry** is the Python representation of an entry stored in the LDAP DIT. There are two types of Entries,
**Read** and **Writable**. Each Entry has a status that identify it's current state.

Entries are returned as the result of a LDAP Search operation or of a Reader search operation. Entries are made of Attributes.
An **Attribute** is stored in an internal dictionary with case insensitive access by the key defined in the Attribute definition.
You can access Entry attributes either as a dictionary or as properties: ``entry['CommonName']`` is the same of ``entry.Common
Name``, of ``entry.CommonName``, of ``entry.commonName`` and of ``entry.commonname``. Only attributes of a Writable Entry can be modified.

Modifications to a Writable Entry are kept in memory until the Entry changes are committed to the DIT. Changes can be discarded
before committed. Modification are declared with the standard *augmented assignments* ``+=`` and ``-=`` or with explicit methods of the
Attribute as ``add()``, ``set()``, ``delete()`` and ``remove()``.

When creating new Entries or assigning new Attribute values the new generated objects are flagged ad **Virtual** to indicate that they
are still not present in the DIT.

Because Attribute names are used as Entry class attributes all the "operational" attributes and methods of an Entry start with the **entry_**
prefix.

Let's try the same operations we did in the previous chapters of this tutorial. First youmust open the
connection to the LDAP server as usual:

    >>> from ldap3 import Server, Connection, ObjectDef, AttrDef, Reader, Writer, ALL
    >>> server = Server('ipa.demo1.freeipa.org', get_info=ALL)
    >>> conn = Connection(server, 'uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org', 'Secret123', auto_bind=True)

Then you must define the kind of entry we want to work with. We can take advantage of the schema information read by
the Server object asking the ldap3 library to automatically build an ObjectDef for the *person* object class, walking up to the root
object class and reading all the mandatory and optional attributes in the LDAP schema hiearchy::

    >>> obj_person = ObjectDef('person', conn)

The ``obj_person`` object now contains the definition of the LDAP *person* object class, including its attributes::

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
attributes of the ``obj_person`` object.


Let's now define a Reader cursor to get all the entries of class 'person' in the 'dc=demo1,dc=freeipa,dc=org' context::
    >>> r = Reader(conn, obj_person, None, 'dc=demo1,dc=freeipa,dc=org')
    >>> r
    CONN   : ldap://ipa.demo1.freeipa.org:389 - cleartext - user: uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org - not lazy - bound - open - <local: 10.3.9.227:2770 - remote: 209.132.178.99:389> - tls not started - listening - SyncStrategy - internal decoder
    BASE   : 'dc=demo1,dc=freeipa,dc=org' [SUB]
    DEFS   : ['person'] [cn, description, objectClass, seeAlso, sn, telephoneNumber, userPassword]
    ATTRS  : ['cn', 'description', 'objectClass', 'seeAlso', 'sn', 'telephoneNumber', 'userPassword']
    FILTER : '(objectClass=person)'

Now you can ask the Reader to execute the search fetching the results in its ``entries`` attribute::

    >>> r.search()
    [DN: uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org - STATUS: Read - READ TIME: 2016-10-19T19:50:37.519775
        cn: Administrator
        objectClass: top, person
                     posixaccount
                     krbprincipalaux
                     krbticketpolicyaux
                     inetuser
                     ipaobject
                     ipasshuser
                     ipaSshGroupOfPubKeys
                     ipaNTUserAttrs
        sn: Administrator
    , DN: uid=manager,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org - STATUS: Read - READ TIME: 2016-10-19T19:50:37.519775
        cn: Test Manager
        objectClass: top
                     person
                     organizationalperson
                     inetorgperson
                     inetuser
                     posixaccount
                     krbprincipalaux
                     krbticketpolicyaux
                     ipaobject
                     ipasshuser
                     ipaSshGroupOfPubKeys
                     mepOriginEntry
                     ipantuserattrs
                     ipauserauthtypeclass
        sn: Manager
    , DN: uid=employee,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org - STATUS: Read - READ TIME: 2016-10-19T19:50:37.519775
        cn: Test Employee
        objectClass: top
                     person
                     organizationalperson
                     inetorgperson
                     inetuser
                     posixaccount
                     krbprincipalaux
                     krbticketpolicyaux
                     ipaobject
                     ipasshuser
                     ipaSshGroupOfPubKeys
                     mepOriginEntry
                     ipantuserattrs
        sn: Employee
        telephoneNumber: 123456
                         7890
    ]

The ``search()`` method set the ``entries`` attribute of the Reader to the collection of Entries found in the search. Here you also get them
printed because of the interactive Python console.
