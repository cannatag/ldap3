============
python3-ldap
============

python3-ldap is a pure Python 3 LDAP v3 strictly conforming to RFC4511.
Its development is at alpha stage.

License
-------

The project is open source and released under the LGPL v3 license.

Mailing List
------------

You can join the python3-ldap mailing list at http://mail.python.org/mailman/listinfo/python3-ldap


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
    - For now I have "sync-nothread" and "async-blocking-threaded" strategies
    - Planned strategies are "sync-threaded" strategy and an "event-nonblocking".

6. Semplified query construction language
    - For a different project I developed an "abstraction layer" for LDAP query. I'd like to have a generalized LDAP abstraction layer to semplify access to the DIT.

7. Compatibility mode for application using python-ldap
    - I have a number of projects using the python-ldap library. I'd like to move them to Python3 without changing what I've already done for LDAP. So it should be (ideally) enough just to change the import from python-ldap to python3-ldap to use them on Python3, at least for the LDAP part.


Installation
------------

You need "setuptools" and "pip" to install python3-ldap (or any other package manager that can download and install from pypi).
Then you can download the python3-ldap library directly from pypi::

    pip install python3-ldap --pre

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


Examples
--------

You can create a connection with::

    from ldap3 import connection, server
    from ldap3 import AUTH_SIMPLE, STRATEGY_SYNC, STRATEGY_ASYNC_THREADED, SEARCH_SCOPE_WHOLE_SUBTREE, GET_ALL_INFO
    s = server.Server('servername', port = 389, getInfo = GET_ALL_INFO)  # define an unsecure ldap server, requesting info on DSE and schema
    c = connection.Connection(s, autoBind = True, clientStrategy = STRATEGY_SYNC, user='username', password='password', authentication=AUTH_SIMPLE)  # define a synchronous connection to the server with basic authentication
    print(s.info) # display info from the DSE. OID are decoded when recognized
    result = c.search('o=test','(objectClass=*)', SEARCH_SCOPE_WHOLE_SUBTREE, attributes = ['sn', 'objectClass'])  # request a few object from the ldap server
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

SSL & TLS
---------

To use SSL basic authentication change the server definition to::

    s = server.Server('servername', port = 636, useSsl = True)  # define a secure ldap server

To start a TLS connection on an already created clear connection::

    c.tls = Tls()
    c.startTls()

You can customize the tls object with reference to key, certificate and CAs. See Tls() constructor docstring for details

Testing
-------

You can look inside the "test" package for examples on each LDAP operation.
To execute the test suite you need and ldap server with a o=test container, a ou=moved,o=test subcontainer
and a user with privileges to add, modify and remove objects in that organization context.

You can configure testserver, testuser and testpassword in the __init__.py file in the test package.


Contact me
----------

For any information, suggestion and bug reporting you can contact me at python3ldap@gmail.com or
join the python3-ldap mailing list at http://mail.python.org/mailman/listinfo/python3-ldap

=========
CHANGELOG
=========
* 0.6.0 - 2013.09.16
    - Moved to beta!
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

* 0.4.0 - 2013-07.15
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
