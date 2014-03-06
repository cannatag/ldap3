python3-ldap
============

python3-ldap is a pure Python 3 LDAP version 3 strictly conforming to RFC4511.
RFC4511 is the current LDAP specification (June 2006) from IETF and obsoletes the previous LDAP
RFCs 2251, 2830, 3771 (December 1997)

python3-ldap can be used on Python 3 and Python 2 (starting from 2.6). In Python 2 there is no direct Unicode support, you get always str (bytes) as response.


License
-------

The Project is open source and released under the LGPL v3 license.


Mailing List
------------

You can join the python3-ldap mailing list at http://mail.python.org/mailman/listinfo/python3-ldap


Home Page
---------
Project home page is https://www.assembla.com/spaces/python3-ldap


Documentation
-------------
Documentation is available at https://pypi.python.org/pypi/python3-ldap


Download
--------
Package download is available at https://pypi.python.org/pypi/python3-ldap or via pip


SVN repository
--------------
You can download the latest source at https://subversion.assembla.com/svn/python3-ldap


Support:
--------
You can submit support tickets on https://www.assembla.com/spaces/python3-ldap/support/tickets


Project goals
-------------

1. Python3-ldap Conforms strictly to the current RFC for LDAP 3 (from rfc4510 to rfc4519)

    - Latest RFC for LDAP v3 (dated 2006) obsoletes the previous RFC specified in rfc3377 (2251-2256, 2829, 2830, 3371) for LDAP v3 and amend and clarify the LDAP protocol.

    - All the asn1 definitions from the rfc4511 must be rewritten because those in the pyasn1_modules package are not current with the RFC.

2. Platform independent (tested on Linux and Windows) architecture

    - The library should run on Windows and Linux and (possibly) other Unixes with no differences.

3. Based only on pure Python code

    - I usually work on Linux and Windows boxes and each time I must install the current python-ldap library for Python2 from different sources.

    - python3-ldap should be directly installed from source of from pypi using pip or a similar package manager on different platforms.

    - Installation should be the same on any platform.

    - Socket and thread programming should be appropriate for the platform used, with no changes needed in the configuration.

    - python3-ldap library should depend on the standard library and the pyasn1 package only.

4. Compatible with python3 and python2

    - Development and testing is done in Python 3, but as the library should (hopefully) be compatible with Python 2.

    - Unicode strings are appropriately converted.

5. Multiple *connection strategies* to choose from, either synchronous or asynchronous

    - I'm planning to use different ways to connect to the LDAP server (no thread, single threaded, multithreaded, event...)

    - I'm not sure about which connection strategy is the best to use on LDAP  messages communication, so I'm writing a Connection object with a **pluggable** socket connection Strategy.

    - "SyncWaitStrategy", "AsyncThreadedStrategy" and "LdifProducerStrategy" are defined.

6. Semplified query construction language

    - For a different project I developed an "abstraction layer" for LDAP query. I'd like to have a generalized LDAP abstraction layer to semplify access to the DIT.

7. Compatibility mode for application using python-ldap

    - I have a number of projects using the python-ldap library. I'd like to move them to Python3 without changing what I've already done for LDAP.

    - It should be (ideally) enough just to change the import from python-ldap to python3-ldap to use them on Python3, at least for the LDAP part.


Installation
------------

You need "setuptools" and "pip" to install python3-ldap (or any other package manager that can download and install from pypi).
Then you can download the python3-ldap library directly from pypi::

    pip install python3-ldap

This library has only one dependence on the pyasn1 module, you don't need the pyasn1_modules package, you can install it or let the installer do it for you.

If you have downloaded the source you can build the library running in the unzipped source directory with::

    python setup.py install


Quick tour
----------

You have to import the library from the ldap3 namespace.
You can choose the strategy the client will use to connect to the server. There are 2 strategy defined: 'syncWait' and 'asyncThreaded'.

With synchronous strategy (syncWait) all LDAP operations return a boolean: True if they're successful, False if they fail.

With asynchronous strategy (asyncThreaded) all LDAP operations request (except Bind) return an integer, the 'messageId' of the request.
You can send multiple request without waiting for responses. You can get the response with the getResponse(messageId) method of the Connection object.
If you get None the response has not yet arrived. You can set a timeout (getResponse(messageId, timeout = 10)) to set the number of seconds to wait for the response to appear.

