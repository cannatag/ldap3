=======
License
=======

The python3-ldap project is open source and released under the LGPL v3 license.

PEP8 Compliance
===============

python3-ldap is PEP8 compliance starting from version 0.9.0.

Mailing List
------------

You can join the python3-ldap mailing list at http://mail.python.org/mailman/listinfo/python3-ldap

Home Page
---------

Project home page is https://www.assembla.com/spaces/python3-ldap

Documentation
-------------

Documentation is available at http://pythonhosted.org/python3-ldap

Download
--------

Package download is available at https://pypi.python.org/pypi/python3-ldap or via pip

SVN repository
--------------

You can download the latest source at https://subversion.assembla.com/svn/python3-ldap

Support
-------

You can submit support tickets on https://www.assembla.com/spaces/python3-ldap/support/tickets

Contact me
----------

For any information and suggestions you can contact me at python3ldap@gmail.com or you can join the python3-ldap mailing list at http://mail.python.org/mailman/listinfo/python3-ldap. You can also open a support ticket on https://www.assembla.com/spaces/python3-ldap/support/tickets

CHANGELOG
=========

* 0.9.2 2014.04.01
    - changed return value in get_response from response to (response, result) - helpful for multi threaded connections
    - added ReusableStrategy for pooling connections

* 0.9.1 2014.03.30
    - added laziness to test suite
    - changed ServerPool signature to accept active and exhaust parameters
    - removed unneeded start_listen parameter
    - added 'lazy' parameter to open, bind and unbind a connection only when an effective operation is done
    - fixed start_tls in SyncWaitRestartable strategy
    - fixed certificate name checking while opening an ssl connection
    - fixed syntax error during installation
    - socket operations now raise proper exception, not generic LDAPException (thanks to Joseph)
    - tested against Python 3.4, 3.3, 2.7, 2.6
    - updated setuptools to 3.3

* 0.9.0 2014.03.20
    - PEP8 compliance
    - added ldap3.compat package with non PEP8-compliant signatures
    - renamed ldap3.abstraction to ldap3.abstract
    - moved connection.py, server.py and tls.py files to ldap3.core
    - fixed SyncWaitRestartableStrategy (thanks to Christoph)

* 0.8.3 2014.03.08
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
	- Added 'raw_attributes' key in search response to hold undecoded (binary) attribute values read from ldap
	- Added __repr__ for Server and Connection objects to re-create the object instance

* 0.4.2 - 2013.07.29
	- Added autoReferral feature as per RFC 4511 (4.1.10)
	- Added allowedReferralHosts to conform to Security considerations of RFC 4516

* 0.4.1 - 2013.07.20
	- Add validation to Abandon operation
	- Added connection.request to hold a dictionary of info about last request
	- Added info about outstanding operation in connection.strategy._oustanding
	- Implemented RFC 4515 foJ6311\\èr search filter coding and decoding
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
