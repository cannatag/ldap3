###########
Connections
###########

Connection object is used to send operation requests to the LDAP Server. It can use different connection strategies and supports the *context manager* protocol to automatically open, bind and unbind the connection.

The following strategies are available:

* STRATEGY_SYNC: the request is sent and the connection waits until the response is received. You get the response in the return value of the connection

* STRATEGY_ASYNC_THREADED: the request is sent and the connection immediately returns a *message_id* that can be used later to retrieve the response

* STRATEGY_SYNC_RESTARTABLE: an automatically restartable synchronous connection. It retries operation for the specified number of times of forever

* STRATEGY_LDIF_PRODUCER: the request is transformed in a *ldif-change* format and an LDIF output is returned

.. sidebar:: Lazy connections

   * In a lazy connection when you open() and bind() nothing is executed. These operation are deferred until an effective LDAP operation (add, modify, delete, compare, modifyDn, search, extended) is performed. If unbind() is executed when still in deferred status all deferred operation are cancelled and nothing is sent over the network. This can be helpful when your application opens connections ahead of knowing if an effective operation will be necessary.

* STRATEGY_REUSABLE_THREADED: an asynchronous strategy that internally opens multiple connections to the Server (or multiple Servers via the ServerPool) each in a different thread

When using an asynchronous strategy each operation returns immediately an operation_id. You can call the get_response method of the connection object to obtain the response received from the server.

Connection parameters are:

* server: the Server object to be contacted. It can be a ServerPool. In this case the ServerPool pooling strategy is followed when opening the connection

* user: the account of the user to log in for simple bind (defaults to None)

* password: the password of the user for simple bind (defaults to None)

* auto_bind: automatically opens and binds the connection. Can be AUTO_BIND_NONE, AUTO_BIND_NO_TLS, AUTO_BIND_TLS_AFTER_BIND, AUTO_BIND_TLS_BEFORE_BIND

* version: LDAP protocol version (defaults to 3)

* authentication: authentication method, can be one of AUTH_ANONYMOUS, AUTH_SIMPLE or AUTH_SASL. Defaults to AUTH_ANONYMOUS if user and password are both None else defaults to AUTH_SIMPLE

* client_strategy: communication strategy used by the client (defaults to STRATEGY_SYNC)

* auto_referrals: specify if the Connection must follows referrals automatically (defaults to True). Allowed referral servers are specified in the Server object

* sasl_mechanism: specify the SASL mechanism to use for AUTH_SASL authentication. Available mechanism are EXTERNAL and DIGEST-MD5 (**deprecated**)

* sasl_credential: an object specific to the SASL mechanism chosen. Look at documentation for each SASL mechanism supported

* collect_usage: binds a ConnectionUsage object to the connection to store metrics of connection usage (see later)

* read_only: inhibit modify, delete, add and modifyDn (move) operations

* lazy: when True connection will defer open and bind until another LDAP operation is requested

* check_names: when True attribute names in assertion and in filter will be checked against the schema (Server must have schema infos loaded with the get_info parameter)

* raise_exceptions: when True LDAP operations will raise exceptions (subclasses of LDAPOperationResult) when the result is not one of the following: RESULT_SUCCESS, RESULT_COMPARE_FALSE, RESULT_COMPARE_TRUE, RESULT_REFERRAL.

With the connection you can perform all the standard LDAP operations:

* bind: performs a bind to the LDAP Server with the authentication type and credential specified in the connection

    * controls: additional controls to be used in the request

* unbind: disconnect and close the connection

    * controls: additional controls to be used in the request

* compare: performs a comparison between an attribute value of an entry and an arbitrary value

    * dn: distinguish name of the entry whose attribute you want to compare

    * attribute: name of the attribute to compare

    * value: value to be compared

    * controls: additional controls to be used in the request

* add: add an entry to the LDAP server

    * dn: distinguish name of the object to add

    * object_class: class name of the attribute to add, can be a string containing a single value or a list of strings

    * attributes: a dictionary in the form {'attr1': 'val1', 'attr2': 'val2', ...} or {'attr1': ['val1', 'val2', ...], ...} for multivalued attributes

* delete: deletes the object specified

    * dn: distinguish name of the object to delete

    * controls: additional controls to be used in the request

* modify: modifies attributes of an entry

    * dn: distinguish name of the object whose attributes must be modified

    * changes: a dictionary in the form {'attribute1': [(operation, [val1, val2, ...])], 'attribute2': [(operation, [val1, val2, ...])]}, operation is MODIFY_ADD, MODIFY_DELETE, MODIFY_REPLACE, MODIFY_INCREMENT

    * controls: additional controls to be used in the request

