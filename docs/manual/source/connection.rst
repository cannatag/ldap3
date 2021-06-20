Connection
##########

The Connection object is used to send operation requests to the LDAP Server. It can use different connection strategies and supports the *context manager* protocol to automatically open, bind and unbind the connection.

The following strategies are available:

* SYNC: the request is sent and the connection waits until the response is received. You get the result in the return value of the connection.

* ASYNC: the request is sent and the connection immediately returns a *message_id* that can be used later to retrieve the response. Safe for multithreaded programs.

* LDIF: the request is transformed in a *ldif-change* format and an LDIF output is returned.

* RESTARTABLE: an automatically restartable synchronous connection. It retries operation for the specified number of times or forever.

* REUSABLE: an asynchronous strategy that internally opens multiple connections to the Server (or multiple Servers via the ServerPool) each in a different thread

* SAFE_SYNC: the request is sent and the connection waits until the response is received. Each operation returns a tuple of 4 elements: status, result, response, request. This strategy is thread-safe.

* SAFE_RESTARTABLE: the request is sent and the connection waits until the response is received. Each operation returns a tuple of 4 elements: status, result, response, request, connection restarts if failing for the specified number of times or forever. This strategy is thread-safe.

.. note::
   **SafeSync** and **SafeRestartable** strategies can be used in multithreaded programs.
   Each LDAP operation with the SafeSync or SafeRestartable strategies returns a tuple of four elements: status, result, response and request.

   * status: states if the operation was successful

   * result: the LDAP result of the operation

   * response: the response of a LDAP Search Operation

   * request: the original request of the operation::

      from ldap3 import Server, Connection, SAFE_SYNC
      server = Server('my_server')
      conn = Connection(s, 'my_user', 'my_password', client_strategy=SAFE_SYNC, auto_bind=True)
      status, result, response, _ = conn.search('o=test', '(objectclass=*)')  # usually you don't need the original request (4th element of the return tuple)

   The SafeSync and SafeRestartable strategies can be used with the Abstract Layer, but the Abstract Layer currently is NOT thread safe.


.. note:: Lazy connections

   In a lazy connection when you open() and bind() nothing is executed. These operation are deferred until an effective LDAP operation (add, modify, delete, compare, modifyDn, search, extended) is performed. If unbind() is executed when still in deferred status all deferred operation are cancelled and nothing is sent over the network. This can be helpful when your application opens connections ahead of knowing if an effective operation is needed.



When using an asynchronous strategy each operation returns immediately a message_id. You can call the get_response method of the connection object to obtain the response received from the server.



Connection parameters are:

* server: the Server object to be contacted. It can be a ServerPool. In this case the ServerPool pooling strategy is followed when opening the connection. You can also pass a string containing the name of the server. In this case the Server object is implicitly created with default values.
* user: the account of the user to log in for simple bind (defaults to None).

* password: the password of the user for simple bind (defaults to None)

* auto_bind: automatically opens and binds the connection. Can be AUTO_BIND_NONE, AUTO_BIND_NO_TLS, AUTO_BIND_TLS_AFTER_BIND, AUTO_BIND_TLS_BEFORE_BIND.

* version: LDAP protocol version (defaults to 3).

* authentication: authentication method, can be one of ANONYMOUS, SIMPLE, SASL or NTLM. Defaults to ANONYMOUS if user and password are both None else defaults to SIMPLE. NTLM uses NTLMv2 authentication. Username must be in the form domain\\user.

* client_strategy: communication strategy used by the client (defaults to SYNC).

* auto_referrals: specify if the Connection must follows referrals automatically (defaults to True). Allowed referral servers are specified in the Server object.

* sasl_mechanism: specify the SASL mechanism to use for SASL authentication. Available mechanism are EXTERNAL, DIGEST-MD5 (**deprecated** by RFCs because insecure) and GSSAPI.

* sasl_credential: an object specific to the SASL mechanism chosen. Refer to the documentation for each SASL mechanism supported.

* collect_usage: binds a ConnectionUsage object to the connection to store metrics of connection usage (see later).

* read_only: when True inhibits modify, delete, add and modifyDn (move) operations, defaults to False.