Library raise LDAPException to signal errors, last exception message is stored in the lastError attribute of the Connection object when available.

After any operation, either synchronous or asynchronous, you'll find the following attributes populated in the Connection object:

- result: the result of the last operation
- response: the response of the last operation (for example, a search)
- lastError: any error occurred in the last operation
- bound: True if bound else False
- listening: True if the socket is listening to the server
- closed: True if the socket is not open
- responseToLdif(): response in LDIF format


Connections
-----------

You can create a connection with::

    from ldap3 import Server, Connection
    from ldap3 import AUTH_SIMPLE, STRATEGY_SYNC, STRATEGY_ASYNC_THREADED, SEARCH_SCOPE_WHOLE_SUBTREE, GET_ALL_INFO
    s = Server('servername', port = 389, getInfo = GET_ALL_INFO)  # define an unsecure LDAP server, requesting info on DSE and schema
    # define a synchronous connection to the server with basic authentication
    c = Connection(s, autoBind = True, clientStrategy = STRATEGY_SYNC, user='username', password='password', authentication=AUTH_SIMPLE)
    print(s.info) # display info from the DSE. OID are decoded when recognized by the library
    # request a few objects from the LDAP server
    result = c.search('o=test','(objectClass=*)', SEARCH_SCOPE_WHOLE_SUBTREE, attributes = ['sn', 'objectClass'])
    if result:
        for r in c.response:
            print(r['dn'], r['attributes']) # return unicode attributes
            print(r['dn'], r['rawAttributes']) return raw (bytes) attributes
    else:
        print('result', conn.result)
    c.unbind()

To move from synchronous to asynchronous connection you have just to change the 'clientStrategy' to 'STRATEGY_ASYNC_THREADED' and add the following line before the 'if result:'::

    c.getResponse(result, timeout = 10)

That's all you have to do to have an asynchronous threaded LDAP client.

To get operational attributes (createStamp, modifiedStamp, ...) for response objects add 'getOperationalAttribute = True' in the search request.


Connection context manager

Connections respond to the context manager protocol, so you can have automatic bind and unbind with the following syntax::

    from ldap3 import Server, Connection
    s = Server('servername')
    c = Connection(s, user = 'username', password = 'password')
    with c:
        c.search('o=test','(objectClass=*)', SEARCH_SCOPE_WHOLE_SUBTREE, attributes = ['sn', 'objectClass'])
    print(connection.result)

or, even shorter::

    from ldap3 import Server, Connection
    with Connection(Server('servername'), user = 'username', password = 'password') as c
        c.search('o=test','(objectClass=*)', SEARCH_SCOPE_WHOLE_SUBTREE, attributes = ['sn', 'objectClass'])  # connection is opened, bound, searched and closed
    print(connection.result)

Connection retains the state when entering the context, that is if the connection was closed and unbound it will remain closed and unbound when leaving the context,
if the connection was open or bound its status will be restored when exiting the context. Connection is always open and bound while in context.

Using the context manager connections will be opened and bound as you enter the Connection context and will be unbound when you leave the context.
Unbind will be tried even if the operations in context raise an exception.


Searching
---------

Search operation is enhanced with a few parameters:

- getOperationalAttributes: when True retrieves the operational (system generated) attributes for each of the result entries.
- pagedSize: if greater than 0 returns a simple paged search response with the number of entries specified (LDAP server must conform to RFC 2696, September 1999).
- pagedCookie: used for subsequent retrieval of additional entries in a simple paged search.
- pagedCriticality: if True the search should fail if simple paged search is not available on the server else a full search is performed

If the search filter contains the following characters you must use the relevant escape ASCII sequence, as per RFC 4515 (section 3): '*' -> '\\\\2A', '(' -> '\\\\28', ')' -> '\\\\29', '\\' -> '\\\\5C', chr(0) -> '\\\\00'


Simple Paged search
-------------------

