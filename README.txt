============
python3-ldap
============

python3-ldap is a pure Python 3 LDAP v3 strictly conforming to RFC4511.
Its development is at beta stage.

SUPPORT FOR PYTHON 2 starting from version 0.6.1 (no direct unicode support)


License
-------

The project is open source and released under the LGPL v3 license.


Mailing List
------------

You can join the python3-ldap mailing list at http://mail.python.org/mailman/listinfo/python3-ldap


Home Page
---------
Project home page is https://www.assembla.com/spaces/python3-ldap


Support:
--------
You can submit support tickets on https://www.assembla.com/spaces/python3-ldap/support/tickets


SVN repository
--------------
You can download the latest source at https://subversion.assembla.com/svn/python3-ldap


Project goals
-------------

1. Strictly follow the current RFC for LDAP 3 (from rfc4510 to rfc4519)
    - Latest RFC for LDAP v3 (dated 2006) obsoletes the previous RFC specified in rfc3377 (2251-2256, 2829, 2830, 3371) for LDAP v3 and amend and clarify the LDAP protocol.
    - All the asn1 definitions from the rfc4511 must be rewritten because those in the pyasn1_modules package are not current with the RFC.

2. Platform independent (tested on Linux and Windows) architecture
    - The library should run on Windows and Linux with no visible differences.

3. Based only on pure Python code
    - I usually work on Linux and Windows boxes and each time have to install the current python-ldap library for Python2 from different sources.
    - python3-ldap should be directly installed from source of from pypi using pip or a similar package manager on different platforms. Installation should be the same on both platforms. -
    - Socket and thread programming should be appropriate for the platform used, with no changes needed in the configuration.
    - python3-ldap library should depend on the standard library and the pyasn1 package only.

4. Compatible with python3 and (possibly) python2
    - Development and testing is done in Python 3, but as the library move from alpha to beta it should (hopefully) be compatible with Python 2.
    - Unicode strings are appropriately converted.

5. Multiple *connection strategies* to choose from, either synchronous or asynchronous
    - I'm planning to use different ways to connect to the LDAP server (no thread, single threaded, multithreaded, event...)
    - I'm not sure about which connection strategy is the best to use on ldap messages communication, so I'm writing a connection object with a **pluggable** socket connection strategy.
    - "SyncWaitStrategy", "AsyncThreadedStrategy" and "LdifProducerStrategy" are defined.
    - Planned strategies are "sync-threaded" strategy and an "event-nonblocking".

6. Semplified query construction language
    - For a different project I developed an "abstraction layer" for LDAP query. I'd like to have a generalized LDAP abstraction layer to semplify access to the DIT.

7. Compatibility mode for application using python-ldap
    - I have a number of projects using the python-ldap library. I'd like to move them to Python3 without changing what I've already done for LDAP. So it should be (ideally) enough just to change the import from python-ldap to python3-ldap to use them on Python3, at least for the LDAP part.


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
You can choose the strategy the client will use to connect to the server. There are 2 strategy defined now: syncWait and asyncThreaded

With synchronous strategy (syncWait) all LDAP operations return a boolean: True if they succede, False if they fail.

With asynchronous strategy (asyncThreaded) all LDAP operations request (except Bind) return an integer, the messageId of the request.
You can send multiple request without waiting for responses. You can get the response with the getResponse(messageId) method of the connection object.
If you get None the response has not yet arrived. You can set a timeout (getResponse(messageId, timeout = 10)) to set the seconds to wait for the response to appears.

Library raise exceptions to signal errors, last exception message is stored in the lastError attribute of the connection object.

After any operation, either synchronous or asynchronous, you'll find the following attributes popolated in the connection object:

- result: the result of the last operation
- response: the response of the last operation (for example, a search)
- lastError: any error occurred in the last operation
- bound: True if bound else False
- listening: True if the socket is listening to the server
- closed: True if the socket is not open
- responseToLdif(): response in LDIF format

Examples
--------