* lazy: when True connection will defer open and bind until another LDAP operation is requested

* check_names: when True attribute names in assertions and filters will be checked against the schema (Server must have schema loaded with the get_info=ALL or get_info=SCHEMA parameter) and search result will be formatted as specified in schema.

* raise_exceptions: when True LDAP operations will raise exceptions (subclasses of LDAPOperationResult) when the result is not one of the following: RESULT_SUCCESS, RESULT_COMPARE_FALSE, RESULT_COMPARE_TRUE, RESULT_REFERRAL.

* pool_name: an optional identifier for the Connection pool when using a pooled connection strategy

* pool_size: size of the connection pool used in a pooled connection strategy

* pool_lifetime: number of seconds before recreating a new connection in a pooled connection strategy

* pool_keepalive: number of seconds to wait before sending an Abandon(0) operation in an idle connection in a pooled connection strategy. Abandon(0) is an harmless LDAP operation used to not let the server closing the connection

* fast_decoder: when False use the pyasn1 decoder instead of the faster internal decoder. Gives a better output in extended log

* receive_timeout: set the socket in non-blocking mode - raising an exception after the specified amount of seconds if nothing is received over the wire

* return_empty_attributes: when a search is performed if an attribute is empty then sets its value to an empty list, default to True

* auto_range: if a server returns a fixed amount of entries in searches using the *range* tag (RFCs 3866) setting this value to True let the ldap3 library automatically request all entries with additional searches. The entries are returned as if a single search is performed

* use_referral_cache: when True referral connections are not immediately closed, and kept in a cache should another request need to contact the same server

* auto_escape: automatically applies LDAP encoding to filter values, default to True

* auto_encode: automatically tries to convert from local encoding to UTF8 for well known syntaxes and types, default to True


.. note::
   The *auto_range* feature is very useful when searching Active Directory servers. When an Active Directory search returns more than 1000 entries this feature is automatically used by the server.
   So it can happens that your code works seamlessy until your data grow to exceed the 1000 entries limit and your code stops working properly without any apparent reason.

With the connection object you can perform all the standard LDAP operations:

* bind: performs a bind to the LDAP Server with the authentication type and credential specified in the connection:

    * controls: additional controls to send in the request


.. note::
   When binding with a username from an untrusted source (as a user typing it in a terminal
   or in a web page) you should perform ``escape_rdn(username)`` to ensure that the input value doesn't contain any illegal character. The escape_rdn() function is in the ldap3.utils.dn namespace.

* unbind: disconnect and close the connection:

    * controls: additional controls to send in the request

* compare: performs a comparison between an attribute value of an entry and an arbitrary value:

    * dn: distinguished name of the entry whose attribute is to compare

    * attribute: name of the attribute to compare

    * value: value to be compared

    * controls: additional controls to send in the request

* add: add an entry to the LDAP server

    * dn: distinguished name of the object to add

    * object_class: class name of the attribute to add, can be a string containing a single value or a list of strings

    * attributes: a dictionary in the form {'attr1': 'val1', 'attr2': 'val2', ...} (or {'attr1': ['val1', 'val2', ...], ...} for multivalued attributes)

    * controls: additional controls to send in the request

* delete: deletes the object specified:

    * dn: distinguished name of the object to delete

    * controls: additional controls to send in the request

* modify: modifies attributes of an entry:

    * dn: distinguished name of the object whose attributes must be modified

    * changes: a dictionary in the form {'attribute1': [(operation1, [val1, val2, ...]), (operation2, [val1, val2, ...]), ...]}, operation is MODIFY_ADD, MODIFY_DELETE, MODIFY_REPLACE, MODIFY_INCREMENT

    * controls: additional controls to send in the request

* modify_dn: modifies the relative distinguished name of an entry or performs a move of an entry:

    * dn: distinguished name of the entry whose relative name must be modified

    * relative_dn: new relative dn of the entry

    * delete_old_dn: remove the previous dn (defaults to True)

    * new_superior: the new container of the entry

    * controls: additional controls to send in the request

