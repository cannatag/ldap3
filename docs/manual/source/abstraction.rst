#################
Abstraction Layer
#################

**A more pythonic LDAP**: LDAP operations look clumsy and hard-to-use because they reflect the old-age idea that time-consuming operations
should be done on the client to not clutter and hog the server with unneeded elaboration. ldap3 includes a fully functional **Abstraction
Layer** that lets you interact with the DIT in a modern and *pythonic* way. With the Abstraction Layer you don't need to directly issue any
LDAP operation at all.

Overview
--------

With the Abstraction Layer you describe LDAP objects using the ObjectDef and AttrDef classes and access the LDAP server  via a *Cursor* in read-only
or read-write mode. Optionally you can use a Simplified Query Language to read the Entries from the DIT.

All classes can be imported from the ldap3 package::

    from ldap3 import ObjectDef, AttrDef, Reader, Writer, Entry, Attribute, OperationalAttribute

The Abstraction Layer relies on a simple **ORM** (Object Relational Mapping) that links Entries object to entries stored in the LDAP. Each Entry
object refers to an ObjectDef that describes the relation between the Attributes stored in the Entry and the attributes stored in the DIT.

ObjectDef class
---------------

The ObjectDef class is used to define an abstract Entry object. You can create ObjectDefs manually, defining each Attribute defininition (AttrDef)
or in an automatic way with the information read from the schema.

To automatically create an ObjectDef just use the following code on an open connection where the schema has been read by the server::

    >>> person = ObjectDef(['inetOrgPerson'], connection)
    >>> person
    OBJ: inetOrgPerson [inetOrgPerson OID: 2.16.840.1.113730.3.2.2, organizationalPerson OID: 2.5.6.7, person OID: 2.5.6.6, top OID: 2.5.6.0]
    ATTRS: audio, businessCategory, carLicense, cn, departmentNumber, description, destinationIndicator, displayName, employeeNumber, employeeType,
    facsimileTelephoneNumber, givenName, homePhone, homePostalAddress, initials, internationalISDNNumber, jpegPhoto, l, labeledURI, mail, manager,
    mobile, o, objectClass, ou, pager, photo, physicalDeliveryOfficeName, postOfficeBox, postalAddress, postalCode, preferredDeliveryMethod,
    preferredLanguage, registeredAddress, roomNumber, secretary, seeAlso, sn, st, street, telephoneNumber, teletexTerminalIdentifier, telexNumber,
    title, uid, userCertificate, userPKCS12, userPassword, userSMIMECertificate, x121Address, x500UniqueIdentifier

As you can see the *person* object has been populated with all attributes from the hierarchy of classes starting from *inetOrgPerson* up to *top*.
For each attribute you get additional information useful to interact with it::

    >>> person.sn
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

When manually creating a new ObjectDef instance you can specify the LDAP class(es) of the entries you will get back in a search.
The object class(es) will be automatically added to the query filter::

    person = ObjectDef('inetOrgPerson')
    engineer = ObjectDef(['inetOrgPerson', 'auxEngineer'])

Once you have defined an ObjectDef instance you can add the attributes definition with the ``add()`` method of ObjectDef. You can also use
the ``+=`` operator as a shortcut. AttrDef(s) can be removed with the ``remove()`` method or using the ``-=`` operator.

ObjectDef is an iterable that returns each AttrDef object (the whole AttrDef object, not only the key).
AttrDefs can be accessed either as a dictionary or as a property, spaces are removed and keys are not case sensitive::

    cn_attr_def = person['Common Name']
    cn_attr_def = person['commonName']  # same as above
    cn_attr_def = person.CommonName  # same as above

This eases the use at the interactive ``>>>`` prompt where you don't have to remember the case of the attribute name.
*Autocompletion feature* is enabled, so you can get a list of all defined attributes as property just pressing TAB at the interactive prompt.

Each class has a useful representation that summarize the instance status. You can access it directly at the interactive prompt,
or in a program with the str() function.

AttrDef class
-------------

