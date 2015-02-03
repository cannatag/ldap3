#################
Abstraction Layer
#################

The ldap3.abstract package is a tool to abstract access to LDAP data. It has a *simplified query language* for performing search operations
and a bunch of objects to define the structure of LDAP entries.
The abstraction layer is useful at command line to perform searches without having to write complex filters and in programs when LDAP is used to record
structured data.

Overview
--------

To use the abstraction layer you must describe LDAP objects definition using the ObjectDef and AttrDef classes, than you create a Reader object for the
ObjectDef you have defined and you perform search operations using a simplified query language.
All classes can be imported from the ldap3 package::

    from ldap3 import ObjectDef, AttrDef, Reader, Entry, Attribute, OperationalAttribute

ObjectDef class
---------------

The ObjectDef class is used to define an abstract LDAP object.
When creating a new ObjectDef instance you can optionally specify the LDAP class(es) of the entries you will get back in a search.
The object class(es) will be automatically added to the query filter::

    person = ObjectDef('inetOrgPerson')
    engineer = ObjectDef(['inetOrgPerson', 'auxEngineer'])

Once you have defined an ObjectDef instance you can add the attributes definition with the add() method of ObjectDef. You can also use the += operator as a shortcut.
AttrDef(s) can be removed with the remove() method or using the -= operator.

ObjectDef is an iterable that returns each AttrDef object (the whole AttrDef object, not only the key).
AttrDefs can be accessed either as a dictionary or as a property, spaces are removed and keys are not case sensitive::

    cn_attr_def = person['Common Name']
    cn_attr_def = person['commonName']  # same as above
    cn_attr_def = person.CommonName  # same as above

This eases the use at interactive prompt where you don't have to remember the case of the attribute name. *Autocompletion feature* is enabled, so you can get
a list of all defined attributes as property just pressing TAB at the interactive prompt.

Each class has a useful representation that summarize the istance status. You can access it directly at the interactive prompt, or in a program with the str() function.

AttrDef class
-------------

The AttrDef class is used to define an abstract LDAP attribute.
AttrDef has a single mandatory parameter, the attribute name, and a number of optional parameters. The 'key' optional parameter defines a friendly name to use
while accessing the attribute. When defining only the attribute name you can add it directly to the ObjectDef (the AttrDef is automatically defined)::

    cn_attribute = AttrDef('cn')
    person.add(cn_attribute)

    person += AttrDef('cn')  # same as above
    person += 'cn'  # same as above

You can even add a list of attrDefs or attribute names to an ObjectDef::

    person += [AttrDef('cn', key = 'Common Name'), AttrDef('sn', key = 'Surname')]
    person += ['cn', 'sn']  # as above, but keys are the attribute names

Validation
^^^^^^^^^^

You can specify a 'validate' parameter to check if the attribute value in a query is valid.
Two parameters are passed to the callable, the AttrDef.key and the value. The callable must return a boolean allowing or denying the validation::

    deps = {'A': 'Accounting', 'F': 'Finance', 'E': 'Engineering'}
    # checks that the parameter in query is in a specific range
    valid_department = lambda attr, value: True if value in deps.values() else False
    person += AttrDef('employeeType', key = 'Department', validate = validDepartment)

In this example the Reader object will raise an exception if values for the 'Department' are not 'Accounting', 'Finance' or 'Engineering'.

Pre Query transformation
^^^^^^^^^^^^^^^^^^^^^^^^

A 'pre_query' parameter indicates a callable to perform a transformation on the value to be searched for the attribute defined::

    # transform value to be search
    def get_department_code(attr, value):
        for dep in deps.items():
            if dep[1] == value:
                return dep[0]
        return 'not a department'

    person += AttrDef('employeeType', key = 'Department', pre_query = get_department_code)

When you perform a search with 'Accounting', 'Finance' or 'Engineering' for the Department key, the real search will be for employeeType = 'A', 'F' or 'E'.

Post query transformation
^^^^^^^^^^^^^^^^^^^^^^^^^

A 'post_query' parameter indicates a callable to perform a transformation on the returned value::

    get_department_name = lambda attr, value: deps.get(value, 'not a department') if attr == 'Department' else value
    person += AttrDef('employeeType', key = 'Department', post_query = get_department_name)

When you have an 'A', an 'F', or an 'E' in the employeeType attribute you get 'Accounting', 'Finance' or 'Engineering' in the 'Department' property
of the Person entry.

