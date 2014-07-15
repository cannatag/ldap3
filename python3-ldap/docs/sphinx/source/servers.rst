#######
Servers
#######

Server object
-------------
The Server object specify the DSA (Directory Server Agent) LDAP server that will be used by the connection. To create a new Server object the following parameters are available:

* host: name or ip of the server (required)

* port: the port where the DSA server is listening (defaults to 386, for a cleartext connection)

* use_ssl: specifies if the connection is on a secure port (defaults to False). When True the secure port is usually set to 636

* allowed_referral_hosts: specifies which servers are considered reliable as referrals (defaults to None)

    * Format is a list of tuples; [(server, allow_auth), (server, allow_auth), ...]

    * server is an IP address or DNS name. Specify an asterisk (*) to accept any server.

    * allow_auth is a boolean to indicate if authentication to that server is allowed; if False only anonymous bind will be used.

* get_info: specifies if the server schema and info must be read (defaults to GET_NO_INFO). Possible values are:

    * GET_NO_INFO: no information is gathered from the server

    * GET_DSA_INFO: server information is stored in server.info

    * GET_SCHEMA_INFO: schema information is stored in server.schema

    * GET_ALL_INFO: server and schema information are gathered and stored in server.info and server.schema

* tls: Tls object that contains information about the certificates and the trusted roots needed to establish a secure connection (defaults to None). If None any server certificate will be accepted.

Example::

    server = Server('server1', port = 636, use_ssl = True, allowed_referral_hosts = [('server2', True), ('server3', False)])

Server Pool
-----------

.. sidebar:: Active strategies

   *ACTIVE* strategies can check if the server is listening on the specified port. When the 'active' attribute is set to True the strategy tries to open and close a socket on the port. If your LDAP server has problems with the opening and closing of sockets you can set 'active' to False..

Different Server objects can be grouped in a Server pool object. A Server pool object can be specified in the Connection object to obtain an high availability (HA) connection. This is useful for long standing connections (for example an LDAP authenticator module in an application server) or when you have a multi replica LDAP server infrastructure. If you set the 'active' attribute to True while defining the ServerPool the strategy will check for server availability. With active ServerPool you can set an additional attribute 'exhaust' to raise an exception if no server is active in the pool. If 'exhaust' is set to False the pool may cycle forever and you must have an alternate way to check exhaustion of the pool.

The pool can have different HA strategies: 

* POOLING_STRATEGY_FIRST: gets the first server in the pool, if 'active' is set to True gets the first available server

* POOLING_STRATEGY_ROUND_ROBIN: each time the connection is open the subsequent server in the pool is used. If active is set to True unavailable servers will be discarded

* POOLING_STRATEGY_RANDOM: each time the connection is open a random server is chosen in the pool. If active is set to True unavailable servers will be discarded

A server pool can be defined in different ways::

    server1 = Server('server1')
    server2 = Server('server2')
    server3 = Server('server1', port=636, use_ssl=True)

* explicitly with Server objects in the init::

    server_pool = ServerPool([server1, server2, server3], POOLING_STRATEGY_ROUND_ROBIN, active=True, exhaust=True)

* explicitly with an add operation in the pool object::

    server_pool = ServerPool(None, POOLING_STRATEGY_ROUND_ROBIN_ACTIVE)
    server_pool.add(server1)
    server_pool.add(server2)
    server_pool.add(server3)

* implicitly directly in the Connection object init (passing a list of servers)::

    conn = Connection([server1, server2, server3])  # the ServerPool object is defined with the default pooling strategy

Pools can be dynamically changed. You can add and remove Server objects from pools even if they are already used in Connection::

    server4 = Server('server2', port=636, use_ssl=True)
    server_pool.remove(server2)
    server_pool.add(server4)

Connections are notified of the change and can reopen the socket to the new server at next open() operation.