The AttrDef class is used to define an abstract LDAP attribute. If you use the automatic ObjectDef creation the relevant AttrDefs
are automatically created. AttrDef has a single mandatory parameter, the attribute name, and a number of optional parameters.
The optional ``key`` parameter defines a friendly name to use while accessing the attribute. The ``description`` parameter can
be used for storing additional information on the Attribute. When defining only the attribute name
you can add it directly to the ObjectDef (the AttrDef is automatically defined)::

    cn_attribute = AttrDef('cn, description='This is the internal account name')
    person.add(cn_attribute)

    person += AttrDef('cn', description='This is the internal account name')  # same as above
    person += 'cn'  # same as above, without description

You can even add a list of attrDefs or attribute names to an ObjectDef::

    person += [AttrDef('cn', key = 'Common Name'), AttrDef('sn', key = 'Surname')]
    person += ['cn', 'sn']  # as above, but keys are the attribute names

Validation
^^^^^^^^^^

You can specify a ``validate`` parameter to check if the attribute value is valid.
Two parameters are passed to the callable, the AttrDef.key and the value. The callable must return a boolean allowing or denying the validation::

    deps = {'A': 'Accounting', 'F': 'Finance', 'E': 'Engineering'}
    # checks that the parameter in query is in a specific range
    valid_department = lambda attr, value: True if value in deps.values() else False
    person += AttrDef('employeeType', key = 'Department', validate = validDepartment)

In this example the Cursor object will raise an exception if values for the 'Department' are not 'Accounting', 'Finance' or 'Engineering'.

Pre Query transformation
^^^^^^^^^^^^^^^^^^^^^^^^

A ``pre_query`` parameter indicates a callable used to perform a transformation on the value to be searched for the attribute defined::

    # transform value to be search
    def get_department_code(attr, value):
        for dep in deps.items():
            if dep[1] == value:
                return dep[0]
        return 'not a department'

    person += AttrDef('employeeType', key = 'Department', pre_query = get_department_code)

When you perform a search with 'Accounting', 'Finance' or 'Engineering' for the Department key, the real search will
be for employeeType = 'A', 'F' or 'E'.

Post query transformation
^^^^^^^^^^^^^^^^^^^^^^^^^

A 'post_query' parameter indicates a callable to perform a transformation on the returned value::

    get_department_name = lambda attr, value: deps.get(value, 'not a department') if attr == 'Department' else value
    person += AttrDef('employeeType', key = 'Department', post_query = get_department_name)

When you have an 'A', an 'F', or an 'E' in the employeeType attribute you get 'Accounting', 'Finance' or 'Engineering' in the 'Department' property
of the Person entry.

With a multivalue attribute post_query receives a list of all values in the attribute. You can return an equivalent list or a single string.

Dereferencing DNs
^^^^^^^^^^^^^^^^^

With ``dereference_dn`` you can establish a relation between different ObjectDefs. When dereference_dn is set to an ObjectDef the Cursor
reads the attribute and use its value as a DN for an object to be searched (using a temporary Reader) with the specified ObjectDef
in the same Connection. The result of the second search is returned as value of the first search::

    department = ObjectDef('groupOfNames')
    department += 'cn'
    department += AttrDef('member', key = 'employeer', dereference_dn = person)  # values of 'employeer' will be the 'Person' entries members of the found department


Cursor
------

There are two kind of *Cursor* in the Abstraction Layer, **Reader** and **Writer**. This helps to avoid the risk of accidentally change a value when you're
just reading them. The idea is that many application uses LDAP in a read-only mode, so having a read-only Cursor eliminates the risk of
accidentally change or remove an entry. You can use a Writer cursor only when you need to modify the DIT. You can even get a Writer cursor
from a Reader one, or get a temporary Writer cursor for a specific Entry returned by a Search operation.

Reader
------

Once you have defined the ObjectDef(s) and the AttrDef(s) you can instance a Reader for the ObjectDef. With it you can perform searches
using a standard LDAP filter or a simplified query language (explained in next paragraph). To execute a different search
the reader can be reset to its initial status with the ``reset()`` method.

A Reader cursor has the following attributes:

- connection: the connection to use.

- definition: the ObjectDef used by the Reader instance.

- query: the simplified query. It can be a standard LDAP filter (see next paragraph).

- base: the DIT base where to start the search.

- components_in_and: defines if the query components are in AND (True, default) or in OR (False).

- sub_tree: specifies if the search must be performed through the whole subtree (True, default) or only in the specified base (False).

- get_operational_attributes: specifies if the search must return the operational attributes (True) of found entries. Defaults to False.

- controls: optional controls to use in the search operation.

- attributes: the list of the attributes requested

- execution_time: the last time the query has run

- schema: the server schema, if any

- entries: the Entries returned by the Search operation


To perform a search Operation you can use any of the following methods:

- search(): standard search.

- search_level(): force a Level search.

- search_subtree(): force a whole sub-tree search, starting from 'base'.

- search_object(): force a object search, DN to search must be specified in 'base'.

- search_size_limit(limit): search with a size limit of 'limit'.

- search_time_limit(limit): search with a time limit of 'limit'.

- search_types_only(): standard search but the response will not contain any value.

- search_paged(page_size, criticality): perform a paged search, with 'page_size' number of entries for each call to this method. If 'criticality' is True the server aborts the operation if the Simple Paged Search extension is not available, else return the whole result set.

Example::

    s = Server('server')
    c = Connection(s, user = 'username', password = 'password')
    query = 'Department: Accounting'  # explained in next paragraph
    person_reader = Reader(c, person, query, 'o=test')
    person_reader.search()

The result of the search will be found in the ``entries`` property of the ``person_reader`` object.

A Reader object is an iterable that returns the entries found in the last search performed. It also has a useful representation that
summarize the Reader configuration and status::

    print(personReader)
    CONN   : ldap://server:389 - cleartext - user: cn=admin,o=test - version 3 - unbound - closed - not listening - SyncWaitStrategy
    BASE   : 'o=test' [SUB]
    DEFS   : 'inetOrgPerson' [CommonName <cn>, Department <employeeType>, Surname <sn>]
    QUERY  : 'Common Name :test-add*, surname:=t*' [AND]
    PARSED : 'CommonName: =test-add*, Surname: =t*' [AND]
    ATTRS  : ['cn', 'employeeType', 'sn', '+'] [OPERATIONAL]
    FILTER : '(&(objectClass=inetOrgPerson)(cn=test-add*)(sn=t*))'
    ENTRIES: 1 [SUB] [executed at: Sun Feb  9 20:43:47 2014]


Writer Cursor
-------------

By design a Writer Cursor has no Search capability because it can be only used to create new Entries or to modify the Entries in a Reader
cursor or in an LDAP Search operation.

Instead of the search_* methods the Writer has the following methods:

- from_cursor: creates a Writer cursor from a Reader cursor, populated with a copy of the Entries in the Reader cursor

- from_response: create a Writer cursor from a Search operation response, populated with a copy of the Entries in the Search response

- commit: writes all the pending changes to the DIT

- discard: discards all the pending changes

- new: creates a new Entry

- refresh_entry: re-reads the Entry from the DIT


Simplified Query Language
-------------------------

In the Reader you can express the query filter using the standard LDAP filter syntax or using a *Simplified Query Language* that resembles
a dictionary structure. If you use the standard LDAP filter syntax you must use the real attribute names because the filter is directly
passed to the Search operation.

The Simplified Query Language filter is a string of key-values couples separated with a ',' (comma), in each of the couples the left
part is the attribute key defined in an AttrDef object while the right part is the value (or values) to be searched. Parts are separed
with a ':' (colon). Keys can be prefixed with a '&' (AND) or a '|' (OR) for searching all the values or at least one of them. Values
can be prefixed with an optional exclamation mark '!' (NOT) for negating the search followed by the needed search operator
('=', '<', '>', '~'). The default operator is '=' and can be omitted. Multiple values are separated by a ';' (semi-colon).

A few examples::

    'CommonName: bob' -> (cn=bob)
    'CommonName: bob; john; michael' -> (|(cn=bob)(cn=john)(cn=michael))
    'Age: > 21' -> (age>=21)
    '&Age: > 21; < 65' ->&(age<=65)(age>=21))
    'Department: != Accounting'' -> (!(EmployeeType=A))
    '|Department:Accounting; Finance' -> (|(EmployeeType=A)(EmployeeType=C))

