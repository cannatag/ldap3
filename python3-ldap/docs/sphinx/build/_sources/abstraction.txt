#################
Abstraction Layer
#################

The ldap3.abstraction package is a tool to abstract access to LDAP data. It has a semplified query language for performing search operations
and a bunch of objects to define the structure of LDAP entries.
The abstraction layer is useful at command line to perform searches without having to write complex filters and in programs when LDAP is used to records
structured data.


Overview

To use the abstraction layer you can define different LDAP objects with the ObjectDef and AttrDef classes, than you create a Reader object for the
ObjectDef you have defined and then you perform search operations using a simplified query language.
All classes can be imported from the ldap3.abstraction package::

    from ldap3.abstraction import ObjectDef, AttrDef, Reader, Entry, Attribute


ObjectDef class

The ObjectDef class is used to define an abstract LDAP object.
When creating a new ObjectDef instance you can optionally specify the LDAP class(es) of the entries you will get back in a search.
The object class(es) will be automatically added to the query filter::

    person = ObjectDef('inetOrgPerson')
    engineer = ObjectDef(['inetOrgPerson', 'auxEngineer'])

Once you have defined an ObjectDef instance you can add the attributes definition with the add() method of ObjectDef. You can also use the += operator as a shortcut.
AttrDef(s) can be removed with the remove() method or using the -= operator.

ObjectDef is an iterable that returns each AttrDef object (the whole AttrDef object, not only the key).
AttrDefs can be accessed either as dictionary or as property, spaces are removed and keys are not case sensitive::

    cnAttrDef = person['Common Name']
    cnAttrDef = person['commonName']  # same as above
    cnAttrDef = person.CommonName  # same as above

This eases the use at interactive prompt where you don't have to remember the case of the attribute name. Aautocompletion feature is enabled, so you can get
a list of all defined attributes as property just pressing TAB.

Each class has a useful representation that summarize the istance status. You can access it directly at command prompt, or in a program with the str() function.


AttrDef class

The AttrDef class is used to define an abstract LDAP attribute.
AttrDef has a single mandatory parameter (the attribute name) and a number of optional parameters. The 'key' optional parameter defines a friendly name to use
while accessing the attribute. When defining only the attribute name you can add it directly to the ObjectDef (the AttrDef is automatically defined)::

    cnAttribute = AttrDef('cn')
    person.add(cnAttribute)

    person += AttrDef('cn')  # same as above
    person += 'cn'  # same as above

You can even add a list of attrDefs or attribute names to an ObjectDef::

    person += [AttrDef('cn', key = 'Common Name'), AttrDef('sn', key = 'Surname')]
    person += ['cn', 'sn']  # as above, but keys are the attributes name


Validate

You can specify a 'validate' parameter to check if the attribute value in a query is valid.
Two parameters are passed to the callable, the AttrDef.key and the value. The callable must return a boolean confirming or denying the validation::

    deps = {'A': 'Accounting', 'F': 'Finance', 'E': 'Engineering'}
    # checks that the parameter in query is in a specific range
    validDepartment = lambda attr, value: True if value in deps.values() else False
    person += AttrDef('employeeType', key = 'Department', validate = validDepartment)

In this example the Reader object will raise an exception if value for the 'Department' is not 'Accounting', 'Finance' or 'Engineering'.


PreQuery

A 'preQuery' parameter indicates a callable to perform transformations on the value to be searched for the attribute defined::

    # transform value to be search
    def getDepartmentCode(attr, value):
        for dep in deps.items():
            if dep[1] == value:
                return dep[0]
        return 'not a department'

    person += AttrDef('employeeType', key = 'Department', preQuery = getDepartmentCode)

When you perform a search with 'Accounting', 'Finance' or 'Engineering' for the Department key, the real search will be for employeeType = 'A', 'F' or 'E'.


PostQuery

A 'postQuery' parameter indicates a callable to perform transormations on the returned value::

    getDepartmentName = lambda attr, value: deps.get(value, 'not a department') if attr == 'Department' else value
    person += AttrDef('employeeType', key = 'Department', postQuery = getDepartmentName)

When you have an 'A', an 'F', or an 'E' in the employeeType attribute you get 'Accounting', 'Finance' or 'Engineering' in the 'Department' property
of the Person entry.

With a multivalue attribute postQuery receives a list of all values in the attribute. You can return an equivalent list or a single string.


DereferenceDN

With 'dereferenceDN' you can establish a relation between ObjectDefs. When dereferenceDN is set to an ObjectDef the Reader reads the attribute and use its value as
a DN for an object to be searched with a temporary Reader using the specified ObjectDef in the same Connection. The result of the second search is returned
as value of the first search::

    department = ObjectDef('groupOfNames')
    department += 'cn'
    department += AttrDef('member', key = 'employeer', dereferenceDN = person)  # values of 'employeer' will be the 'Person' entries members of the found department


Reader

Once you have defined the ObjectDef(s) and the AttrDef(s) you can instance a Reader for the ObjectDef. With it you can perform searches using a simplified
query language (explained in next paragraph). The reader can be reset to its initial status with the reset() method to execute a different search.

Reader has the following parameters:

- 'connection': the connection to use.

- 'objectDef': the ObjectDef used by the Reader instance.