.. note::

   modify_dn is really a two-flavours operation: you can rename the last part of the dn *or* you move the entry in another container but you cannot perform both operations at the same time.

* Search: performs a search in the LDAP database:

    * search_base: the base of the search request.

    * search_filter: the filter of the search request. It must conform to the LDAP filter syntax specified in RFC4515.
      If the search filter contains the following characters you must use the relevant escape ASCII sequence, as per RFC4515
      (section 3): '*' -> '\\\\2A', '(' -> '\\\\28', ')' -> '\\\\29', '\\' -> '\\\\5C', chr(0) -> '\\\\00'.

    * search_scope: specifies how broad the search context is:

        * BASE: retrieves attributes of the entry specified in the search_base.

        * LEVEL: retrieves attributes of the entries specified in the search_base. The base must reference a container object.

        * SUBTREE: retrieves attributes of the entries specified in the search_base and all subordinate containers downward.

    * dereference_aliases: specifies how the server must treat references to other entries:

        * DEREF_NEVER: never dereferences entries, returns alias objects instead. The alias contains the reference to the real entry.

        * DEREF_SEARCH: while searching subordinates of the base object, dereferences any alias within the search scope.
          Dereferenced objects become the bases of further search scopes where the Search operation is also applied.
          The server should eliminate duplicate entries that arise due to alias dereferencing while searching.

        * DEREF_BASE: dereferences aliases in locating the base object of the search, but not when searching subordinates
          of the base object.

        * DEREF_ALWAYS: always returns the referenced entries, not the alias object.

    * attributes: a single attribute or a list of attributes to be returned by the search (defaults to None).
      If attributes is None no attribute is returned. If attributes=ALL_ATTRIBUTES all attributes are returned,
      if attributes=ALL_OPERATIONAL_ATTRIBUTES all operational attributes are returned. To get both use
      attributes=[ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES].


    * size_limit: maximum number of entries returned by the search (defaults to None).
      If None the whole set of found entries is returned, unless the server has a more restrictive constrai.

    * time_limit: number of seconds allowed for the search (defaults to None).
      If None the search can take an unlimited amount of time, unless the server has a more restrictive constrain.

    * types_only: doesn't return attribute values.

    * get_operational_attributes: if True returns information attributes (managed automatically by the server) for each entry.

    * controls: additional controls to send in the request.

    * paged_size: if paged_size is greater than 0 a simple paged search is executed as described in RFC2696 (defaults to None).
      The search will return at most the specified number of entries.

    * paged_criticality: if True the search will be executed only if the server is capable of performing a simple paged search.
      If False and the server is not capable of performing a simple paged search a standard search will be executed.

    * paged_cookie: an *opaque* string received in a paged paged search that must be sent back while requesting
      subsequent entries of the search result.

* Abandon: abandons the operation indicated by message_id, if possible:

    * message_id: id of a previously sent request

    * controls: additional controls to send in the request to be abandoned

* Extended: performs an extended operation:

    * request_name: name of the extended operation

    * request_value: optional value sent in the request (defaults to None)

    * controls: additional controls to send in the request

    * no_encode: when True the value is passed without any encoding (defaults to False)


Additional methods defined:

* start_tls: establishes a secure connection, can be executed before or after the bind operation.

* do_sasl_bind: performs a SASL bind with the parameter defined in the Connection. It's automatically executed when you call the bind operation if SASL authentication is used.

* refresh_dsa_info: reads info from server as specified in the get_info parameter of the Connection object.

* response_to_ldif: a method you can call to convert the response of a search to a LDIF format (ldif-content). It has the following parameters:

    * search_result: the result of the search to be converted (defaults to None). If None get the last response received from the Server

    * all_base64: converts all the value to base64 (defaults to False)

* response_to_json: this method returns the entries found in a search in a string with JSON format

* response_to_file: this method saves to a file the entries found in a search with JSON format. You can specify if you want the raw attributes with the raw=True parameter. Entries are saved as a list in the 'entries' key.

Connection attributes:

* server: the active Server object used in the connection

* server_pool: the ServerPool object used in the connection if available

* read_only: True if the connection is in read only mode