* modify_dn: modifies relative distinguished name of an entry or performs a move of an entry

    * dn: distinguish name of the entry whose relative name must be modified

    * relative_dn: new relative dn of the entry

    * delete_old_dn: remove the previous dn (defaults to True)

    * new_superior: the new container of the entry

    * controls: additional controls to be used in the request

.. note::

   modify_dn is really a two-flavours operation: you can rename the last part of the dn *or* you move the entry in another container but you cannot perform both operations at the same time.

* Search: performs a search in the LDAP database

    * search_base: base of the search request

    * search_filter: filter of the search request. It must conform to the LDAP filter syntax specified in RFC4515. If the search filter contains the following characters you must use the relevant escape ASCII sequence, as per RFC4515 (section 3): '*' -> '\\\\2A', '(' -> '\\\\28', ')' -> '\\\\29', '\\' -> '\\\\5C', chr(0) -> '\\\\00'

    * search_scope: specifies how broad the search context is:

        * SEARCH_SCOPE_BASE_OBJECT: retrieves attributes of the entry specified in the search_base

        * SEARCH_SCOPE_SINGLE_LEVEL: retrieves attributes of the entries specified in the search_base. The base must reference a container object

        *  SEARCH_SCOPE_WHOLE_SUBTREE: retrieves attributes of the entries specified in the search_base and all subordinate containers downward.

    * dereference_aliases: specifies how the server must treat references to other entries:

        * SEARCH_NEVER_DEREFERENCE_ALIASES: never dereferences entries, returns alias objects instead. The alias contains the reference to the real entry

        * SEARCH_DEREFERENCE_IN_SEARCHING: while searching subordinates of the base object, dereferences any alias within the search scope. Dereferenced objects become the vertices of further search scopes where the       Search operation is also applied. The server should eliminate duplicate entries that arise due to alias dereferencing while searching.

        * SEARCH_DEREFERENCE_FINDING_BASE_OBJECT: dereferences aliases in locating the base object of the search, but not when searching subordinates of the base object.

        * SEARCH_DEREFERENCE_ALWAYS: always returns the referenced entries, not the alias object

    * attributes: a single attribute or a list of attributes to be returned by the search (defaults to None). If attributes is None  no attribute is returned. If attributes is ALL_ATTRIBUTES all attributes are returned

    * size_limit: maximum number of entries returned by the search (defaults to None). If None the whole set of found entries is returned, unless the server has a more restrictive rule.

    * time_limit: number of seconds allowed for the search (defaults to None). If None the search can take an unlimited amount of time, unless the server has a more restrictive rule.

    * types_only: never returns attribute values

    * get_operational_attributes: if True returns information attributes mananged automatically by the server for  each entry

    * controls: additional controls to be used in the request

    * paged_size: if paged_size is greater than 0 a simple paged search is executed as described in RFC2696 (defaults to None). The search will return at most the specified number of entries

    * paged_criticality: if True the search will be executed only if the server is capable of performing a simple paged search. If False and the server is not capable of performing a simple paged search a standard search will be executed.

    * paged_cookie: an *opaque* string received in the last paged search that must be sent while requesting subsequent entries of the search result

* Abandon: abandons the operation indicated by message_id, if possible

    * message_id: id of a previously sent request

    * controls: additional controls to be used in the request

* Extended: performs an extended operation

    * request_name: name of the extended operation

    * request_value: optional value sent in the request (defaults to None)

    * controls: additional controls to be used in the request


Additional methods defined:

* start_tls: establishes a secure connection, can be executed before or after the bind operation

* do_sasl_bind: performs a SASL bind with the parameter defined in the Connection. It's automatically executed when you call the bind operation if SASL authentication is used

* refresh_dsa_info: reads info from server as specified in the get_info parameter of the Connection object

* response_to_ldif: a method you can call to convert the response of a search to a LDIF format (ldif-content). It has the following parameters:

    * search_result: the result of the search to be converted (defaults to None). If None get the last response received from the Server

    * all_base64: converts all the value to base64 (defaults to False)

* close: an alias for the unbind operation

Connection attributes:

* server: the active Server object used in the connection

* server_pool: the ServerPool object used in the connection if available

* read_only: True if the connection is in read only mode

* version: the LDAP protocol version used

* result: the result of the last operation

* response: the response of the last operation (for example, the entries found in a search), without the result

* last_error: any error occurred in the last operation

* bound: True if bound to server else False

* listening: True if the socket is listening to the server

* closed: True if the socket is not open

* strategy_type: the strategy type used by the connection

* strategy: the strategy instance used by the connection

* authentication: the authentication type used in the connection

* user: the user name for simple bind

* password: password for simple bind

* auto_bind: True if auto_bind is active else False

* tls_started: True if the Transport Security Layer is active

* usage: metrics of connection usage

