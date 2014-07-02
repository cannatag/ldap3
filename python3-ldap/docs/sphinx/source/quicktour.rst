##########
Quick tour
##########

To use python3-ldap import the library from the ldap3 namespace. You can choose the strategy that the client will use to connect to the server. There are 4 strategies that can be used for establishing a connection: STRATEGY_SYNC, STRATEGY_ASYNC_THREADED, STRATEGY_LDIF_PRODUCER and STRATEGY_SYNC_RESTARTABLE

With synchronous strategy (STRATEGY_SYNC and STRATEGY_SYNC_RESTARTABLE) all LDAP operation requests return a boolean: True if they're successful, False if they fail.

With asynchronous strategies (STRATEGY_ASYNC_THREADED) all LDAP operation requests (except Bind) return an integer, the 'message_id' of the request. You can send multiple request without waiting for responses.

You can get each response with the get_response(message_id) method of the Connection object. If you get None the response has not yet arrived. A timeout can be specified (get_response(message_id, timeout = 20)) to set the number of seconds to wait for the response to appear or the default value will be used.

Library raises LDAPException to signal errors, the last exception message is stored in the last_error attribute of the Connection object when available.

After any operation, either synchronous or asynchronous, you'll find the following attributes populated in the Connection object:

* result: the result of the last operation
* response: the response of the last operation (for example, the entries found in a search)
* last_error: any error occurred in the last operation
* bound: True if bound else False
* listening: True if the socket is listening to the server
* closed: True if the socket is not open

You can  have a LDIF representation of the response of a search with::

    connection.response_to_ldif()

Connections
-----------

You can create a connection with::

    # import class and constants
    from ldap3 import Server, Connection, AUTH_SIMPLE, STRATEGY_SYNC, STRATEGY_ASYNC_THREADED, SEARCH_SCOPE_WHOLE_SUBTREE, GET_ALL_INFO

    # define the server and the connection
    s = Server('servername', port = 389, get_info = GET_ALL_INFO)  # define an unsecure LDAP server, requesting info on DSE and schema
    c = Connection(s, auto_bind = True, client_strategy = STRATEGY_SYNC, user='username', password='password', authentication=AUTH_SIMPLE)
    print(s.info) # display info from the DSE. OID are decoded when recognized by the library

    # request a few objects from the LDAP server
    c.search('o=test','(objectClass=*)', SEARCH_SCOPE_WHOLE_SUBTREE, attributes = ['sn', 'objectClass'])
    response = c.response
    result = c.result
    for r in response:
        print(r['dn'], r['attributes']) # return unicode attributes
        print(r['dn'], r['raw_attributes']) return raw (bytes) attributes
    print(result)
    c.unbind()

To move from synchronous to asynchronous connection you have just to change the 'client_strategy' parameter to 'STRATEGY_ASYNC_THREADED' and substitute the *response* and *result* assignments with::

    response, result = c.get_response(result)

That's all you have to do to have an asynchronous threaded LDAP client connection.

To get operational attributes (createStamp, modifiedStamp, ...) for response objects add 'get_operational_attribute = True' in the search request::

    c.search('o=test','(objectClass=*)', SEARCH_SCOPE_WHOLE_SUBTREE, attributes = ['sn', 'objectClass'], get_operational_attribute = True)

Connection context manager
--------------------------

Connections respond to the context manager protocol, so you can have automatic open, bind and unbind with the following syntax::

    from ldap3 import Server, Connection
    s = Server('servername')
    c = Connection(s, user = 'username', password = 'password')
    with c:
        c.search('o=test','(objectClass=*)', SEARCH_SCOPE_WHOLE_SUBTREE, attributes = ['sn', 'objectClass'])
    print(c.response)

or, even shorter::

    from ldap3 import Server, Connection
    with Connection(Server('servername'), user = 'username', password = 'password') as c
        c.search('o=test','(objectClass=*)', SEARCH_SCOPE_WHOLE_SUBTREE, attributes = ['sn', 'objectClass'])  # connection is opened, bound, searched and closed
    print(c.response)

The Connection object retains its state when entering the context, that is if the connection was closed and unbound it will remain closed and unbound when leaving the context,
if the connection was open or bound its state will be restored when exiting the context. Connection is always open and bound while in context.

Using the context manager connections will be opened and bound as you enter the Connection context and will be unbound when you leave the context.
Unbind will be tried even if the operations in context raise an exception.

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
Raw values for the attributes retrieved are stored in the *raw_attributes* dictonary of the search resulty entries in c.response.

Simple Paged search
-------------------

The search operation can perform a *simple paged search* as per RFC2696. You must specify the required number of entries in each response set.
After the first search you must send back the cookie you get with each response in each subsequent search. If you send 0 as paged_size and a valid cookie the search operation referred by that cookie is abandoned.
Cookie can be found in connection.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']; the server may return an estimated total number of entries in
connection.result['controls']['1.2.840.113556.1.4.319']['value']['size'].
You can change the paged_size in any subsequent search request.

Example::

    from ldap3 import Server, Connection, SEARCH_SCOPE_WHOLE_SUBTREE
    total_entries = 0
    server = Server('test-server')
    c = Connection(server, user = 'username', password = 'password')
    c.search(search_base = 'o=test', search_filter = '(objectClass=inetOrgPerson)', search_scope = SEARCH_SCOPE_WHOLE_SUBTREE,
                      attributes = ['cn', 'givenName'], paged_size = 5)
    total_entries += len(c.response)
    cookie = self.c.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
    while cookie:
        c.search(search_base = 'o=test', search_filter = '(object_class=inetOrgPerson)', search_scope = SEARCH_SCOPE_WHOLE_SUBTREE,
                          attributes = ['cn', 'givenName'], paged_size = 5, paged_cookie = cookie)
        total_entries += len(c.response)
        cookie = self.c.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
    print('Total entries retrieved:', total_entries)
    c.unbind()