The search operation is capable of performing a simple paged search as per RFC 2696. You must specify the required number of entries in each response set.
After the first search you must send back the cookie you get with each response. If you send 0 as pagedSize and a valid cookie the search operation is abandoned
Cookie can be found in connection.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']; the server may return an estimated total number of entries in
connection.result['controls']['1.2.840.113556.1.4.319']['value']['size'].
You can change the pagedSize in any subsequent search request.

Example::

    from ldap3 import Server, Connection, SEARCH_SCOPE_WHOLE_SUBTREE
    totalEntries = 0
    server = Server('test-server')
    connection = Connection(server, user = 'test-user', password = 'test-password')
    connection.search(searchBase = 'o=test', searchFilter = '(objectClass=inetOrgPerson)', searchScope = SEARCH_SCOPE_WHOLE_SUBTREE,
                      attributes = ['cn', 'givenName'], pagedSize = 5)
    totalEntries += len(connection.response)
    cookie = self.connection.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
    while cookie:
        connection.search(searchBase = 'o=test', searchFilter = '(objectClass=inetOrgPerson)', searchScope = SEARCH_SCOPE_WHOLE_SUBTREE,
                          attributes = ['cn', 'givenName'], pagedSize = 5, pagedCookie = cookie)
        totalEntries += len(connection.response)
        cookie = self.connection.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
    print('Total entries retrieved:', totalEntries)
    connection.close()


SSL & TLS
---------

To use SSL basic authentication change the server definition to::

    s = server.Server('servername', port = 636, useSsl = True)  # define a secure LDAP server

To start a TLS connection on an already created clear connection::

    c.tls = Tls()
    c.startTls()

You can customize the Tls object with references to key, certificate and CAs. See the Tls() constructor docstring for details


SASL
----

Two SASL mechanisms are implemented in the python3-ldap library: EXTERNAL and DIGEST-MD5. Even if DIGEST-MD5 is deprecated and moved to historic (RFC 6331, July 2011)
because it is "insecure and unsuitable for use in protocols" I've developed the authentication phase of the protocol because it is still used in LDAP servers.


External

You can use the EXTERNAL mechanism when you're on a secure (TLS) channel. You can provide an authorization identity string in saslCredentials or let the
server trust the credential provided when establishing the secure channel::

     tls = Tls(localPrivateKeyFile = 'key.pem', localCertificateFile = 'cert.pem', validate = ssl.CERT_REQUIRED, version = ssl.PROTOCOL_TLSv1,
               caCertsFile = 'cacert.b64')
     server = Server(host = test_server, port = test_port_ssl, useSsl = True, tls = tls)
     connection = Connection(server, autoBind = True, version = 3, clientStrategy = test_strategy, authentication = AUTH_SASL,
                             saslMechanism = 'EXTERNAL', saslCredentials = 'username')


Digest-MD5

To use the DIGEST-MD5 you must pass a 4-value tuple as saslCredentials: (realm, user, password, authzId). You can pass None for 'realm' and 'authzId' if not used.

Quality of Protection is always 'auth'::

     server = Server(host = test_server, port = test_port)
     connection = Connection(server, autoBind = True, version = 3, clientStrategy = test_strategy, authentication = AUTH_SASL,
                             saslMechanism = 'DIGEST-MD5', saslCredentials = (None, 'username', 'password', None))

UsernameId is not required to be an LDAP entry, but it can be any identifier recognized by the server (i.e. email, principal, ...). If
you pass None as 'realm' the default realm of the LDAP server will be used.

Again, consider that DIGEST-MD5 is deprecated and should not be used.


Abstraction Layer
-----------------

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

- 'componentsInAnd': defines if the query components are in AND (True, default) or in OR (False).

- 'subTree': specifies if the search must be performed through the whole subtree (True, default) or only in the specified base (False).

- 'getOperationalAttributes': specifies if the search must return the operational attributes (True) of found entries. Defaults to False.

- 'controls': optional controls to use in the search operation.

Connection is open and closed automatically by the Reader.

To perform the search you can use any of the following methods:

- search()  # standard search

- searchLevel()  # force a Level search.

- searchSubTree()  # force a whole sub-tree search, starting from 'base'.

- searchObject()  # force a object search, DN to search must be specified in 'base'.

- searchSizeLimit(limit)  # search with a size limit of 'limit'.

- searchTimeLimit(limit)  # search with a time limit of 'limit'.

