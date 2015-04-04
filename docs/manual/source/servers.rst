#######
Servers
#######

Server object
-------------
The Server object specify the DSA (Directory Server Agent) LDAP server that will be used by the connection. To create a new Server object the following parameters are available:

* host: name or ip or the complete url in the scheme://hostname:hostport format of the server (required) - port and scheme defined here have precedence over the parameters port and use_tls

* port: the port where the DSA server is listening (defaults to 389, for a cleartext connection)

* use_ssl: specifies if the connection is on a secure port (defaults to False). When True the secure port is usually set to 636

* allowed_referral_hosts: specifies which servers are considered reliable as referrals (defaults to None)

    * Format is a list of tuples; [(server, allow_auth), (server, allow_auth), ...]

    * server is an IP address or DNS name. Specify an asterisk (*) to accept any server.

    * allow_auth is a boolean to indicate if authentication to that server is allowed; if False only anonymous bind will be used.

* get_info: specifies if the server schema and info must be read (defaults to GET_NO_INFO). Possible values are:

    * NONE: no information is gathered from the server

    * DSA: server information is stored in server.info

    * SCHEMA: schema information is stored in server.schema

    * ALL: server and schema information are gathered and stored in server.info and server.schema

    * OFFLINE_EDIR_8_8_8: pre-built schema and info for NetIQ eDirectory 8.8.8

    * OFFLINE_AD_2012_R2: pre-built schema and info for Microsoft Active Directory from Windows Server 2012 R2

    * OFFLINE_SLAPD_2_4: pre-built schema and info for Openldap 2.4

    * OFFLINE_DS389_1_3_3: pre-built schema and info for DS389 1.3.3

* mode: specifies dual IP stack behaviour for resolving LDAP server names in dns: Possible values are:

    * IP_SYSTEM_DEFAULT: disable dual stack feature. Use system default

    * IP_V4_ONLY: use only IPV4 names

    * IP_V6_ONLY: use only IPV6 names

    * IP_V4_PREFERRED: tries IPV4 names and if connection fails tries IPV6

    * IP_V6_PREFERRED: tries IPV6 names and if connection fails tries IPV4

* tls: Tls object that contains information about the certificates and the trusted roots needed to establish a secure connection (defaults to None). If None any server certificate will be accepted.

* formatter: a dictionary of custom formatter for attributes returned in search

* connect_timeout: timeout in seconds for the connect operation

Example::

    server = Server('server1', port = 636, use_ssl = True, allowed_referral_hosts = [('server2', True), ('server3', False)])

Server Pool
-----------

.. sidebar:: Active strategies

   *ACTIVE* strategies can check if the server is listening on the specified port. When the 'active' attribute is set to True the strategy tries to open and close a socket on the port. If your LDAP server has problems with the opening and closing of sockets you can set 'active' to False..

Different Server objects can be grouped in a Server pool object. A Server pool object can be specified in the Connection object to obtain an high availability (HA) connection. This is useful for long standing connections (for example an LDAP authenticator module in an application server) or when you have a multi replica LDAP server infrastructure. If you set the 'active' attribute to True while defining the ServerPool the strategy will check for server availability. With active ServerPool you can set an additional attribute 'exhaust' to raise an exception if no server is active in the pool. If 'exhaust' is set to False the pool may cycle forever and you must have an alternate way to check exhaustion of the pool.

The pool can have different HA strategies:

* POOLING_STRATEGY_FIRST: gets the first server in the pool, if 'active' is set to True gets the first available server

* FIRST: alias for POOLING_STRATEGY_FIRST

* POOLING_STRATEGY_ROUND_ROBIN: each time the connection is open the subsequent server in the pool is used. If active is set to True unavailable servers will be discarded

* ROUND_ROBIN: alias for POOLING_STRATEGY_ROUND_ROBIN

* POOLING_STRATEGY_RANDOM: each time the connection is open a random server is chosen in the pool. If active is set to True unavailable servers will be discarded

* RANDOM: alias for POOLING_STRATEGY_RANDOM

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


Custom formatters can be used to specify how an attribute value must be returned in the 'attributes' attribute of the search entry object.
A formatter must be a callable that receives a bytes value and return an object. The object will be returned in the 'attributes' if the schema is read and check_names connection parameter is True.
If the attribute is defined in the schema as 'multi_value' the attribute value is returned as a list (even if only a single value is present) else it's returned as a single value.

Offline Schema
--------------

If your LDAP server doesn't return the DSA info or the Schema you can load pre-built schemas and infos with the get_info parameter. Are available schemas for eDirectory, Active Directory and Openldap.

You can also save the schema and info in a json string::

    json_info = server.info.to_json()
    json_schema = server.schema.to_json('')

or can have them saved on file::

    server.info.to_file('server-info.json)
    server.schema.to_file('server-schema.json')

to build a new server object with the saved json files you can retrieve them with::

    from ldap3 import DsaInfo, SchemaInfo
    dsa_info = DsaInfo.from_file('server-info.json')
    schema_info = SchemaInfo.from_file('server-schema.json')
    server = Server('hostname', dsa_info, schema_info)

and then you can use the server as usual. Hostname must resolve to a real server.
