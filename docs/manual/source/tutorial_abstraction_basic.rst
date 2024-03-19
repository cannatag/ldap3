Tutorial: ldap3 Abstraction Layer - Introduction
################################################

A more pythonic LDAP
====================

LDAP was developed in the late '70s when hosts were very expensive. Elaboration was slow and the protocol was developed
with the intent of shifting the burden of computing on the client side. So LDAP operations are crude and rough and clients
must perform a lot of pre-elaboration before sending their request to servers. This is quite different from what you would
expect from any modern API where you send requests to the server (maybe using simple JSON) without knowing almost anything
about how actually the elaboration is actually performed by the server.

.. note:: An example of this approach is the Search operation: one would expect that the filter string is simply sent to the
   server but, if you look at the ldap3 code for the Search operation you'll find a complete parser for the filter, that breaks
   the filter down to its elemental assertions and builds a recursive representation (similar to an AST, an *Abstract Syntax Tree*)
   of the filter. It's this representation that is sent to the server in a quite complex binary format (called ASN.1 *Abstract
   Syntax Notation.1*), not the text of the filter.

The ldap3 library includes an Abstraction Layer that lets you interact with the entries in the DIT in a *pythonic way*,
with a simple syntax and a consistent behaviour. The Abstraction Layer includes an ORM (Object Relational Mapping) that
links Entries (a standard Python class) to entries stored in the DIT. Each Entry object refers to an **ObjectDef** (object
class definition) made up of **AttrDef** (attribute type definition) that describes relations between the Attributes stored
in the Entry and the attribute values stored for that entry on the LDAP server. With the ORM you can perform all the usual
CRUD (Create, Read, Update, Delete) operations, move an entry or rename it. No coding of LDAP operation is required.

.. note:: In this tutorial we refer to Python objects with an uppercase leading character (Entry, Entries, Attribute, Attributes)
   words, while refer to objects on the LDAP server with lowercase words (entry, entries, attribute, attributes).
   Attributes of a generic Python object are referred to as 'property'.

With the Abstraction Layer you describe the structure of an LDAP entry and access the LDAP server via a standard Python
object, the **Cursor**, that reads and writes Entries from and to the DIT. Optionally you can use a Simplified Query Language
in place of the standard LDAP filter syntax.

There are two kinds of Cursor, **Reader** and **Writer**. This mitigates the risk of accidentally changing
data in applications that access LDAP only for reading, isolating the writing component: a Reader cursor can't write
to the DIT and a Writer cursor can't read data from it, Writer cursors are only used for modifying the DIT. So reading
and writing of data are strictly kept isolated.

Cursors contain Entries. An **Entry** is the Python representation of an entry stored in the LDAP DIT. There are two types of Entries,
**Read** and **Writable**. Each Entry has a status that identifies it's current state.

Entries are returned as the result of a LDAP Search operation or of a Reader search operation. Entries are made of Attributes.
An **Attribute** is stored in an internal dictionary with case insensitive access and a friendly key.
You can access Entry Attributes either as a dictionary or as properties: ``entry['CommonName']`` is the same of ``entry['Common
Name]``,``entry.CommonName``, ``entry.commonName`` and of ``entry.commonname`` (this feature is helpful when you work at the Python
command line; the Abstracton Layer also provides auto-completion of attribute names with the TAB key). Only Attributes of a Writable
Entry can be modified (they actually become WritableAttribute, with updating capability).

Modifications to a Writable Entry are kept in memory until the Entry changes are committed to the DIT. Changes can be discarded
before committed. Modifications are declared with the standard *augmented assignments* ``+=`` and ``-=`` or with explicit methods of the
WritableAttribute object as ``add()``, ``set()``, ``delete()`` and ``remove()``.

When creating Entries or assigning new Attribute values, new objects are flagged as **Virtual** until committed, to indicate that they
are still not present in the DIT.

Update operations can be applied to a single Entry or to the whole Entries collection of a Writer cursor.

Let's try the same operations we did in the previous chapters of this tutorial. Open the connection to the LDAP server as usual:

    >>> from ldap3 import Server, Connection, ObjectDef, AttrDef, Reader, Writer, ALL
    >>> server = Server('ipa.demo1.freeipa.org', get_info=ALL)
    >>> conn = Connection(server, 'uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org', 'Secret123', auto_bind=True)

Cursor and ObjectDef
--------------------
ldap3 must know the kind of entry (the LDAP object class) you want to work with to properly manage its attributes. You can take advantage
of the schema information read by the Server object and ask the ldap3 library to automatically build an ObjectDef. We can try for the
*person* object class, that represents a user in LDAP. The Abstraction Layer will walk up the schema up to the root class reading all
the mandatory and optional attributes in its hierarchy, building the AttrDefs collection::

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

As you can see *person* is a structural class and it's a subclass of the abstract *top* class in the LDAP schema hierarchy. For convenience,
mandatory (MUST) Attributes are listed separately from optional (MAY) Attributes because they are the attributes that must always be present
for the entry to be valid. You can also access the Attribute definitions as if they were standard properties of the ``obj_person`` object.

You can specify any additional auxiliary class with the ``auxiliary_class`` parameter of the ObjectClass or of the Cursor objects.

Entry status
------------
An Entry acquires a number of different statuses in its lifetime and moves from one status to another only when specific events occour.
The status of an Entry reflects it's internal state:

Entries created with a Reader cursor can have only one status:

* **Read**: the entry has been read from the DIT and converted to an Entry in the Entries collection.


A Writable Entry in a Writer cursor acquires the following statuses in its lifetime:

* **Writable**: the Entry has been created from a Read one, but no Attribute has been changed yet.

* **Pending changes**: some Attributes have been changed, but still not committed to the LDAP server.

* **Missing mandatory attributes**: some mandatory Attribute values are missing, the Entry cannot be committed.


There are three global events (delete, move, rename) that lock a Writable Entry until committed (or discarded). In this case the
status can be one of the following:

* **Ready for deletion**: Entry is flagged for deletion.

* **Ready for moving**: Entry is flagged for moving.

* **Ready for renaming**: Entry is flagged for renaming.


A new Entry, created in a Writer cursor can have the following status:

* **Virtual**: the Entry is new and still not present in the DIT.


After a commit a Writable Entry can be in one of this two statuses:

* **Committed**: changes have been written to the DIT.

* **Deleted**: the Entry has been removed from the DIT.

Note that in a Writable Entry pending changes can be discarded at any time. In this case the Entry status is set to Writable and the
original Attribute values are retained.

To get the status of an Entry use the ``get_status()`` method. You cannot directly change the status of an Entry, as it's updated according
to the operations performed.

When an Entry is in **Pending changes** status, new Attributes are flagged as Virtual until committed (or discarded).