* version: the LDAP protocol version used

* result: the result of the last operation

* response: the response of the last operation (for example, the entries found in a search), without the result

* last_error: any error occurred in the last operation (for synchronous strategies)

* bound: True if bound to server else False

* listening: True if the socket is listening to the server

* closed: True if the socket is not open

* strategy_type: the client strategy type used by the connection

* strategy: the strategy instance used by the connection

* authentication: the authentication type used in the connection

* user: the user name for simple bind

* password: password for simple bind

* auto_bind: True if auto_bind is active else False

* tls_started: True if the Transport Security Layer is active

* usage: metrics of connection usage

* lazy: connection will defer open and bind until another LDAP operation is requested

* check_names: True if you want to check the attribute and object class names against the schema in filters and in add/compare/modify operations

* pool_name: an optional identifier for the Connection pool when using a pooled connection strategy

* pool_size: size of the connection pool used in a pooled connection strategy

* pool_lifetime: number of seconds before recreating a new connection in a pooled connection strategy

Controls
========
Controls, if used, must be a list of tuples. Each tuple must have 3 elements: the control OID, a boolean to specify if the control is critical,
and a value. If the boolean is set to True the server must honorate the control or refuse the operation. Mixing controls must be defined
in controls specification (as per RFC4511). controlValue is optional, set it to None to not send any value.


Result
======

Each operation has a result stored as a dictionary in the connection.result attribute.
You can check the result value to know if the operation has been sucessful. The dictionary has the following field:

* result: the numeric result code of the operation as specified in RFC4511

* description: extended description of the result code, as specified in RFC4511

* message: a diagnostic message sent by the server (optional)

* dn: a distinguish name of an entry related to the request (optional)

* referrals: a list of referrals where the operation can be continued (optional)


Responses
=========

Responses are received and stored in the connection.response as a list of dictionaries.
You can get the search result entries of a Search operation iterating over the response attribute.
Each entry is a dictionary with the following field:

* dn: the distinguished name of the entry

* attributes: a dictionary of returned attributes and their values. Values are in UTF-8 format. If the Connection is aware of the server schema,
  values are properly stored: directly for single-valued attributes and as a list for multi-valued attributes. A multi-valued attribute
  with a single value is always stored as a list. If the server schema is unkwown all values are stored as a list.


* raw_attributes: the unencoded values, always stores as a list of bytearray regardless of the schema definition.


Checked Attributes
==================
The checked attributes feature checks the LDAP syntax of the attributes defined in schema and returns a properly formatted entry value while performing searches.
This means that if, for example, you have an attributes specified as GUID in the server schema you will get the properly formatted GUID value ('012381d3-3b1c-904f-b29a-012381d33b1c') in the connection.response[0]['attributes'] key dictionary instead of a sequence of bytes.
Or if you request an attribute defined as an Integer in the schema you will get the value already converted to int.
Furthermore for attributes defined *single valued* in the schema you will get the value instead of a list containing only one value.
To activate this feature you must set the get_info parameter to SCHEMA or ALL when defining the server object and the check_names attributes to True in the Connection object (the default).

There are some standard formatters defined in the library, most of them are defined in the relevants RFCs:

* format_unicode  # returns an unicode object in Python 2 and a string in Python 3

* format_integer  # returns an integer

* format_binary  # returns a bytes() sequence

* format_uuid  # returns a GUID (UUID) as specified in RFC 4122 - byte order is big endian

* format_uuid_le  # same as above but byte order is little endian

* format_boolean  # returns a boolean

* format_time  # returns a datetime object (with properly defined timezone, or UTC if timezone is not specified) as defined in RFC 4517

You can even define your custom formatter for specific purposes. Just pass a dictionary in the format {'identifier': callable}
in the 'formatter' parameter of the Server object. The callable must be able to receive a bytes value and convert it to the relevant object or class instance.

Custom formatters have precedence over standard formatter. In each category (from highest to lowest) the resolution order is:

1. attribute name

2. attribute oid (from schema)

3. attribute names (from oid_info)

4. attribute syntax (from schema)

If a suitable formatter is not found the value will be rendered as bytes.