There are no parentheses in the Simplified Query Language, this means that you cannot mix components with '&' (AND)  and '|' (OR). You have
the 'component_in_and' flag in the Reader object to specify if components are in '&' (AND, True value) or in '|' (OR, False value).
'component_in_and' defaults to True::

    'CommonName: b*, Department: Engineering' -> (&(cn=b*)(EmployeeType=E'))

Object classes defined in the ObjectDef are always included in the filter, so for the previous example the resulting filter is::

    (&(&(objectClass=inetOrgPerson)(objectClass=AuxEngineer))(cn=b*)(EmployeeType=E))

when using a Reader with the 'engineer' ObjectDef.

Entry
-----

Cursors contains Entries that are the Python representation of entries stored in the LDAP DIT. There are two types of Entries,
**Read** and **Writable**. Each Entry has a ``state`` attribute that keeps information on the current status of the Entry.

Entries are returned as the result of a Search operation or a Reader search. You can access entry attributes either
as a dictionary or as properties using the AttrDef key you specified in the ObjectDef.
``entry['CommonName']`` is the same of ``entry.Common Name`` of ``entry.CommonName`` of ``entry.commonName`` and of ``entry.commonname``.

Each Entry has a entry_dn() method that returns the distinguished name of the LDAP entry, and a entry_cursor() method that returns a reference
to the Cursor used to read the entry.

Attributes are stored in an internal dictionary with case insensitive access by the key defined in the AttrDef. You can access the raw
attribute with the ``entry_raw_attribute(attribute_name)`` to get an attribute raw value, or ``entry_raw_attributes()`` to get
the whole raw attributes dictionary.

Because Attribute names are used as Entry class attributes all the "operational" attributes and method of an entry starts with **entry_**. An
Entry as the following attributes and methods:

* entry_dn: the DN of the LDAP entry

* entry_cursor: the cursor object the Entry belongs to

* entry_status: a description of the current status of the Entry (can be any of 'Initial', 'Virtual', 'Missing mandatory attributes',
  'Read', 'Writable', 'Pending changes', 'Committed', 'Ready for deletion', 'Ready for moving', 'Ready for renaming', 'Deleted'.

* entry_definition: the ObjectDef (with relevant AttrDefs) of the Entry

* entry_raw_attributes: raw attribute values as read from the DIT

* entry_mandatory_attributes: the list of attributes that are mandatory for this Entry

* entry_attributes: formatted attribute values read from the DIT

* entry_attributes_as_dict: a dictonary with formatted attribute value

* entry_read_time: the time of last read of the Entry from the LDAP server

* entry_raw_attribute(attribute): method to request a specific raw attribute

* entry_to_json(raw=False, indent=4, sort=True, stream=None, checked_attributes=True): method to convert an Entry to a JSON representation

* entry_to_ldif(all_base64=False, line_separator=None, sort_order=None, stream=None): method to convert an Entry to a LDIF representation


A Read Entry has the following additional method:

* entry_writable(object_def=None, writer_cursor=None, attributes=None, custom_validator=None): method to create a new Writable Entry *linked* to
  the original Entry. This means that every change to the Entry is reflected to the original one

A Writable Entry has the following additional properties and methods:

* entry_virtual_attributes: list of the available attributes without a value

* entry_commit_changes(refresh=True, controls=None): writes all pending changes to the DIT

* entry_discard_changes(): discards all pending changes

* entry_delete(): set the entry for deletion (performed at commit time)

* entry_refresh(self, tries=4, seconds=2): re-reads the Entry attribute values from the LDAP Server

* entry_move(destination_dn): set the entry for moving (performed at commit time)

* entry_rename(new_name): set the entry for renaming (performed at commit time)




An Entry can be converted to LDIF with the ``entry_to_ldif()`` method and to JSON with the ``entry_to_json()`` method.
Entries can be easily printed at the interactive prompt::

    >>> print(c.entries[0].entry_to_ldif())
    version: 1
    dn: cn=person1,o=test
    objectClass: inetOrgPerson
    objectClass: organizationalPerson
    objectClass: Person
    objectClass: ndsLoginProperties
    objectClass: Top
    sn: person1_surname
    cn: person1
    givenName: person1_givenname
    GUID:: +J4sRRpsAEmjlfieLEUabA==
    # total number of entries: 1

    >>> print(c.entries[0].entry_to_json())
    {
        "attributes": {
            "cn": [
                "person1"
            ],
            "givenName": [
                "person1_givenname"
            ],
            "GUID": [
                "f89e2c45-1a6c-0049-a395-f89e2c451a6c"
            ],
            "objectClass": [
                "inetOrgPerson",
                "organizationalPerson",
                "Person",
                "ndsLoginProperties",
                "Top"
            ],
            "sn": [
                "person1_surname"
            ]
        },
        "dn": "cn=person1,o=test"
    }

Attribute
---------

Values found for each attribute are stored in the Attribute object. You can access the 'values' and the 'raw_values' lists. You can
also get a reference to the relevant AttrDef in the 'definition' property, and to the relevant Entry in the 'entry' property.
You can iterate over the Attribute to get each value::

    person_common_name = person_entry.CommonName
    for cn in person_common_name:
        print(cn)
        print(cn.raw_values)

If the Attribute has a single value you get it in the 'value' property. This is useful while using the Python
interpreter at the ``>>>`` interactive prompt. If the Attribute has more than one value you get the same 'values'
list in 'value'. When you want to assign the attribute value to a variable you must use 'value' (or 'values' if you always
want a list)::

    my_department = person_entry.Department.value


When an entry is Writable the Attribute has additional attributes and methods and operators used to apply changes to the attribute values:

* virtual: True if the attribute is new and still not stored in the DIT

* changes: the list of the pending changes for the attribute

* add(value): adds one or more values to the attribute, same of **+=**

* set(value): sets one or more values for the attribute, removing any previous stored value

* delete(value): delete one or more values from the attribute, same of **-=**

* remove(): sets the attribute for deletion

* discard(): discards all pending changes in the Attribute

Modifying an Entry
------------------

With the Abstraction Layer you can "build" your Entry object and then commit it to the LDAP server in a simple pythonic way. First
you must obtain a **Writable** Entry. Entry may become writable in four different way: as Entries from a Reader Cursor,
as Entries form a Search response, as a single Entry from a Search response or as a new (virtual) Entry::

    >>> # this example is at the >>> prompt. Create a connection and a Reader cursor for the inetOrgPerson object class
    >>> from ldap3 import Connection, Reader, Writer, ObjectDef
    >>> c = Connection('sl10', 'cn=my_user,o=my_org', 'my_password', auto_bind=True)
    >>> o = ObjectDef('inetOrgPerson', c)  # automatic read of the inetOrgPerson structure from schema
    >>> r = Reader(c, o, None, 'o=test')  # we don't need to provide a filter because of the objectDef implies '(objectclass=inetOrgPerson)'
    >>> r.search()  # populate the reader with the Entries found in the Search

    # make a Writable Cursor from the person_reader Reader Cursor
    >>> w = Writer.from_cursor(r)
    >>> e = w[0]  # A Cursor is indexed on the Entries collection

    # make a Writable Cursor from an LDAP search response, you must specify the objectDef
    >>> c.search('o=test', '(objectClass=inetOrgPerson), attributes=['cn', 'sn', 'givenName']
    >>> w = Writer.from_response(c, c.response, 'inetOrgPerson')
    >>> e = w[0]

    # make a Writable Entry from the first entry of an LDAP search response, an implicit Writer Cursor is created
    >>> e = c.entries[0].entry_writable()

    # make a new Writable Entry. The Entry remains in "Virtual" state until committed to the DIT
    >>> e = w.new('cn=new_entry, o=test')

Now you can use the ``e`` Entry object as a Python class object with standard behaviour::

    >>> e.sn += 'Young'  # add an additional value to an existing attribute
    >>> e.givenname = 'John'  # create a new attribute and assign a value to it - attribute is flagged 'Virtual' until commit
    >>> e
    DN: cn=smith_j,o=test - STATUS: Writable, Pending changes - READ TIME: 2016-10-19T09:51:08.919905
        cn: smith_j
        givenName: <Virtual>
                   CHANGES: [('MODIFY_REPLACE', ['John'])]
        objectClass: inetOrgPerson
                     organizationalPerson
                     Person
                     ndsLoginProperties
                     Top
        sn: Smith
            CHANGES: [('MODIFY_ADD', ['Young'])]

Now let's perform the commit of the Entry and check the refreshed data::

    >>> e.entry_commit_changes()
    True
    >>> e
    DN: cn=smith_j,o=test - STATUS: Writable, Committed - READ TIME: 2016-10-19T09:54:58.321715
        cn: [05038763]modify-dn-2
        givenName: John
        objectClass: inetOrgPerson
                     organizationalPerson
                     Person
                     ndsLoginProperties
                     Top
        sn: Smith
            Young

As you can see the status of the entry is "Writable, Committed" and the read time has been updated.

You can discard the pending changes with ``e.entry_discard_changes()`` or delete the whole entry with ``e.delete()``. You can
also move the Entry to another container in the DIT with ``e.entry_move()`` or renaming it with ``e.entry_rename)``.

OperationalAttribute
--------------------

The OperationalAttribute class is used to store Operational Attributes read with the 'get_operational_attributes' of the Reader object set to True. It's the same
of the Attribute class except for the 'definition' property that is not present. Operational attributes key are prefixed with 'OA_'.
