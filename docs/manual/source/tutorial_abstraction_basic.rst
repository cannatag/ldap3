Tutorial: ldap3 Abstraction Layer - Introduction
################################################

A more pythonic LDAP
====================

LDAP was developed in the late '70s when hosts were very expensive. Elaboration was slow and the LDAP protocol was developed
with the idea of shifting the burden of computing on the client side. So LDAP operations are crude and rough, clients
must perform a lot of pre-elaboration before sending the request to servers. This is quite different from what you would
expect from any modern API where you send your request to the server (maybe using simple JSON) withouth knowing almost anything
about how actually the work is internally done in the server.

.. note:: An example of this approach is the Search operation: one would expect that the filter string is parsed on the
server but, if you look at the ldap3 code for the Search operation you'll find a complete parser for the filter, that breaks
it down to its elementary assertions and builds a recursive representation (similar to an AST) of the filter. It's this representation
that is sent to the server in a quite complex binary format, not the simple text of the filter.

The ldap3 library includes an Abstraction Layer that lets you interact with the entries in the DIT in a pythonic way, with simple,
consistent and easy-to-remember behaviour. With the Abstraction Layer you get an ORM (Object Relational Mapping) that links
standard Python objects to entries stored in the DIT. Each Entry object refers to an **ObjectDef** (object class definition) made up of
one or more **AttrDef** (attribute type definition) that describes the relation between the Attributes stored in the Entry and the
attributes values stored for that entry on the LDAP server. With the ORM you can perform all the usual CRUD (Create, Read, Update,
Delete) operations and also you can move an entry or rename it. No coding of LDAP operation is actually required.

.. note:: In this tutorial we refer to Python objects with an uppercase leading character (Entry, Entries, Attribute, Attributes)
words, while refer to objects on the LDAP server with lowercase words (entry, entries, attribute, attributes). Attributes of a generic Python
object are referred to as 'property'.

With the Abstraction Layer you describe LDAP entries and access the LDAP server via a standard Python object: the **Cursor** that
reads and writes Entries from/to the DIT. Optionally you can use a Simplified Query Language instead of the standard LDAP filter syntax.

There are two kinds of Cursor in the Abstraction Layer, **Reader** and **Writer**. This mitigates the risk of accidentally changing
data in applications that use LDAP only for reading. A Writer cursor cannot read data from the DIT as well, Writer cursors
are only used for modifying the DIT. So reading and writing of data is kept strictly separated.

Cursors contains Entries. An **Entry** is the Python representation of an entry stored in the LDAP DIT. There are two types of Entries,
**Read** and **Writable**. Each Entry has a status that identify it's current state.

Entries are returned as the result of a LDAP Search operation or of a Reader search operation. Entries are made of Attributes.
An **Attribute** is stored in an internal dictionary with case insensitive access with a friendly key defined in the Attribute definition.
You can access Entry Attributes either as a dictionary or as properties: ``entry['CommonName']`` is the same as ``entry.Common
Name``, as ``entry.CommonName``, as ``entry.commonName`` and of ``entry.commonname``. Only Attributes of a Writable Entry can be modified
(are automatically subclassed to WritableAttribute).

Modifications to a Writable Entry are kept in memory until the Entry changes are committed to the DIT. Changes can be discarded
before committed. Modifications are declared with the standard *augmented assignments* ``+=`` and ``-=`` or with explicit methods of the
WritableAttribute object as ``add()``, ``set()``, ``delete()`` and ``remove()``.

When creating Entries or assigning new Attribute values new objects are flagged as **Virtual** until committed, to indicate that they
are still not present in the DIT.

Let's try the same operations we did in the previous chapters of this tutorial. First you must open the connection to the LDAP server as usual:

    >>> from ldap3 import Server, Connection, ObjectDef, AttrDef, Reader, Writer, ALL
    >>> server = Server('ipa.demo1.freeipa.org', get_info=ALL)
    >>> conn = Connection(server, 'uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org', 'Secret123', auto_bind=True)

Cursor and ObjectDef
--------------------
ldap3 must know the kind of entry (the LDAP object class) you want to work with to properly manage its data. You can take advantage
of the schema information read by the Server object and ask the ldap3 library to automatically build an ObjectDef for the *person* object
class. The Abstraction Layer will walk up the schema up to the root class reading all the mandatory and optional attributes in the hierarchy,
building its AttrDefs collection::

    >>> obj_person = ObjectDef('person', conn)

The ``obj_person`` object now contains the definition of the LDAP *person* object class as an ObjectDef and includes its attributes
as a collection of AttrDef::

    >>> obj_person
    OBJ : person [person (Structural) 2.5.6.6, top (Abstract) 2.5.6.0]
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

As you can see *person* is a structural subclass of the abstract *top* class in the LDAP schema hierarchy. For convenience mandatory (MUST) Attributes are listed separately
from optional (MAY) Attributes because are the attributes that must always be present in the entry. You can also access the Attribute definitions as if they
were standard properties of the ``obj_person`` object.
