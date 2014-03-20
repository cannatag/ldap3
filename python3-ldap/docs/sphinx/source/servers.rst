#######
Servers
#######

Server object
-------------
The Server object specify the DSA (Directory Server Agent) LDAP server that will be used by the connection. To create a new Server object the following parameters are available:

* host: name or ip of the server (required)

* port: the port where the DSA server is listening (defaults to 386, for a cleartext connection)

* use_ssl: specifies if the connection is on a secure port (defaults to False). When True the secure port is usually set to 636

* allowed_referral_hosts: specifies which servers are considered reliable as referrals (defaults to None), Specify a list of referral servers or an asterisk to accept all servers

* get_info: specifies if the server schema and info must be read (defaults to GET_NO_INFO). Possible values are:

    * GET_NO_INFO: no information is gathered from the server

    * GET_DSA_INFO: server information is stored in server.info

    * GET_SCHEMA_INFO: schema information is stored in server.schema

    * GET_ALL_INFO: server and schema information are gathered and stored in server.info and server.schema

* tls: Tls object that contains information about the certificates and the trusted roots needed to establish a secure connection (defaults to None). If None any server certificate will be accepted.

Example::

    server = Server('server1', port = 636, use_ssl = True, allowed_referral_hosts = ['server2', 'server3'])

Server Pool
-----------

.. sidebar:: Active strategies

   *ACTIVE* strategies check if the server is listening on the specified port. The strategy tries to open and close a socket on the port. If your LDAP server has problems with the opening and closing of sockets you can use a PASSIVE strategy.

Different Server objects can be grouped in a Server pool object. A Server pool object can be specified in the Connection object to obtain an high availability (HA) connection. This is useful for long standing connections (for example an LDAP authenticator module in an application server) or when you have a multi replica LDAP server infrastructure. The pool can have different HA strategies:

* POOLING_STRATEGY_NONE: no pooling strategy used, the connection use always the first server in the pool

* POOLING_STRATEGY_FIRST_ACTIVE: get the first available and active server in the pool, if no server is active an exception is raised

* POOLING_STRATEGY_ROUND_ROBIN_PASSIVE: each time the connection is open the subsequent server in the pool is used

* POOLING_STRATEGY_ROUND_ROBIN_ACTIVE: each time the connection is open the subsequent active server in the pool is used, if no server is active an exception is raised

* POOLING_STRATEGY_RANDOM_PASSIVE: each time the connection is open a random server is chosen in the pool

* POOLING_STRATEGY_RANDOM_ACTIVE: each time the connection is open an active random server is chosen in the pool, if no server is active an exception is raised

A server pool can be defined in different ways::

    server1 = Server('server1')
    server2 = Server('server2')
    server3 = Server('server1', port=636, use_ssl=True)

* explicitly with Server objects in the init::

    server_pool = ServerPool([server1, server2, server3], POOLING_STRATEGY_ROUND_ROBIN_ACTIVE)

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
