##########
Connection
##########

Connection object is used to send operation requests to the LDAP Server. It can use different connection strategies.
It supports the *context manager* protocol that automatically opens and closes the connection.

The following strategies are available:

* STRATEGY_SYNC: the request is sent and the connection waits until the response is received. You get the response as return value of the connection

* STRATEGY_ASYNC_THREADED: the request is sent and the connection immediately returns a *message_id* that can be later used to retrieve the response

* STRATEGY_SYNC_RESTARTABLE: an automatically restartable synchronous connection. It retries operation for the specified number of times of forever

* STRATEGY_LDIF_PRODUCER: the request is transformed in a *ldif-change* format and a ldif output is returned


Connection parameters are:

* server: the Server object to be contacted. It can be a ServerPool. In this case the ServerPool pooling strategy is followed when opening the connection

* user: the account of the user to log in for simple bind (defaults to None)

* password: the password of the user for simple bind (defaults to None)

* auto_bind: automatically opens and bind the connection (defaults to False)

* version: LDAP protocol version (defaults to 3)

* authentication: authentication method, can be one of AUTH_ANONYMOUS, AUTH_SIMPLE or AUTH_SASL. Defaults to AUTH_ANONYMOUS if user and password are both None else defaults to AUTH_SIMPLE

* client_strategy: communication strategy used by the client (defaults to STRATEGY_SYNC)

* auto_referrals: specify if the Connection must follows referrals automatically (defaults to True). Allowed referral servers are specified in the Server object

* sasl_mechanism: specify the SASL mechanism to use for AUTH_SASL authentication. Available mechanism are EXTERNAL and DIGEST-MD5 (**deprecated**)

* sasl_credential: an object specific to the SASL mechanism chosen. Look at documentation for each SASL mechanism supported

* collect_usage: binds a ConnectionUsage object to the connection to store metrics of connection usage (see later)

* read_only: inhibit modify, delete, add and modifyDn (move) operations


Through the connection you can perform all the standard LDAP operations:

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
   modify_dn is really a two-flavours operation: you can rename the last part of the dn *or* you move the entry in another container. You cannot perform both operation at the same time.

* Search: performs a search in the LDAP database


* Abandon: abandons the operation indicated by message_id, if possible

    * message_id: id of a previously sent request

    * controls: additional controls to be used in the request

* Extended: performs an extended operation

    * request_name: name of the extended operation

    * request_value: optional value sent in the request (defaults to None)

Additional methods defined:

* start_tls: establishes a secure connection, can be executed before or after the bind operation

* do_sasl_bind: performs a SASL bind with the parameter defined in the Connection. It's automatically executed when you call the bind operation if SASL authentication is used

    * controls: additional controls to be used in the request

* refresh_dsa_info: reads info from server as specified in the get_info parameter of the Connection object

* response_to_ldif: converts the response of a search to a LDIF format (ldif-content)

    * search_result: the result of the search to be converted (defaults to None). If None get the last response received from the Server

    * all_base64: converts all the value to base64 (defaults to False)

* close: an alias for the unbind operation
