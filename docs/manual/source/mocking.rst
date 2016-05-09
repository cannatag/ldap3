#######
Mocking
#######

You can mock ldap3 in your project using the MockSyncStrategy or the MockAsyncStrategy. Both of these strategies are based
on the MockBaseStreategy that emulates a simple LDAP server and can be used to test the LDAP functionalities in your project.
You can even define a specific kind of LDAP server to emulate and MockBaseStrategy will provide a suitable schema and the relevant DSA info.

To populate the DIT (the Directory Information Tree, the hierarchical database that contains the LDAP data) you can provide data from an
actual LDAP server via a JSON data file or you can create at runtime only the entries and the attributes needed for your test suite.

Anyway if you want to use Simple Bind authentication you must provide users and passwords needed by the test. No ACL or rights control is done
by the MockBaseStrategy.

To mock the ldap3 library in your project you must define a fake Server object and set the client_strategy attribute to MOCK_SYNC or MOCK_ASYNC
while defining the Connection object::

    from ldap3 import Server, Connection
    server = Server('my_fake_server')
    connection = Connection(server, user='cn=my_user,ou=test,o=lab', password='my_password', client_strategy=MOCK_SYNC)

then you can load the json entries file to add data to the DIT::

    connection.strategy.entries_from_json('my_entries.json')

or add entries dynamically at runtime::

    connection.strategy.add_entry('cn=user0,ou=test,o=lab', {'userPassword': 'test0000', 'sn': 'user0_sn', 'revision': 0})
    connection.strategy.add_entry('cn=user1,ou=test,o=lab', {'userPassword': 'test1111', 'sn': 'user1_sn', 'revision': 0})
    connection.strategy.add_entry('cn=user2,ou=test,o=lab', {'userPassword': 'test2222', 'sn': 'user2_sn', 'revision': 0})

.. note::
    MockBaseStrategy doesn't check the validity of the added entries against the schema, so you can just add the entries and the attribute
    values needed to perform your tests.

Then you can use the mock connection as a normal connection to an LDAP server.

.. note::
    The MockBaseStrategy provides only Simple Authentication bind. You can bind to any object in the dict that has a **userPassword** attribute
    (either single or multi-valued). The password must be stored as cleartext. You cannot use the ``auto_bind`` parameter because the DIT is
    populated after the creation of the Connection object.

MockBaseStrategy supports the Bind, Unbind, Add, Modify, ModifyDn, Compare, Delete and Search operations (except for the
extensible match). Abandon and Extended are not supported.

.. note::
    You can replicate the DIT of a real server (or just the portions of the Tree that you need in your tests) using the response_to_json() method
    of the Connection object with *raw* output. Just perform a SUBTREE search with ALL_ATTRIBUTES (or the attributes needed in your tests) with
    the needed base and a filter as ``(objectclass=*)`` that captures every object in the DIT::

        from ldap3 import Server, Connection, ALL_ATTRIBUTES
        server = Server('my_real_server')
        connection = Connection(server, 'cn=my_real_user,ou=test,o=lab', 'my_real_password', auto_bind=True)
        if connection.search('ou=test,o=lab', '(objectclass=*)', attributes=ALL_ATTRIBUTES):
            connection.response_to_json('my_entries.json', raw=True, checked_attributes=False)

    The *my_entries.json* file can then be used in the ``entries_from_json()`` method of the MockBaseStrategy.

While defining the mock server you can specify a predefined schema with the ``get_info`` parameter::

    from ldap3 import Server, Connection. OFFLINE_SLAPD_2_4
    server = Server('my_fake_server', get_info=OFFLINE_SLAPD_2_4)

The available offline schemas are OFFLINE_SLAPD_2_4 (OpenLDAP), OFFLINE_EDIR_8_8_8 (eDirectory), OFFLINE_AD_2012_R2 (Active Directory) and
OFFLINE_DS389_1_3_3 (389 Directory Server).

You can also speficy a previously saved schema and info retrieved from a real server::

    from ldap3 import Server, Connection, ALL

    # Retrieve server info and schema from a real server
    server = Server('my_real_server', get_info=ALL)
    connection = Connection(server, 'cn=my_user,ou=test,o=lab', 'my_real_password', auto_bind=True)

    # Store server info and schema to json files
    server.info.to_file('my_real_server_info.json')
    server.schema.to_file('my_real_server_schema.json')


A complete example
^^^^^^^^^^^^^^^^^^

The following code retrieves the schema and the server info from a real server, then read the entries from a portion of the DIT and store them
in a json file. Then a fake server is created and loaded with the previoulsy saved schema, server info and entries and a fake user is defined
for simple binding::

    from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES
    REAL_SERVER = 'my_real_server'
    REAL_USER = 'cn=my_real_user,ou=test,o=lab'
    REAL_PASSWORD = 'my_real_password'

    # Retrieve server info and schema from a real server
    server = Server(REAL_SERVER, get_info=ALL)
    connection = Connection(server, REAL_USER, REAL_PASSWORD, auto_bind=True)

    # Store server info and schema to json files
    server.info.to_file('my_real_server_info.json')
    server.schema.to_file('my_real_server_schema.json')

    # Read entries from a portion of the DIT from real server and store them in a json file
    if connection.search('ou=test,o=lab', '(objectclass=*)', attributes=ALL_ATTRIBUTES):
        connection.response_to_json('my_real_server_entries.json', raw=True, checked_attributes=False)

    # Close the connection to the real server
    connection.unbind()

    # Create a fake server from the info and schema json files
    fake_server = Server.from_definition('my_fake_server', 'my_real_server_info.json', 'my_real_server_schema.json'

    # Create a MockSyncStrategy connection to the fake server
    fake_connection = Connection(fake_server, user='cn=my_user,ou=test,o=lab', password='my_password', client_strategy=MOCK_SYNC)

    # Populate the DIT of the fake server
    fake_connetion.strategy.entries_from_json('my_real_server_entries.json')

    # Add a fake user for Simple binding
    connection.strategy.add_entry('cn=my_user,ou=test,o=lab', {'userPassword': 'my_password', 'sn': 'user_sn', 'revision': 0})

    # Bind to the fake server
    connection.bind()

Then the connection is ready to be used in your tests.