* lazy: connection will defer open and bind until another LDAP operation is requested

* check_names: True if you want to check the attribute and object class names against the schema in filters and in add/compare/modify operations (:class: requested by RFC)

* pool_name: an identifier for the Connection pool when using a pooled connection strategy

* pool_size: size of the connection pool used in a pooled connection strategy

* pool_lifetime: number of second before recreating a new connection in a pooled connection strategy

Simple Paged search
-------------------

The search operation can perform a *simple paged search* as per RFC2696. You must specify the required number of entries in each response set. After the first search you must send back the cookie you get with each response in each subsequent search. If you send 0 as paged_size and a valid cookie the search operation referred by that cookie is abandoned.
Cookie can be found in connection.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']; the server may return an estimated total number of entries in connection.result['controls']['1.2.840.113556.1.4.319']['value']['size']. You can change the paged_size in any subsequent search request.

Example::

    from ldap3 import Server, Connection, SEARCH_SCOPE_WHOLE_SUBTREE
    total_entries = 0
    server = Server('test-server')
    connection = Connection(server, user='test-user', password='test-password', auto_bind=True)
    connection.search(search_base='o=test', search_filter='(objectClass=inetOrgPerson)', search_scope=SEARCH_SCOPE_WHOLE_SUBTREE,
                      attributes=['cn', 'givenName'], paged_size=5)
    total_entries += len(connection.response)
    cookie = self.connection.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
    while cookie:
        connection.search(search_base = 'o=test', search_filter = '(object_class=inetOrgPerson)', search_scope = SEARCH_SCOPE_WHOLE_SUBTREE,
                          attributes = ['cn', 'givenName'], paged_size = 5, paged_cookie = cookie)
        total_entries += len(connection.response)
        cookie = self.connection.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
    print('Total entries retrieved:', total_entries)
    connection.close()

Controls
========
Controls, if used, must be a list of tuples. Each tuple must have 3 elements: the control OID, a boolean to specify if the control is critical, and a value. If the boolean is set to True the server must honorate the control or refuse the operation. Mixing controls must be defined in controls specification (as per RFC4511)


Responses
=========

Responses are received and stored in the connection.response as a list of dictionaries.
You can get the search result entries of a Search operation iterating over the response attribute. Each entry is a dictionary with the following field:
* dn: the distinguished name of the entry
* attributes: a dictionary of returned attributes and their values. Values are list. Values are in UTF-8 format.
* raw_attributes: same as 'attributes' but not encoded (bytearray)

Result
======

Each operation has a result stored as a dictionary in the connection.result attribute.
You can check the result value to know if the operation has been sucessful. The dictionary has the following field:
* result: the numeric result code of the operation as specified in RFC4511
* description: extended description of the result code, as specified in RFC4511
* message: a diagnostic message sent by the server (optional)
* dn: a distinguish name of an entry related to the request (optional)
* referrals: a list of referrals where the operation can be continued (optional)


Checked Attributes
==================
The checked attributes feature checks the LDAP syntax of the atttributes defined in schema and returns a properly formatted entry result while performing searches. This means that if you have an attributes specified as GUID in the server schema you will get the properly formatted GUID value (for example '012381d3-3b1c-904f-b29a-012381d33b1c') in the connection.response[0]['checked_attributes'] key dictionary instead of a sequence of bytes. Or if you request an attribute defined as an Interger in the schema you will get the value already converted to int.
Furthermore for attributes defined as single valued in schema you will get the value instead of a list of values (that would always be one sized). To activate this feature you must set the get info to GET_SCHEMA_INFO or GET_ALL_INFO value when defining the server object and the 'check_names' attributes to True in the Connection object (this is True by default starting from 0.9.4).

There are a few of standard formatters defined in the library, most of them are defined in the relevants RFCs:
format_unicode  # returns an unicode object in Python 2 and a string in Python 3
format_integer  # returns an integer
format_binary  # returns a bytes() sequence
format_uuid  # returns a GUID (UUID) as specified in RFC 4122 - byte order is big endian
format_uuid_le  # same as above but byte order is little endian
format_boolean  # returns a boolean
format_time  # returns a datetime object (with properly defined timezone, or UTC if timezone is not specified) as defined in RFC 4517

You can even define your custom formatter for specific purposes. Just pass a dictionary in the format {'identifier': callable} in the 'formatter' parameter of the Server object. The callable must be able to receive a single byte value and convert it the relevant object or class instance.

The resolution order of the format feature is the following:
Custom formatters have precedence over standard formatter. In each category (from highest to lowest):
1. attribute name
2. attribute oid(from schema)
3. attribute names (from oid_info)
4. attribute syntax (from schema)
If a suitable formatter is not found the value will be rendered as bytes