With a multivalue attribute post_query receives a list of all values in the attribute. You can return an equivalent list or a single string.

Dereferencing DNs

With 'dereference_dn' you can establish a relation between different ObjectDefs. When dereference_dn is set to an ObjectDef the Reader reads the attribute and use its value as
a DN for an object to be searched (using a temporary Reader) with the specified ObjectDef in the same Connection. The result of the second search is returned
as value of the first search::

    department = ObjectDef('groupOfNames')
    department += 'cn'
    department += AttrDef('member', key = 'employeer', dereference_dn = person)  # values of 'employeer' will be the 'Person' entries members of the found department

Reader
------

Once you have defined the ObjectDef(s) and the AttrDef(s) you can instance a Reader for the ObjectDef. With it you can perform searches using a simplified
query language (explained in next paragraph). To execute a different search the reader can be reset to its initial status with the reset() method.

Reader has the following parameters:

- 'connection': the connection to use.

- 'object_def': the ObjectDef used by the Reader instance.

- 'query': the simplified query. It can be a standard LDAP filter (see next paragraph).

- 'base': the DIT base where to start the search.

- 'components_in_and': defines if the query components are in AND (True, default) or in OR (False).

- 'sub_tree': specifies if the search must be performed through the whole subtree (True, default) or only in the specified base (False).

- 'get_operational_attributes': specifies if the search must return the operational attributes (True) of found entries. Defaults to False.

- 'controls': optional controls to use in the search operation.

Connection is open and closed automatically by the Reader.

To perform the search you can use any of the following methods:

- search(): standard search.

- search_level(): force a Level search.

- search_sub_tree(): force a whole sub-tree search, starting from 'base'.

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

The result of the search will be found in the 'entries' property of the person_reader object.

A Reader object is an iterable that returns the entries found in the last search performed. It also has a useful representation that summarize the Reader
configuration and status::

    print(personReader)
    CONN   : ldap://server:389 - cleartext - user: cn=admin,o=test - version 3 - unbound - closed - not listening - SyncWaitStrategy
    BASE   : 'o=test' [SUB]
    DEFS   : 'iNetOrgPerson' [CommonName <cn>, Department <employeeType>, Surname <sn>]
    QUERY  : 'Common Name :test-add*, surname:=t*' [AND]
    PARSED : 'CommonName: =test-add*, Surname: =t*' [AND]
    ATTRS  : ['cn', 'employeeType', 'sn', '+'] [OPERATIONAL]
    FILTER : '(&(objectClass=iNetOrgPerson)(cn=test-add*)(sn=t*))'
    ENTRIES: 1 [SUB] [executed at: Sun Feb  9 20:43:47 2014]


Simplified Query Language
-------------------------

In the Reader you can express the query filter using the standard LDAP filter syntax or using a *Simplified Query Language* that resembles a dictionary structure.
If you use the standard LDAP filter syntax you must use the real attribute names because the filter is directly passed to the Search operation.

Tee Simplified Query Language filter is a string of key-values couples separated with a ',' (comma), in each of the couples the left part is the attribute key defined
in an AttrDef object while the right part is the value (or values) to be searched. Parts are separed with a ':' (colon). Keys can be prefixed with a '&' (AND) or a '|' (OR)
or searching all the values or at least one of them. Values can be prefixed with an optional exclamation mark '!' (NOT) for negating the search followed by the needed search
operator ('=', '<', '>', '~'). The default operator is '=' and can be omitted. Multiple values are separated by a ';' (semi-colon).

    A few examples::

    'CommonName: bob' -> (cn=bob)
    'CommonName: bob; john; michael' -> (|(cn=bob)(cn=john)(cn=michael))
    'Age: > 21' -> (age>=21)
    '&Age: > 21; < 65' ->&(age<=65)(age>=21))
    'Department: != Accounting'' -> (!(EmployeeType=A))
    '|Department:Accounting; Finance' -> (|(EmployeeType=A)(EmployeeType=C))