You can create a connection with::

    from ldap3 import Server, Connection
    from ldap3 import AUTH_SIMPLE, STRATEGY_SYNC, STRATEGY_ASYNC_THREADED, SEARCH_SCOPE_WHOLE_SUBTREE, GET_ALL_INFO
    s = Server('servername', port = 389, getInfo = GET_ALL_INFO)  # define an unsecure ldap server, requesting info on DSE and schema
    # define a synchronous connection to the server with basic authentication
    c = Connection(s, autoBind = True, clientStrategy = STRATEGY_SYNC, user='username', password='password', authentication=AUTH_SIMPLE)
    print(s.info) # display info from the DSE. OID are decoded when recognized
    # request a few objects from the ldap server
    result = c.search('o=test','(objectClass=*)', SEARCH_SCOPE_WHOLE_SUBTREE, attributes = ['sn', 'objectClass'])
    if result:
        for r in c.response:
            print(r['dn'], r['attributes']) # for unicode attributes
            print(r['dn'], r['rawAttributes']) for raw (bytes) attributes
    else:
        print('result', conn.result)
    c.unbind()

To move from syncronous to asynchronous connection just change the clientStrategy to STRATEGY_ASYNC_THREADED and add the following line before the "if result:"::

    c.getResponse(result, timeout = 10)

That's all you have to do to have an asynchronous threaded ldap client.

To get operational attributes (info as createStamp, modifiedStamp, ...) for response objects add in getOperationalAttribute = True in the search request.


SASL
----

Two SASL mechanism are implemented in the python3-ldap library: EXTERNAL and DIGEST-MD5. Even if DIGEST-MD5 is deprecated and moved to historic by RFC 6331
because it is "insecure and unsuitable for use in protocols" I've developed the authentication phase of the protocol because it is still used in ldap servers.

You can use the EXTERNAL mechanism when you're on a secure (TLS) channel. You can provide an authorization identity string in saslCredentials or let the
server trust the credential provided when establishing the secure channel::

     tls = Tls(localPrivateKeyFile = 'key.pem', localCertificateFile = 'cert.pem', validate = ssl.CERT_REQUIRED, version = ssl.PROTOCOL_TLSv1,
               caCertsFile = 'cacert.b64')
     server = Server(host = test_server, port = test_port_ssl, useSsl = True, tls = tls)
     connection = Connection(server, autoBind = True, version = 3, clientStrategy = test_strategy, authentication = AUTH_SASL,
                             saslMechanism = 'EXTERNAL', saslCredentials = 'username')

To use the DIGEST-MD5 you must pass a 4-value tuple as saslCredentials: (realm, user, password, authzId). You can pass None for realm and authzId if not used.
Quality of Protection is always 'auth'::

     server = Server(host = test_server, port = test_port)
     connection = Connection(server, autoBind = True, version = 3, clientStrategy = test_strategy, authentication = AUTH_SASL,
                             saslMechanism = 'DIGEST-MD5', saslCredentials = (None, 'username', 'password', None))

UsernameId is not required to be an ldap entry, but it can be any identifier recognized by the server (i.e. email, principal). If
you pass None as realm the default realm of the server will be used.

Keep in mind that DIGEST-MD5 is deprecated and should not be used.


Searching
---------

Search operation is enhanced with a few parameters:

- getOperationalAttributes: if True retrieve the operational (system generated) attributes for each of the result entries
- pagedSize: if greater than 0 return a simple paged search response with the number of entries required (server must conform to rfc 2696)
- pagedCookie: used for subsequent retrieve of additional entries in a simple paged search
- pagedCriticality: if True the search should fail if simple paged search is not available on the server else a full search is performed
- if the search filter contains the following characters you must use the relevant escape ASCII sequence, as per RFC 4515 (section 3): '*' -> '\\\\2A', '(' -> '\\\\28', ')' -> '\\\\29', '\\' -> '\\\\5C', chr(0) -> '\\\\00'

Simple Paged search
-------------------

