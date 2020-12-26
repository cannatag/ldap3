Extended Microsoft operations
#############################


Microsoft extended operations are intended for Active Directory::

    extend.microsoft
        extend.microsoft.dir_sync(
            sync_base,
            sync_filter,
            attributes,
            cookie,
            object_security,
            ancestors_first,
            public_data_only,
            incremental_values,
            max_length,
            hex_guid
        )
        extend.microsoft.modify_password(
            user,
            new_password,
            old_password=None
        )
        extend.microsoft.persistent_search(
            search_base,
            search_scope,
            attributes,
            streaming,
            callback
        )


Microsoft persistent search is similar to the :doc:`standard persistent search</standard>` but not the same. It does not tell about object
creation or deletion, it simply notifies when an object has been modified and sends all the attributes that were requested. This means it
doesn't tell what changed. The control used is **LDAP_SERVER_NOTIFICATION_OID** (1.2.840.113556.1.4.528).

This search needs the *AsyncStream* strategy to work properly. This strategy sends each received packet to an external thread where it can
be processed as soon as it is received.
As the standard persistent_search, it never sends the *SearchDone* packet, the :doc:`abandon operation</abandon>` may be used to tell AD
to cancel the persistent search. 

The persistent_search() method has limited parameters compared a :doc:`standard search</searches>`. However, it accepts some additional parameters specific
to the persistent search::

    def persistent_search(self,
                          search_base='',
                          search_scope=SUBTREE,
                          attributes=ALL_ATTRIBUTES,
                          streaming=True,
                          callback=None
                          ):

If you don't pass any parameters the search should be globally applied in your LDAP server and all object attributes are returned.

The only permitted search filter is ``(objectclass = *)`` so it has been fixed within the function.

To enable Persistent Searches to get any object modification as they happen (for logging purpose)::

    from ldap3 import Server, Connection, ASYNC_STREAM

    s = Server('myserver')
    c = Connection(s, 'cn=admin,o=resources', 'password', client_strategy=ASYNC_STREAM)

    c.stream = open('myfile.log', 'w+')
    p = c.extend.microsoft.persistent_search(base, scope, ['objectClass', 'sn'])

now the persistent search is running in an internal thread. Each modification is recorded in the log in LDIF-CHANGE format, with the event type,
event time and the modified dn and changelog number (if available) as comments.

For example an output from my test suite is the following::

    # 2020-12-23T15:41:40.578021
    dn: cn=dn-1,ou=test,dc=domain,dc=local
    objectClass: User
    objectClass: organizationalPerson
    objectClass: Person
    objectClass: Top
    sn: dn-1

    # 2020-12-23T15:41:40.579555
    dn: cn=dn-1,ou=test,dc=domain,dc=local
    objectClass: User
    objectClass: organizationalPerson
    objectClass: Person
    objectClass: Top
    sn: dn-1

    # 2020-12-23T15:41:45.349306
    dn: cn=dn-2,ou=test,dc=domain,dc=local
    objectClass: User
    objectClass: organizationalPerson
    objectClass: Person
    objectClass: Top
    sn: dn-2

There's no sign of what happened to the object. All we know is that there was a modification.

If you want to temporary stop the persistent search you can use ``p.stop()``. Use ``p.start()`` to start it again.


If you call the ``persistent_search()`` method with ``streaming=False`` you can get the modified entries with the ``p.next()`` method.
Each call to ``p.next(block=False, timeout=None)`` returns one event, with the extended control already decoded (as dict values) if
available::

    from ldap3 import Server, Connection, ASYNC_STREAM

    s = Server('myserver')
    c = Connection(s, 'cn=admin,o=resources', 'password', client_strategy=ASYNC_STREAM, auto_bind=True)

    p = c.extend.microsoft.persistent_search(streaming=False)
    p.start()
    while True:
        print(p.next(block=True))

When using ``next(block=False)`` or ``next(block=True, timeout=10)`` the method returns `None` if nothing is received from the server.

Alternatively you may use the ``funnel`` method to iterate over the received changes. It is a generator::

    for result_entry in p.funnel(block=True):
        print(result_entry['dn'])

If you call the ``persistent_search()`` method with ``callback=myfunction`` (where `myfunction` is a callable, including lambda, accepting
a dict as parameter) your function will be called for each event received in the persistent search.
The function will be called in the same thread of the persistent search, so it should not block::

    from ldap3 import Server, Connection, ASYNC_STREAM, ALL_ATTRIBUTES

    def change_detected(result_entry):
        print(result_entry['dn'])
        print(result_entry['attributes'])
    
    s = Server('myserver')
    c = Connection(s, 'cn=admin,o=resources', 'password', client_strategy=ASYNC_STREAM, auto_bind=True)
    p = c.extend.microsoft.persistent_search(base, scope, ALL_ATTRIBUTES, callback=change_detected)