- searchTypesOnly()  # standard search without the attributes values.

- searchPaged(pageSize, criticality)  # perform a paged search, with 'pageSize' number of entries for each call to this method. If 'criticality' is
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

Each Entry has a getEntryDN() method that contains the distinguished name of the LDAP entry, and a getEntryReader() method that contains a reference
to the Reader used to read the entry.

Attributes are stored in an internal dictionary with case insensitive access by the key defined in the AttrDef. You can even access the raw attribute with
the getRawAttribute(attributeName) to get an attribute raw value, or getRawAttributes() to get the whole raw attributes dictionary.

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

LDIF
----

LDIF is a data interchange format for LDAP. It is defined in RFC 2849 (June 2000) in two different flavours: ldif-content and ldif-change.
ldif-content is used to describe DIT entries in an ASCII stream (i.e. a file), while ldif-change is used to describe Add, Delete, Modfify and
ModifyDn operations. These two formats have different purposes and cannot be mixed in the same stream.
If the DN of the Entry or an Attribute value contains any unicode character the value must be base64 encoded, as specified in RFC 2849.
Python3-ldap is compliant to the latest LDIF format (version: 1).

LDIF-content

You can use the ldif-content flavour with any search result::

    ...
    # request a few objects from the ldap server
    result = c.search('o=test','(cn=test-ldif*)', SEARCH_SCOPE_WHOLE_SUBTREE, attributes = ['sn', 'objectClass'])
    ldifStream = c.responseToLdif()
    ...


ldifStream will contain::

    version: 1
    dn: cn=test-ldif-1,o=test
    objectClass: inetOrgPerson
    objectClass: organizationalPerson
    objectClass: Person
    objectClass: ndsLoginProperties
    objectClass: Top
    sn: test-ldif-1

    dn: cn=test-ldif-2,o=test
    objectClass: inetOrgPerson
    objectClass: organizationalPerson
    objectClass: Person
    objectClass: ndsLoginProperties
    objectClass: Top
    sn:: dGVzdC1sZGlmLTItw6DDssO5


    # total number of entries: 2


you can even request a ldif-content for a response you saved early::

        # request a few objects from the ldap server
        result1 = c.search('o=test','(cn=test-ldif*)', SEARCH_SCOPE_WHOLE_SUBTREE, attributes = ['sn', 'objectClass'])
        result2 = c.search('o=test','(!(cn=test-ldif*))', SEARCH_SCOPE_WHOLE_SUBTREE, attributes = ['sn', 'objectClass'])
        ldifStream = c.responseToLdif(result1)

ldifStream will contain the LDIF representation of the result entries.


LDIF-change

To have the ldif representation of Add, Modify, Delete and ModifyDn operation you must use the LDIF_PRODUCER strategy. With this strategy operations are
not executed on an LDAP server but are converted to an ldif-change format that can be sent to an LDAP server.

For example::

    from ldap3 import Connection, STRATEGY_LDIF_PRODUCER
    connection = Connection(server = None, clientStrategy = STRATEGY_LDIF_PRODUCER)  # no need of real LDAP server
    connection.add('cn=test-add-operation,o=test'), 'iNetOrgPerson',
                   {'objectClass': 'iNetOrgPerson', 'sn': 'test-add', 'cn': 'test-add-operation'})

    in connection.response you will find:

    version: 1
    dn: cn=test-add-operation,o=test
    changetype: add
    objectClass: inetorgperson
    sn: test-add
    cn: test-add-operation

A more complex modify operation (from the RFC 2849 examples)::

    from ldap3 import MODIFY_ADD. MODIFY_DELETE, MODIFY_REPLACE
    connection.modify('cn=Paula Jensen, ou=Product Development, dc=airius, dc=com',
        {'postaladdress': (MODIFY_ADD, ['123 Anystreet $ Sunnyvale, CA $ 94086']),
         'description': (MODIFY_DELETE, []),
         'telephonenumber': (MODIFY_REPLACE, ['+1 408 555 1234', '+1 408 555 5678']),
         'facsimiletelephonenumber': (MODIFY_DELETE, ['+1 408 555 9876'])
        })

    returns:

    version: 1
    dn: cn=Paula Jensen, ou=Product Development, dc=airius, dc=com
    changetype: modify
    add: postaladdress
    postaladdress: 123 Anystreet $ Sunnyvale, CA $ 94086
    -
    delete: description
    -
    replace: telephonenumber
    telephonenumber: +1 408 555 1234
    telephonenumber: +1 408 555 5678
    -
    delete: facsimiletelephonenumber
    facsimiletelephonenumber: +1 408 555 9876
    -