There are no parentheses in the Simplified Query Language, this means that you cannot mix components with '&' (AND)  and '|' (OR). You have the 'component_in_and'
flag in the Reader object to specify if components are in '&' (AND, True value) or in '|' (OR, False value). 'component_in_and' defaults to True::

    'CommonName: b*, Department: Engineering' -> (&(cn=b*)(EmployeeType=E'))

Object classes defined in the ObjectDef are always included in the filter, so for the previous example the resulting filter is::

    (&(&(objectClass=iNetOrgPerson)(objectClass=AuxEngineer))(cn=b*)(EmployeeType=E))

when using a Reader with the 'engineer' ObjectDef.

Entry
-----

Entry objects contain the result of the search. You can access entry attributes either as a dictionary or as properties using the AttrDef key you specified in
the ObjectDef. entry['CommonName'] is the same of entry.CommonName and of entry.commonName or entry.commonname.

Each Entry has a entry_get_dn() method that returns the distinguished name of the LDAP entry, and a entry_get_reader() method that returns  a reference
to the Reader used to read the entry.

Attributes are stored in an internal dictionary with case insensitive access by the key defined in the AttrDef. You can even access the raw attribute with
the get_raw_attribute(attribute_name) to get an attribute raw value, or get_raw_attributes() to get the whole raw attributes dictionary.
You can get the whole attribute name list with entry_get_attribute_names(), and the attributes dictionary with entry_get_attributes_dict()

Entry is a read only object, you cannot modify or add any property to it. It's an iterable object that returns an attribute object at each iteration. Note that
you get back the whole attribute object, not only the key as in a standard dictionary::

    person_entry = person_reader.entries[0]
    for attr in person_entry:
        print(attr.key)

An Entry can be converted to ldif with the entry.entry_to_ldif() method and to json with the entry.entry_to_json() method.
Entries can be easily printed at the interactive prompt::

    >>> c.entries[0]
    DN: o=services
        ACL: 2#entry#o=services#loginScript
             2#entry#o=services#printJobConfiguration
             32#subtree#cn=edir1,o=services#[All Attributes Rights]
             16#subtree#cn=edir1,o=services#[Entry Rights]
             32#subtree#cn=edir2,o=services#[All Attributes Rights]
             16#subtree#cn=edir2,o=services#[Entry Rights]
             32#subtree#cn=edir3,o=services#[All Attributes Rights]
             16#subtree#cn=edir3,o=services#[Entry Rights]
        GUID: fd9a0d90-15be-2841-fd82-fd9a0d9015be
        backLink: 32860#cn=edir3,o=services
        createTimestamp: 2014-06-20 13:19:14+00:00
        entryDN: o=services
        entryFlags: 4
        localEntryID: 32787
        modifiersName: cn=admin,o=services
        modifyTimestamp: 2014-11-07 08:17:43+00:00
        name: services
        o: services
        objectClass: Organization
                     ndsLoginProperties
                     ndsContainerLoginProperties
                     Top
        revision: 6
        structuralObjectClass: Organization
        subordinateCount: 33
        subschemaSubentry: cn=schema

and each attribute of the entry can be accessed as a dictionary or as a namespace::

    >>> c.entries[0].GUID
        GUID: fd9a0d90-15be-2841-fd82-fd9a0d9015be
    >>> c.entries[0].GUID.value
        'fd9a0d90-15be-2841-fd82-fd9a0d9015be'
    >>> c.entries[0].GUID.raw_values
        [b'\xfd\x9a\r\x90\x15\xbe(A\xfd\x82\xfd\x9a\r\x90\x15\xbe']
    >>> c.entries[0].GUID.values
        ['fd9a0d90-15be-2841-fd82-fd9a0d9015be']

you can obtain already formatted values when requesting the schema in the Server object.


Attribute
---------

Values found for each attribute are stored in the Attribute object. You can access the 'values' and the 'raw_values' lists. You can also get a reference to the
relevant AttrDef in the 'definition' property, and to the relevant Entry in the 'entry' property. You can iterate over the Attribute to get each value::

    person_common_name = person_entry.CommonName
    for cn in person_common_name:
        print(cn)
        print(cn.raw_values)

If the Attribute has a single value you get it in the 'value' property. This is useful while using the Python interpreter at the interactive prompt. If the Attribute
has more than one value you get the same 'values' list in 'value'. When you want to assign the attribute value to a variable you must use 'value' (or 'values' if you always
want a list)::

    my_department = person_entry.Department.value

OperationalAttribute
--------------------

The OperationalAttribute class is used to store Operational Attributes read with the 'get_operational_attributes' of the Reader object set to True. It's the same
of the Attribute class except for the 'definition' property that is not present. Operational attributes key are prefixed with 'op_'.
