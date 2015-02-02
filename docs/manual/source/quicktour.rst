##########
Quick tour
##########

To use ldap3 import the library from the ldap3 namespace. You can choose the strategy that the client will use to connect to the server.
 here are 5 strategies that can be used for establishing a connection: SYNC, ASYNC, LDIF, RESTARTABLE and REUSABLE.

With synchronous strategy (SYNC, RESTARTABLE) all LDAP operation requests return a boolean: True if they're successful, False if they fail.

With asynchronous strategies (ASYNC, REUSABLE) all LDAP operation requests (except Bind that returns a boolean) return an integer,
 the 'message_id' of the request. You can send multiple request without waiting for responses.

You can get each response with the get_response(message_id) method of the Connection object.If you get an exception the response has not yet arrived.
A timeout value can be specified (get_response(message_id, timeout = 20)) to set the number of seconds to wait for the response to appear (defaults is 10 seconds).

Library raises an exception in the LDAPExceptionError hierarchy to signal errors, the last exception message is stored in the last_error attribute of the Connection object when available.

After any operation, you'll find the following attributes populated in the Connection object:

* result: the result of the last operation (only synchronous strategies)

* response: the entries found if the last operation is a search operation (only for synchronous strategies)

* last_error: any error occurred in the last operation

* bound: True if bound else False

* listening: True if the socket is listening to the server

* closed: True if the socket is not open

You can have a LDIF representation of the response of a search with::

    connection.response_to_ldif()

or you can save the response to a JSON string::

    entries = connection.response_to_json()

or have the response saved to a file in JSON format::

    connection.response_to_json('entries-found.json')

Connections
-----------

You can create a connection with::

    # import class and constants
    from ldap3 import Server, Connection, SIMPLE, SYNC, ASYNC, SUBTREE, ALL

    # define the server and the connection
    s = Server('servername', port = 389, get_info = ALL)  # define an unsecure LDAP server, requesting info on DSE and schema
    c = Connection(s, auto_bind = True, client_strategy = SYNC, user='username', password='password', authentication=SIMPLE, check_names=True)
    print(s.info) # display info from the DSE. OID are decoded when recognized by the library

    # request a few objects from the LDAP server
    c.search('o=test','(objectClass=*)', SUBTREE, attributes = ['sn', 'objectClass'])
    response = c.response
    result = c.result
    for r in response:
        print(r['dn'], r['attributes']) # return unicode attributes
        print(r['dn'], r['raw_attributes']) return raw (bytes) attributes
    print(result)
    c.unbind()

To move from synchronous to asynchronous connection you have just to change the 'client_strategy' parameter to 'ASYNC' and substitute the *response* and *result* assignments with::

    response, result = c.get_response(result)

That's all you have to do to have an asynchronous threaded LDAP client connection.

To get operational attributes (createStamp, modifiedStamp, ...) for response objects add 'get_operational_attributes = True' in the search request::

    c.search('o=test','(objectClass=*)', SUBTREE, attributes = ['sn', 'objectClass'], get_operational_attributes = True)


After a search operation you can  access the connection.entries property, to get the search result in a more object oriented representation::

    c.search('o=test','(objectClass=*)', SUBTREE, attributes = ['sn', 'givenName', 'objectClass'], get_operational_attributes = True)
    for entry in c.entries:
        print(entry.entry_get_dn())
        print(entry.givenName, entry.sn)

    Look at "abstraction layer" for the description of the Entry object)

Connection context manager
--------------------------

Connections respond to the context manager protocol, so you can have automatic open, bind and unbind with the following syntax::

    from ldap3 import Server, Connection, SUBTREE
    s = Server('servername')
    c = Connection(s, user='username', password='password')
    with c:
        c.search('o=test','(objectClass=*)', SUBTREE, attributes = ['sn', 'objectClass'])
    print(c.response)

or, even shorter::

    from ldap3 import Server, Connection, SUBTREE
    with Connection(Server('servername'), user = 'username', password = 'password') as c
        c.search('o=test','(objectClass=*)', SUBTREE, attributes = ['sn', 'objectClass'])  # connection is opened, bound, searched and closed
    print(c.response)

The Connection object retains its state when entering the context, that is if the connection was closed and unbound it will remain closed and unbound when leaving the context,
if the connection was open or bound its state will be restored when exiting the context. Connection is always open and bound while in context.

Using the context manager connections will be opened and bound as you enter the Connection context and will be unbound when you leave the context.
Unbind will be tried even if the operations in context raise an exception.


Binding
-------

You can bind (authenticate) to the server with any of the authentication method defined in the LDAP v3 protocol: Anonymous, Simple and SASL.

You can perform an automatic bind with the auto_bind=True parameter of the connection object or performing a bind() operation that returns a boolean to indicate if bind was succcesful.

You can read the result of the bind operation in the 'result' attribute of the connection object. If auto_bind is not succesful the library will raise an LDAPBindError exception.

Searching
---------

Search operation is enhanced with a few parameters:

- get_operational_attributes: when True retrieves the operational (system generated) attributes for each of the result entries.
- paged_size: if greater than 0 the server returns a simple paged search response with the number of entries specified (LDAP server must conform to RFC2696).
- paged_cookie: used for subsequent retrieval of additional entries in a simple paged search.
- paged_criticality: if True the search should fail if simple paged search is not available on the server else a full search is performed.

If the search filter contains the following characters you must use the relevant escape ASCII sequence, as per RFC4515 (section 3):
 '*' -> '\\\\2A', '(' -> '\\\\28', ')' -> '\\\\29', '\\' -> '\\\\5C', chr(0) -> '\\\\00'

To search for a binary value you must use the RFC4515 escape ASCII sequence for each byte in the search assertion. You can use the function *escape_bytes()* in ldap3.utils.conv for properly escape a bytes object::

    from ldap3.utils.conv import escape_bytes
    guid = b'\xca@\xf2k\x1d\x86\xcaL\xb7\xa2\xca@\xf2k\x1d\x86'
    search_filter = '(guid=' + escape_bytes(guid) + ')'
    c.search('o=test', search_filter, attributes=['guid'])

search_filter will contain *'(guid=\\ca\\40\\f2\\6b\\1d\\86\\ca\\4c\\b7\\a2\\ca\\40\\f2\\6b\\1d\\86)'*
Raw values for the attributes retrieved are stored in the *raw_attributes* dictonary of the search result entries in c.response.
If the schema is read (with get_info=GET_SCHEMA_INFO (or GET_ALL_INFO in the Server object) and check_names is set to True in the Connection object the *attributes* is populated with the formatted values as specified by the RFCs and the schema syntaxes.
Custom formatters can be used to specify how an attribute value must be returned in the 'attributes' attribute of the search entry object.
A formatter must be a callable that receives a bytes value and return an object. The object will be returned in the 'attributes'.
If the attribute is defined in the schema as 'multi_value' the attribute value is returned as a list (even if only a single value is present) else it's returned as a single value.

Formatted (following the schema and RFC indications) attributes are stored in the *attributes* dictionary of the search result entries in c.response. This is performed only if the schema is read in the server object and the check_names parameter is set to True else the unicode value is returned.

Attributes key are case insensitive, this means that you can access c.response[0]['attributes']['postalAddress'] or c.response[0]['attributes']['postaladdress'] and get the same values back.


Simple Paged search
-------------------

The search operation can perform a *simple paged search* as per RFC2696. You must specify the required number of entries in each response set.
After the first search you must send back the cookie you get with each response in each subsequent search. If you send 0 as paged_size and a valid cookie the search operation referred by that cookie is abandoned.
Cookie can be found in connection.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']; the server may return an estimated total number of entries in
connection.result['controls']['1.2.840.113556.1.4.319']['value']['size'].
You can change the paged_size in any subsequent search request.

Example::

    from ldap3 import Server, Connection, SUBTREE
    total_entries = 0
    server = Server('test-server')
    c = Connection(server, user='username', password='password')
    c.search(search_base = 'o=test',
             search_filter = '(objectClass=inetOrgPerson)',
             search_scope = SUBTREE,
             attributes = ['cn', 'givenName'],
             paged_size = 5)
    total_entries += len(c.response)
    for entry in c.response:
        print(entry['dn'], entry['attributes])
    cookie = c.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
    while cookie:
        c.search(search_base = 'o=test',
                 search_filter = '(object_class=inetOrgPerson)',
                 search_scope = SUBTREE,
                 attributes = ['cn', 'givenName'],
                 paged_size = 5,
                 paged_cookie = cookie)
        total_entries += len(c.response)
        cookie = c.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
        for entry in c.response:
            print(entry['dn'], entry['attributes])
    print('Total entries retrieved:', total_entries)

Or you can use the much simpler extended operations package that wraps all this machinery and hides implementation details, you can choose to get back a generator or the whole list of entries found.


Working with a generator is better when you deal with very long list of entries or have memory issues::

    # generator
    total_entries = 0
    entry_generator = c.extend.standard.paged_search(search_base = 'o=test',
                                                     search_filter = '(objectClass=inetOrgPerson)',
                                                     search_scope = SUBTREE,
                                                     attributes = ['cn', 'givenName'],
                                                     paged_size = 5,
                                                     generator=True)
    for entry in entry_generator:
        total_entries += 1
        print(entry['dn'], entry['attributes])
    print('Total entries retrieved:', total_entries)

Remember that a generator can be consumed only one time, so you must elaborate the results in a sequential way.


Working with a list keeps all the found entries in a list and you can elaborate them in a random way::

    # whole result list
    entry_list = c.extend.standard.paged_search(search_base = 'o=test',
                                                search_filter = '(objectClass=inetOrgPerson)',
                                                search_scope = SUBTREE,
                                                attributes = ['cn', 'givenName'],
                                                paged_size = 5,
                                                generator=False)
    for entry in entry_list:
        print entry['attributes']
    total_entries = len(entry_list)
    print('Total entries retrieved:', total_entries)