Testing
-------

Inside the "test" package you can find examples for each of the LDAP operations.
You can customize the test modifying the variables in the __init__.py in the test package. You can set the following parameters::

    test_server = 'server'  # the LDAP server where tests are executed
    test_user = 'user'  # the user that performs the tests
    test_password = 'password'  # user's password

    test_base = 'o=test'  # base context where test objects are created
    test_moved = 'ou=moved,o=test'  # base context where objects are moved in ModifyDN operations
    test_name_attr = 'cn'  # naming attribute for test objects

    test_port = 389  # ldap port
    test_port_ssl = 636  # ldap secure port
    test_authentication = AUTH_SIMPLE  # authentication type
    test_strategy = STRATEGY_SYNC  # strategy for executing tests
    #test_strategy = STRATEGY_ASYNC_THREADED  # uncomment this line to test the async strategy

To execute the test suite you need an LDAP server with the test_base and test_moved containers and a test_user with privileges to add, modify and remove objects
in that context.
To execute the testTLS unit test you must supply your own certificates or tests will fail.


Contact me
----------

For any information and suggestion you can contact me at python3ldap@gmail.com or
join the python3-ldap mailing list at http://mail.python.org/mailman/listinfo/python3-ldap

You can also open a ticket on https://www.assembla.com/spaces/python3-ldap/support/tickets


Acknowledgements
----------------

I want to thank Mark Lutz for his 'Learning Python' and 'Programming Python' excellent books serie and John Goerzen and Brandon Rhodes
for their book 'Foundations of Python Network Programming'. These books are a wonderful tool for learning Python and this project owes a lot to them.

I wish to thank JetBrains for donating to this project the Open Source license of PyCharm 3 Professional.

I wish to thank Assembla for providing the free source repository space and the agile tools to develop this project.


CHANGELOG
=========

* 0.8.3
    - SyncWaitRestartable strategy
    - removed forceBind parameter
    - usage statistics updated with restartable successes/failures counters and open/closed/wrapped sockets counter

* 0.8.2 2014.03.04
    - Added refresh() method to Entry object to read again the attributes from the Reader
    - Fixed python 2.6 issues
    - Fixed test suite for python 2.6

* 0.8,1 2014.02.12
    - Changed Exception returned by the library to LDAPException, a subclass of Exception.
    - Fixed documentation typos

* 0.8.0 - 2014.02.08
    - Added abstraction layer (for searching)
    - Added context manager to Connection class
    - Added readOnly parameter to Connection class
    - Fixed a bug in search with 'less than' parameter
    - Remove validation of available SSL protocols because different Python interpreters can use different ssl packages

* 0.7.3 - 2014.01.05
    - Added SASL DIGEST-MD5 support
    - Moved to intrapackage (relative) imports

* 0.7.2 - 2013.12.30
    - Fixed a bug when parentheses are used in search filter as ASCII escaped sequences

* 0.7.1 - 2013.12.21
    - Completed support for LDFI as per rfc 2849
    - Added new LDIF_PRODUCER strategy to generate LDIF-CHANGE stream
    - Fixed a bug in the autoReferral feature when controls where used in operation

* 0.7.0 - 2013.12.12
    - Added support for LDIF as per rfc 2849
    - Added ldif-content compliant search responses
    - Added exception when using autoBind if connection is not successful

* 0.6.7 - 2013.12.03
    - Fixed exception when DSA is not willing to return rootDSE and schema info

* 0.6.6 - 2013.11.13
    - Added parameters to tests suite

* 0.6.5 - 2013.11.05
    - Modified rawAttributes decoding, now null (empty) values are returned even if invalid in protocol

* 0.6.4 - 2013.10.16
    - Added simple paged search as per rfc 2696
    - Controls return values are decoded and stored in result attribute of connection