- 'query': the simplified query. It can be a standard LDAP filter too (see next paragraph).

- 'base': the DIT base where to start the search.

- 'components_in_and': defines if the query components are in AND (True, default) or in OR (False).

- 'subTree': specifies if the search must be performed through the whole subtree (True, default) or only in the specified base (False).

- 'getOperationalAttributes': specifies if the search must return the operational attributes (True) of found entries. Defaults to False.

- 'controls': optional controls to use in the search operation.

Connection is open and closed automatically by the Reader.

To perform the search you can use any of the following methods:

- search()  # standard search

- search_level()  # force a Level search.

- searchSubTree()  # force a whole sub-tree search, starting from 'base'.

- search_object()  # force a object search, DN to search must be specified in 'base'.

- search_size_limit(limit)  # search with a size limit of 'limit'.

- search_time_limit(limit)  # search with a time limit of 'limit'.

- search_types_only()  # standard search without the attributes values.

- search_paged(pageSize, criticality)  # perform a paged search, with 'pageSize' number of entries for each call to this method. If 'criticality' is
                                      True the server aborts the operation if the Simple Paged Search extension is not available, else return the whole result set.

Example::

    s = Server('server')
    c = Connection(s, user = 'username', password = 'password')
    query = 'Department: Accounting'  # explained in next paragraph
    personReader = Reader(c, person, query, 'o=test')
    personReader.search()

The result of the search will be found in the 'entries' property of the personReader object.

A Reader object is an iterable that returns the entries found in the last search performed. It also  has a useful representation that summarize the Reader
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

In the Reader you can express the query filter using the standard LDAP filter syntax or using a Simplified Query Language that resembles a dictionary structure.
If you use the standard LDAP filter syntax you must use the real attribute names because the filter is directly passed to the Search operation.
THe Simplified Query Language is a string of key-values couples separated with a ',' (comma), in each of the couples the left part is the attribute key defined
in an AttrDef object while the right part is the value (or values) to be searched. Parts are separed with a ':' (colon). Keys can be prefixed with a '&' or a '|'
or searching all the values or at least one of them. Values can be prefixed with an optional '!' (exclamation mark) for negating the search and by the search
operator ('=', '<', '>', '~') requested. The default operator is '=' and can be omitted. Multiple values are separated by a ';' (semi-colon).

    A few examples::

    'CommonName: bob' -> (cn=bob)
    'CommonName: bob; john; michael' -> (|(cn=bob)(cn=john)(cn=michael))
    'Age: > 21' -> (age>=21)
    '&Age: > 21; < 65' ->&(age<=65)(age>=21))
    'Department: != Accounting'' -> (!(EmployeeType=A))
    '|Department:Accounting; Finance' -> (|(EmployeeType=A)(EmployeeType=C))

There are no parentheses in the Simplified Query Language, this means that you cannot mix components with '&' (AND)  and '|' (OR). You have the 'componentInAnd'
flag in the Reader object to specify if components are in '&' (true) or in '|' (false). 'componentInAnd' defaults to True::

    'CommonName: b*, Department: Engineering' -> (&(cn=b*)(EmployeeType=E'))

Object classes defined in the ObjectDef are always included in the filter, so for the previous example the resulting filter is::

    (&(&(objectClass=iNetOrgPerson)(objectClass=AuxEngineer))(cn=b*)(EmployeeType=E))

when using a Reader with the 'engineer' ObjectDef.


Entry

Entry objects contain the result of the search. You can access entry attributes either as a dictionary or as properties using the AttrDef key you specified in
the ObjectDef. entry['CommonName'] is the same of entry.CommonName.

Each Entry has a get_entry_dn() method that contains the distinguished name of the LDAP entry, and a get_entry_reader() method that contains a reference
to the Reader used to read the entry.

Attributes are stored in an internal dictionary with case insensitive access by the key defined in the AttrDef. You can even access the raw attribute with
the get_raw_attribute(attributeName) to get an attribute raw value, or get_raw_attributes() to get the whole raw attributes dictionary.

Entry is a read only object, you cannot modify or add any property to it. It's an iterable object that returns an attribute object at each iteration. Note that
you get back the whole attribute object, not only the key as in a standard dictionary::

    personEntry = personReader.entries[0]
    for attr in personEntry:
        print(attr.key)


Attribute

Values found for each attribute are stored in the Attribute object. You can access the 'values' and the 'rawValues' lists. You can also get a reference to the
relevant AttrDef in the 'definition' property, and to the relevant Entry in the 'entry' property. You can iterate over the Attribute to get each value::

    personCommonName = personEntry.CommonName
    for cn in personCommonName:
        print(cn)
        print(cn.rawValues)

If the Attribute has a single value you get it in the 'value' property. This is useful while using the Python interpreter at the interactive prompt. If the Attribute
has more than one value you get the same 'values' list in 'value'. When you want to assign the attribute value to a variable you must use 'value' (or 'values' if you always
want a list)::

    myDepartment = personEntry.Department.value


OperationalAttribute

The OperationalAttribute class is used to store Operational Attributes read with the 'getOperationalAttributes' of the Reader object set to True. It's the same
of the Attribute class except for the 'definition' property that is not present.
