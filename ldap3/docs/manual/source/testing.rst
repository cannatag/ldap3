#######
Testing
#######

Inside the "test" package you can find examples for each LDAP operation. You can customize the test modifying the variables in the __init__.py in the test package.
You can set the following parameters::

    test_server = 'server'  # the LDAP server where tests are executed
    test_user = 'user'  # the user that performs the tests
    test_password = 'password'  # user's password
    test_base = 'o=test'  # base context where test objects are created
    test_moved = 'ou=moved,o=test'  # base context where objects are moved in ModifyDN operations
    test_name_attr = 'cn'  # naming attribute for test objects
    test_port = 389  # ldap port
    test_port_ssl = 636  # ldap secure port
    test_authentication = AUTH_SIMPLE  # authentication type
    test_strategy = STRATEGY_SYNC  # strategy for executing tests
    #test_strategy = STRATEGY_ASYNC_THREADED  # uncomment this line to test the async strategy
    # test_strategy = STRATEGY_SYNC_RESTARTABLE  # uncomment this line to test the sync_restartable strategy

To execute the test suite you need an LDAP server with the test_base and test_moved containers and a test_user with privileges to add, modify and remove objects
in that context.

To execute the test_tls unit test you must supply your own certificates or tests will fail.

The test package is available in the git repository.