* 0.6.3 - 2013.10.07
    - Added Extesible Filter syntax to search filter
    - Fixed exception while closing connection in AsyncThreaded strategy

* 0.6.2 - 2013.10.01
    - Fix for referrals in searchRefResult
    - Disabled schema reading on Active Directory

* 0.6.1 - 2013.09.22
    - Experimental support for Python 2 - no unicode
    - Added backport of ssl.match_name for python 2
    - Minor fix for using the client in Python 2
    - Fix for getting schema info with AsyncThreaded strategy

* 0.6.0 - 2013.09.16
    - Moved to beta!
    - Added support site hosted on www.assembla.com
    - Added public svn repository on www.assembla.com
    - Added getInfo to server object, parameter can be: GET_NO_INFO, GET_DSA_INFO, GET_SCHEMA_INFO, GET_ALL_INFO
    - Added method to read the schema from the server. Schema is decoded and returned in different dictionaries of the  server.schema object
    - Updated connection usage info (elapsed time is now computed when connection is closed)
    - Updated OID dictionary with extensions and controls from Active Directory specifications.

* 0.5.3 - 2013.09.03
    - Added getOperationalAttributes boolean to Search operation to fetch the operational attributes during search
    - Added increment operation to modify operation as per rfc 4525
    - Added dictionary of OID description (for DSE and schema decoding)
    - Added method to get Info from DSE (returned in server.info object)
    - Modified exceptions for sending controls in LDAP request
    - Added connection usage (in connection.usage if collectUsage=True in connection definition)
    - Fixed StartTls in asynchronous client strategy

* 0.5.2 - 2013.08.27
    - Added SASLprep profile for validating password
    - Fixed rfc4511 asn1 definition

* 0.5.1 - 2013.08.17
	- Refactored package structure
	- Project description reformatted with reStructuredText
	- Added Windows graphical installation

* 0.5.0 - 2013.08.15
	- Added reference to LGPL v3 license
	- Added Tls object to hold ssl/tls configuration
	- Added StartTLS feature
	- Added SASL feature
	- Added SASL EXTERNAL mechanism
	- Fixed Unbind
	- connection.close in now an alias for connection.unbind

* 0.4.4 - 2013.08.01
	- Added 'Controls' to all LDAP Requests
	- Added Extended Request feature
	- Added Intermediate Response feature
	- Added logical namespace 'ldap3'

* 0.4.3 - 2013.07.31
	- Test suite refactored
	- Fixed single object search response error
	- Changed attributes returned in search from tuple to dict
	- Added 'rawAttributes' key in search response to hold undecoded (binary) attribute values read from ldap
	- Added __repr__ for Server and Connection objects to re-create the object instance

* 0.4.2 - 2013.07.29
	- Added autoReferral feature as per RFC 4511 (4.1.10)
	- Added allowedReferralHosts to conform to Security considerations of RFC 4516

* 0.4.1 - 2013.07.20
	- Add validation to Abandon operation
	- Added connection.request to hold a dictionary of info about last request
	- Added info about outstanding operation in connection.strategy._oustanding
	- Implemented RFC 4515 for search filter coding and decoding
	- Added a parser to build filter string from LdapMessage

* 0.4.0 - 2013.07.15
    - Refactoring of the connection and strategy classes
    - Added the ldap3.strategy namespace to contains client connection strategies
    - Added ssl authentication
    - Moved authentication parameters from Server object to Connection object
    - Added ssl parameters to Server Object

* 0.3.0 - 2013.07.14
    - Fixed AsyncThreaded strategy with _outstanding and _responses attributes to hold the pending requests and the not-yet-read responses
    - Added Extended Operation
    - Added "Unsolicited Notification" discover logic
    - Added managing of "Notice of Disconnection" from server to properly close connection

* 0.2.0 - 2013.07.13
    - Update setup with setuptools 0.7
    - Docstrings added to class
    - Removed ez_setup dependency
    - Removed distribute dependency

* 0.1.0 - 2013.07.12
    - Initial upload on pypi
    - PyASN1 rfc4511 module completed and tested
    - Synchronous client working properly
    - Asynchronous client working but not fully tested
    - Basic authentication working