The search operation is capable of performing a simple paged search as per rfc 2696. You must specify the required number of entries in each response set.
After the first search you must send back the cookie you get with each response. If you send 0 as pagedSize and a valid cookie the search operation is abandoned
Cookie can be found in connection.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']; the server may return an estimated total number of entries in
connection.result['controls']['1.2.840.113556.1.4.319']['value']['size']
You can change the pagedSize in any subsequent search request

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

    s = server.Server('servername', port = 636, useSsl = True)  # define a secure ldap server

To start a TLS connection on an already created clear connection::

    c.tls = Tls()
    c.startTls()

You can customize the tls object with reference to key, certificate and CAs. See Tls() constructor docstring for details


Abstraction Layer
-----------------

The ldap3.abstraction package is a tool to abstract access to LDAP data. It has a semplified query language for performing search operations
and a bunch of objects to define



LDIF
----

LDIF is a data interchange format for LDAP. It is defined in RFC 2849 in two different flavours: ldif-content and ldif-change.
ldif-content is used to describe DIT entries in an ASCII stream (i.e. a file), while ldif-change is used to describe Add, Delete, Modfify and
ModifyDn operations. These two format have different purposes and cannot be mixed in the same stream.
If the dn of the entry or an attribute value contains any unicode character the value must be base64 encoded, as specified in RFC 2849.
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

     ...
        # request a few objects from the ldap server
        result1 = c.search('o=test','(cn=test-ldif*)', SEARCH_SCOPE_WHOLE_SUBTREE, attributes = ['sn', 'objectClass'])
        result2 = c.search('o=test','(!(cn=test-ldif*))', SEARCH_SCOPE_WHOLE_SUBTREE, attributes = ['sn', 'objectClass'])
        ldifStream = c.responseToLdif(result1)
        ...

ldifStream will contain the LDIF representation of the result1 entries.


LDIF-change

To have the ldif representation of Add, Modify, Delete and ModifyDn operation you must use the LDIF_PRODUCER strtegy. With this strategy operations are
not executed on an LDAP server but are converted to an LDIF-change format that can be sent to an LDAP server with different mechanisms.

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
You can customize the test modifying the variables in the __init__.py in the test package. You can set the following parameters:

test_server = 'server'  # the ldap server where tests executed
test_user = 'user'  # the user that performs the tests
test_password = 'password'  # user's password

test_base = 'o=test'  # base context where test objects are created
test_moved = 'ou=moved,o=test'  # base context where  objects are moved in ModifyDN operations
test_name_attr = 'cn'  # naming attribute for test objects

test_port = 389  # ldap port
test_port_ssl = 636  # ldap secure port
test_authentication = AUTH_SIMPLE  # authentication type
test_strategy = STRATEGY_SYNC  # strategy for executing tests
#test_strategy = STRATEGY_ASYNC_THREADED  # uncomment this line to the the async strategy

To execute the test suite you need and ldap server with the test_base and test_moved containers
and a test_user with privileges to add, modify and remove objects in that organization context.
To execute the testTLS unit test you must supply your own certificates or it will fail.


Contact me
----------

For any information and suggestion  you can contact me at python3ldap@gmail.com or
join the python3-ldap mailing list at http://mail.python.org/mailman/listinfo/python3-ldap

You can also open a ticket on https://www.assembla.com/spaces/python3-ldap/support/tickets


Acknowledgements
----------------

I want to thank Mark Lutz for his 'Learning Python' and 'Programming Python' books series and John Goerzen and Brandon Rhodes
for their book 'Foundations of Python Network Programming'. These books are a wonderful tool for learning Python in the pythonic way
and this project owes a lot to them.

I wish to thank JetBrains for donating to this project the Open Source license of PyCharm 3 Professional.

I wish to thank Assembla for providing the free source repository space and the agile tools to develop this project.


=========
CHANGELOG
=========

* 0.8.0 - 2014.02.01
    - Added abstraction layer
    - Added context manager to Connection class

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
