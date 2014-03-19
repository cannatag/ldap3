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


The connection exposes the following methods:
