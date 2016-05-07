#######
Mocking
#######

You can easily mock ldap3 in your project using the MockSyncStrategy or the MockAsyncStrategy. Both of these strategies are based
on the MockBaseStreategy that emulates a simple LDAP server and can be used to test the LDAP functionalities in your project. If you need
you can even speficy a specific kind of LDAP server to emulate and MockBaseStrategy will provide a suitable schema and the relevant DSA info.

To populate the DIT (the Directory Information Tree, the hierarchical database that contains the LDAP data) you can provide data from an
actual LDAP server via a JSON import file or you can create at runtime only the entries needed for your test suite.

Anyway you must provide users and passwords needed by the test.

To mock the ldap3 library in your project you must define a fake Server object and set the client_strategy attribute to MOCK_SYNC or MOCK_ASYNC
while defining the Connection object::

    from ldap3 import Server, Connection
    server = Server('my_fake_server')
    connection = Connection(server, user='cn=my_user,ou=test,o=lab', password='my_fake_password', client_strategy=MOCK_SYNC)

then you can load the json entries file to add data to the DIT::

    connection.strategy.entries_from_json('my_entries.json')

or add entries dynamically at runtime::

    connection.strategy.add_entry('cn=user0,o=lab', {'userPassword': 'test0000', 'sn': 'user0_sn', 'revision': 0})
    connection.strategy.add_entry('cn=user1,o=lab', {'userPassword': 'test1111', 'sn': 'user1_sn', 'revision': 0})
    connection.strategy.add_entry('cn=user2,o=lab', {'userPassword': 'test2222', 'sn': 'user2_sn', 'revision': 0})

.. note::
    MockBaseStrategy doesn't check against the schema the validity of the added entries, so you can just add the entries needed to perform your tests.

Then you can use the mock connection as a normal connection to a real ldap server.

.. note::
    The MockBaseStrategy provides only Simple Authentication bind. You can bind to any object in the dict that has a **userPassword** attribute (either single or multi-valuee).
    The password must be stored as cleartext.

MockBaseStrategy supports the Bind, Unbind, Add, Modify, ModifyDn, Compare, Delete and Search operations (except the
extensible match). Abandon and Extended are not supported.

You can replicate the DIT of a real server (or just the portions of the Tree that you need in your tests) using the response_to_json() method
of the Connection object with *raw* output. Just perform a SUBTREE search with ALL_ATTRIBUTES with the needed base and a filter similar
to ``(objectclass=*)`` that captures every object in the DIT::

    from ldap3 import Server, Connection, ALL_ATTRIBUTES
    server = Server('my_real_server')
    connection = Connection(server, 'cn=my_user,ou=test,o=lab', 'my_real_password', auto_bind=True)
    if connection.search('ou=test,o=lab', '(objectclass=*)', attributes=ALL_ATTRIBUTES):
        connection.response_to_json('my_entries.json', raw=True, checked_attributes=False)

The *my_entries.json* can then be used in the ``entries_from_json()`` method of the MockBaseStrategy


