##########
Quick tour
##########

You have to import the library from the ldap3 namespace.
You can choose the strategy the client will use to connect to the server. There are 2 strategy defined: 'syncWait' and 'asyncThreaded'.

With synchronous strategy (syncWait) all LDAP operations return a boolean: True if they're successful, False if they fail.

With asynchronous strategy (asyncThreaded) all LDAP operations request (except Bind) return an integer, the 'messageId' of the request.
You can send multiple request without waiting for responses. You can get the response with the get_response(messageId) method of the Connection object.
If you get None the response has not yet arrived. You can set a timeout (get_response(messageId, timeout = 10)) to set the number of seconds to wait for the response to appear.

Library raise LDAPException to signal errors, last exception message is stored in the lastError attribute of the Connection object when available.

After any operation, either synchronous or asynchronous, you'll find the following attributes populated in the Connection object:

- result: the result of the last operation
- response: the response of the last operation (for example, a search)
- lastError: any error occurred in the last operation
- bound: True if bound else False
- listening: True if the socket is listening to the server
- closed: True if the socket is not open
- response_to_ldif(): response in LDIF format


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
            print(r['dn'], r['raw_attributes']) return raw (bytes) attributes
    else:
        print('result', conn.result)
    c.unbind()

To move from synchronous to asynchronous connection you have just to change the 'clientStrategy' to 'STRATEGY_ASYNC_THREADED' and add the following line before the 'if result:'::

    c.get_response(result, timeout = 10)

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
