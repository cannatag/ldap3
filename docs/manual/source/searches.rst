The SEARCH operation
####################

The **Search** operation is used to request a server to return, subject to access controls and other restrictions,
a set of entries matching a search filter. This can be used to read attributes from a single entry, from entries
immediately subordinate to a particular entry, or from a whole subtree of entries.

In the ldap3 library the signature for the Search operation is::

    def search(self,
               search_base,
               search_filter,
               search_scope=SUBTREE,
               dereference_aliases=DEREF_ALWAYS,
               attributes=None,
               size_limit=0,
               time_limit=0,
               types_only=False,
               get_operational_attributes=False,
               controls=None,
               paged_size=None,
               paged_criticality=False,
               paged_cookie=None):


* search_base: the base of the search request.

* search_filter: the filter of the search request. It must conform to the LDAP filter syntax specified in RFC4515.

* search_scope: specifies how broad the search context is:

    * BASE: retrieves attributes of the entry specified in the search_base.

    * LEVEL: retrieves attributes of the entries contained in the search_base. The base must reference a container object.

    * SUBTREE: retrieves attributes of the entries specified in the search_base and all subordinate containers downward.

* dereference_aliases: specifies how the server must treat references to other entries:

    * DEREF_NEVER: never dereferences entries, returns alias objects instead. The alias contains the reference to the real entry.

    * DEREF_SEARCH: while searching subordinates of the base object, dereferences any alias within the search scope.
      Dereferenced objects become the bases of further search scopes where the Search operation is also applied by the server.
      The server should eliminate duplicate entries that arise due to alias dereferencing while searching.

    * DEREF_BASE: dereferences aliases in locating the base object of the search, but not when searching subordinates
      of the base object.

    * DEREF_ALWAYS: always returns the referenced entries, not the alias object.

* attributes: a single attribute or a list of attributes to be returned by the search (defaults to None).
  If attributes is None no attribute is returned. If attributes is ALL_ATTRIBUTES or ALL_OPERATIONAL_ATTRIBUTES all user attributes
  or all operational attributes are returned.

* size_limit: maximum number of entries returned by the search (defaults to None).
  If None the whole set of found entries is returned, unless the server has a more restrictive rule.

* time_limit: number of seconds allowed for the search (defaults to None).
  If None the search can take an unlimited amount of time, unless the server has a more restrictive rule.

* types_only: doesn't return any attribute value, only the attribute names are returned.

* get_operational_attributes: if True returns informational attributes (managed automatically by the server) for each entry.

* controls: additional controls to send in the request.

* paged_size: if paged_size is greater than 0 a simple paged search is executed as described in RFC2696 (defaults to None).
  The search will return at most the specified number of entries.

* paged_criticality: if True the search will be executed only if the server is capable of performing a simple paged search.
  If False and the server is not capable of performing a simple paged search a standard search will be executed.

* paged_cookie: an *opaque* string received in a paged paged search that must be sent back while requesting
  subsequent entries of the search result.

.. warning::
    Make sure to call escape_filter_chars() from ldap3.utils.conv on any user input before placing it into a .search() call. This is to avoid possible injection of malicious code. Look at https://www.linkedin.com/pulse/ldap-injection-django-jerin-jose for more information.


The LDAP filter
---------------

The LDAP filter defines the conditions that must be fulfilled in order for the Search to match a given entry and must follow
the syntax defined in RFC 4515. The filter is composed of assertions that can be joined with AND (&) or OR (|) operators,
or negated with the NOT (!) operator. The AND, OR, and NOT choices can be used to form combinations of assertions in a
complex filter. At least one filter element must be present in an AND or in a OR.

An assertion is formed by 3 parts: the attribute name, a matching operator, and the matched value. The assertion itself
is surrounded by parentheses, as in "(sn=Smith)". The LDAP schema defines how each attribute matching rule and ordering
rule is evaluated.

An assertion is evaluated by the server to TRUE, FALSE, or Undefined. An assertion evaluates to Undefined when the server
is not able to determine whether the assertion value matches an entry (for example when the matching rule is not defined
for an attribute, when the type of filter is not implemented by the server or when the assertion value is invalid). If
the filter evaluates to TRUE for a particular entry the attributes requested in the Search operation are returned for
that entry as part of the Search result (subject to any applicable access control restrictions). If the filter evaluates
to FALSE or Undefined, then the entry is ignored for the Search operation.

An AND is TRUE if all the assertion in the set evaluate to TRUE, FALSE if at least one assertion is FALSE and Undefined
otherwise.

An OR is TRUE if at least one assertion evaluates to TRUE, FALSE if all the assertions in the set evaluate to FALSE and
Undefined otherwise.

A NOT is TRUE if the assertion being negated is FALSE, FALSE if it is TRUE, and Undefined if it is Undefined.

If the search filter contains the following characters you must use the relevant escape ASCII sequence, as per RFC4515
(section 3): '*' -> '\\\\2A', '(' -> '\\\\28', ')' -> '\\\\29', '\\' -> '\\\\5C', chr(0) -> '\\\\00'.

There are 7 match operators that can be used in a filter:

* EQUALITY (attribute=value): The matching rule for an equality filter is defined in the schema by the EQUALITY matching
  rule for the attribute type. The filter is TRUE when the EQUALITY rule returns TRUE as applied to the attribute and the
  asserted value.

* SUBSTRING (attribute=initial*middle*final): there can be at most one initial substring and at most one final substring
  of the assertion value, while there can be many middle substrings separated by an asterisk. The matching rule in a
  substrings filter is defined by the SUBSTR matching rule for the attribute type. The filter is TRUE when the SUBSTR rule
  returns TRUE as applied to the attribute and the asserted value.

* GREATER OR EQUAL (attribute>=value): The matching rule is defined by the ORDERING matching rule for the attribute type.
  The filter is TRUE when the ORDERING rule returns FALSE as applied to the attribute and the asserted value.

* LESS OR EQUAL (attribute<=value): The matching rules are defined by the ORDERING and EQUALITY matching rules for the
  attribute type. The filter is TRUE when either the ORDERING or EQUALITY rule returns TRUE as applied to the attribute
  and the asserted value.

* PRESENT (attribute=*): the filter is TRUE when there is an attribute present in an entry, FALSE when no attribute
  is present in an entry, and Undefined otherwise.

* APPROXIMATE (attribute~=value): the filter is TRUE when there is a value of the attribute type for which some
  server locally-defined approximate matching algorithm (e.g., spelling variations, phonetic match, etc.) returns TRUE.
  If a value matches for equality, it also satisfies an approximate match. If approximate matching is not supported for the
  attribute, this filter should be treated as an equality filter by the server. The approximate algorithm, if available,
  is local to the server so you should check your server documentation to see if this matching operator can be used.

* EXTENSIBLE (attribute:=value): in the extensible filter the attribute part of the filter is augmented with other
  information (separated by a colon ":" as in "(o:dn:=Ace Industry)") to achieve particular search behaviours. Please
  check the documentation of your LDAP server to see what EXTENSIBLE syntax is available.

NOT, AND and OR
---------------

You can negate the result of an assertion with the NOT (!) operator as in::

    (!(sn=Smith))  # retrieves all entries where the sn is not Smith

You can join more than one assertion with the AND (&) and the OR (|) operator to create a complex filter. The AND and
OR operator have their own parentheses that include all the assertion in the set::

    (&(givenName=A*)(sn=Smith))  # retrieves all entries where sn attribute is Smith and givenName starts with A.
    (|(sn=Smith)(sn=Johnson))  # retrieves all entries where sn is Smith or Johnson.

You can even mix the NOT, AND and OR to form a more complex filter as in::

    (|(&(objectClass=inetOrgPerson)(!(cn=Smith))(cn=admin*))  # retrieves all entries whose cn starts with admin and all entries
    of class inetOrgPerson with a surname different from Smith.

Search scope and aliases
------------------------

The scope of the search specifies how broad the search context will be. The LDAP database is a hierarchical structure
(similar to a traditional file system) with a root and with container and leaf objects. a container can be stored in other
containers, but not in a leaf object. It must be clear that containers and leafs structure has nothing to do with the group
and group membership objects. A group (groupOfNames) object is a leaf object with a member attribute that contains references
to other objects.

The only way to know if an object is a container or a leaf object is to query the LDAP server schema for that object's class.

There are three possible scopes:

* BASE: the scope is constrained to the entry named by search_base.

* LEVEL: the scope is constrained to the immediate subordinates of the entry named by search_base.

* SUBTREE: the scope is constrained to the entry named by search_base and to all its subordinates.

An object can be an alias of another one defined somewhere in the LDAP data structure (it is similar to a link inside the
LDAP database). While searching you can specify if "dereferencing" must be applied to the found aliases. The act of dereferencing
an alias includes recursively dereferencing of aliases. The LDAP server should detect looping while dereferencing aliases
in order to prevent denial-of-service attacks of this nature.

There are four possible ways of managing aliases while searching:

* DEREF_NEVER: never dereferences entries, returns alias objects instead. The alias contains the reference to the real entry.

* DEREF_SEARCH: while searching subordinates of the base object, dereferences any alias within the search scope.
  Dereferenced objects become the bases of further search scopes where the Search operation is also applied by the server.
  If the search scope is SUBTREE, the Search continues in the subtree of any dereferenced object. If the search scope is
  LEVEL, the search is applied to any dereferenced objects and is not applied to their subordinates.
  Servers should eliminate duplicate entries that arise due to alias dereferencing while searching.

* DEREF_BASE: dereferences aliases in locating the base object of the search, but not when searching subordinates
  of the base object.

* DEREF_ALWAYS: Dereference aliases both in searching and in locating the base object of the Search.

Attributes
----------

There are two kinds of attributes defined in the LDAP schema: User attributes and Operational Attributes. User attribute
are added, modified and deleted with the usual LDAP operations, while Operational attributes are managed by the server and
can only be read.

The server can apply some ACL to attributes and entries to prevent users from accessing data they don't have right to read
or modify.

You can request a list of attributes to be returned for each found entry. You must specify the attribute names or the
following values for attribute grouping:

* (ASTERISK): all user attributes, defined in ldap3.ALL_ATTRIBUTES

+ (PLUS): all operational attributes, defined in ldap3.ALL_OPERATIONAL_ATTRIBUTES

1.1: no attributes, defined in ldap3.NO_ATTRIBUTES

Even if the RFC states that if you don't specify any attribute the server should return all available attributes for each
entry found in the search the ldap3 library requires that you to specify at least one attribute in the attributes list,
else it will perform a "1.1" Search request that returns only the dn of the entries found. To get all the user attributes
you can use::

    attributes=ldap3.ALL_ATTRIBUTES

while to get all the user and all the operational attributes you can use::

    attributes=[ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES]


Keep in mind that the server may not return some operational attribute if they are not explicitly requested
(because they may take a long time or many resources to be computed), so if you need a specific attribute is better to
request it explicitly. Also, some servers dont' return operational attributes information when reading the schema.

To request the operational attributes you can even set the get_operational_attributes parameter to True.

The standard LDAP RFCs define that if an attribute doesn't have a value it must not be returned at all. This can cause your code
to become clumsy because you have to check always for existence of an attribute in the *attribute* dictionary of the response.
To let the library return an empty attribute even if it is not present in the LDAP object retrieved by the search you can set the
*return_empty_attributes* parameter to True in the Connection object, in this case all the requested attributes not present in the objects
found by the search are set to an empty list.

Checked Attributes
------------------

The checked attributes feature checks the LDAP syntax of the attributes defined in schema and returns a properly formatted
entry result while performing searches. This means that if, for example, you have an attributes specified as GUID in the
server schema you will get the properly formatted GUID value ('012381d3-3b1c-904f-b29a-012381d33b1c') in the
connection.response[0]['attributes'] key dictionary instead of a sequence of bytes. Or if you request an attribute defined
as an Interger in the schema you will get the value already converted to int. Furthermore for attributes defined as single
valued in schema you will get the value instead of a list of values (that would always be one sized).
To activate this feature you must set the get info to GET_SCHEMA_INFO or GET_ALL_INFO value when defining the server object
and the 'check_names' attributes to True in the Connection object (True by default).

There are a few of standard formatters defined in the library, most of them are defined in the relevants RFCs:

* format_unicode  # returns an unicode object in Python 2 and a string in Python 3

* format_integer  # returns an integer

* format_binary  # returns a bytes() sequence

* format_uuid  # returns a GUID (UUID) as specified in RFC 4122 - byte order is big endian

* format_uuid_le  # same as above but byte order is little endian

* format_boolean  # returns a boolean

* format_time  # returns a datetime object (with properly defined timezone, or UTC if timezone is not specified) as
  defined in RFC 4517

You can even define your custom formatter for specific purposes. Just pass a dictionary in the format
{'identifier': callable} in the 'formatter' parameter of the Server object. The callable must be able to receive a single byte
value and convert it the relevant object or class instance.

The resolution order of the format feature is the following:

Custom formatters have precedence over standard formatter. In each category (from highest to lowest priority):

1. attribute name

2. attribute oid(from schema)

3. attribute names (from oid_info)

4. attribute syntax (from schema)

If a suitable formatter is not found the value will be rendered as bytes.

Search constraints
------------------

You can limit the number of entries returned in a search or the time spent by the server performing the search using the
size_limit and time_limit parameters. The server can also have some system wide constrains regarding the maximun number of
entries returned in any search and the time spent in performing the search. It can also have some constrains on how the
aliases are dereferenced. You must check the configuration of your LDAP server to verify which limitations are currenty
active.

You can also request to not get any attribute value in the entries returned by the search with the types_only=True
parameter.


.. note::
   Microsoft Active Directory set an hard limit of 1000 entries returned by any search. So it's better to always set up a paged search
   when dealing with AD.


Simple paged search
-------------------

The search operation can perform a *simple paged search* as per RFC2696. You must specify the required number of entries
returned in each response set. After the first search you must send back the cookie you get with each response in each
subsequent search. If you send 0 as paged_size and a valid cookie the search operation referred by that cookie is abandoned.
Cookie can be found in connection.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']; the server may return
an estimated total number of entries in connection.result['controls']['1.2.840.113556.1.4.319']['value']['size'].
You can change the paged_size in any subsequent search request.

Example::

    from ldap3 import Server, Connection, SUBTREE
    total_entries = 0
    server = Server('test-server')
    c = Connection(server, user='username', password='password')
    c.search(search_base = 'o=test',
             search_filter = '(objectClass=inetOrgPerson)',
             search_scope = SUBTREE,
             attributes = ['cn', 'givenName'],
             paged_size = 5)
    total_entries += len(c.response)
    for entry in c.response:
        print(entry['dn'], entry['attributes'])
    cookie = c.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
    while cookie:
        c.search(search_base = 'o=test',
                 search_filter = '(objectClass=inetOrgPerson)',
                 search_scope = SUBTREE,
                 attributes = ['cn', 'givenName'],
                 paged_size = 5,
                 paged_cookie = cookie)
        total_entries += len(c.response)
        cookie = c.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
        for entry in c.response:
            print(entry['dn'], entry['attributes'])
    print('Total entries retrieved:', total_entries)

Or you can use the much simpler extended operations package that wraps all this machinery and hides implementation
details, you can choose to get back a generator or the whole list of entries found.

Working with a generator is better when you deal with very long list of entries or have memory issues::

    # paged search wrapped in a generator
    total_entries = 0
    entry_generator = c.extend.standard.paged_search(search_base = 'o=test',
                                                     search_filter = '(objectClass=inetOrgPerson)',
                                                     search_scope = SUBTREE,
                                                     attributes = ['cn', 'givenName'],
                                                     paged_size = 5,
                                                     generator=True)
    for entry in entry_generator:
        total_entries += 1
        print(entry['dn'], entry['attributes'])
    print('Total entries retrieved:', total_entries)

Remember that a generator can be consumed only one time, so you must elaborate the results in a sequential way.


Working with a list keeps all the found entries in a list and you can elaborate them in a random way::

    # whole result list
    entry_list = c.extend.standard.paged_search(search_base = 'o=test',
                                                search_filter = '(objectClass=inetOrgPerson)',
                                                search_scope = SUBTREE,
                                                attributes = ['cn', 'givenName'],
                                                paged_size = 5,
                                                generator=False)
    for entry in entry_list:
        print entry['attributes']
    total_entries = len(entry_list)
    print('Total entries retrieved:', total_entries)

If the paged search operation returns an error, the paged_search() method raises an Exception of class LDAPOperationResult, subclassed to the actual error returned by the server.

Response
--------

Responses are received and stored in the connection.response as a list of dictionaries.
You can get the search result entries of a Search operation iterating over the response attribute.
Each entry is a dictionary with the following field:

* dn: the distinguished name of the entry

* attributes: a dictionary of returned attributes and their values. Values are list. Values are in UTF-8 format

* raw_attributes: same as 'attributes' but not encoded (bytearray)


Entries
-------

Entries found in search are returned also in connection.entries as abstract.entry objects. This can be helpful when you
use the ldap3 library from the interpreter prompt.

Each Entry object contains one object found in the search. You can access entry attributes either as a dictionary or as
properties using the attribute name: entry['CommonName'] is the same of entry.CommonName and of entry.commonName or entry.commonname.

Each Entry has an entry_dn property that returns the distinguished name of the LDAP entry.

Attributes are stored in an internal dictionary with case insensitive access. You can even access the raw attribute with
the entry_raw_attribute(attribute_name) to get an attribute raw value, or property entry_raw_attributes to get the whole
raw attributes dictionary.

Entry is a read only object, you cannot modify or add any property to it. It's an iterable object that returns an attribute
object at each iteration. Note that you get back the whole attribute object, not only the key as in a standard dictionary::

    >>> c.entries[0]
    DN: cn=person1,o=test
        cn: person1
        givenName: person1_givenname
        objectClass: inetOrgPerson
                     organizationalPerson
                     Person
                     ndsLoginProperties
                     Top
        sn: person1_surname
        GUID: fd9a0d90-15be-2841-fd82-fd9a0d9015be

and each attribute of the entry can be accessed as a dictionary or as a namespace::

    >>> c.entries[0].GUID
        GUID: fd9a0d90-15be-2841-fd82-fd9a0d9015be
    >>> c.entries[0].GUID.value
        'fd9a0d90-15be-2841-fd82-fd9a0d9015be'
    >>> c.entries[0].GUID.raw_values
        [b'\xfd\x9a\r\x90\x15\xbe(A\xfd\x82\xfd\x9a\r\x90\x15\xbe']
    >>> c.entries[0].GUID.values
        ['fd9a0d90-15be-2841-fd82-fd9a0d9015be']

An Entry can be converted to LDIF with the entry.entry_to_ldif() method and to JSON with the entry.entry_to_json() method.
Entries can be easily printed at the interactive prompt::


    >>> print(c.entries[0].entry_to_ldif())
    version: 1
    dn: cn=person1,o=test
    objectClass: inetOrgPerson
    objectClass: organizationalPerson
    objectClass: Person
    objectClass: ndsLoginProperties
    objectClass: Top
    ACL: 2#subtree#cn=person1,o=test#[All Attributes Rights]
    ACL: 6#entry#cn=person1,o=test#loginScript
    ACL: 2#entry#[Public]#messageServer
    ACL: 2#entry#[Root]#groupMembership
    ACL: 6#entry#cn=person1,o=test#printJobConfiguration
    ACL: 2#entry#[Root]#networkAddress
    sn: person1_surname
    cn: person1
    givenName: person1_givenname
    GUID:: +J4sRRpsAEmjlfieLEUabA==
    # total number of entries: 1

    >>> print(c.entries[0].entry_to_json())
    {
        "attributes": {
            "ACL": [
                "2#subtree#cn=person1,o=test#[All Attributes Rights]",
                "6#entry#cn=person1,o=test#loginScript",
                "2#entry#[Public]#messageServer",
                "2#entry#[Root]#groupMembership",
                "6#entry#cn=person1,o=test#printJobConfiguration",
                "2#entry#[Root]#networkAddress"
            ],
            "cn": [
                "person1"
            ],
            "givenName": [
                "person1_givenname"
            ],
            "GUID": [
                "f89e2c45-1a6c-0049-a395-f89e2c451a6c"
            ],
            "objectClass": [
                "inetOrgPerson",
                "organizationalPerson",
                "Person",
                "ndsLoginProperties",
                "Top"
            ],
            "sn": [
                "person1_surname"
            ]
        },
        "dn": "cn=person1,o=test"
    }

To obtain already formatted values you must request the schema in the Server object with get_info=SCHEMA or get_info=ALL.


Extended logging
----------------

To get an idea of what happens when you perform a Search operation this is the extended log from a session to an OpenLdap
server from a Windows client with dual stack IP::

    # Initialization:

    INFO:ldap3:ldap3 library initialized - logging emitted with loglevel set to DEBUG - available detail levels are: OFF, ERROR, BASIC, PROTOCOL, NETWORK, EXTENDED - sensitive data will be hidden
    DEBUG:ldap3:ERROR:detail level set to EXTENDED
    DEBUG:ldap3:ERROR:hide sensitive data set to True
    DEBUG:ldap3:BASIC:instantiated Server: <Server(host='openldap', port=389, use_ssl=False, get_info='NO_INFO')>
    DEBUG:ldap3:BASIC:instantiated Usage object
    DEBUG:ldap3:BASIC:instantiated <SyncStrategy>: <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - closed - <no socket> - tls not started - not listening - No strategy - async - real DSA - not pooled - cannot stream output>
    DEBUG:ldap3:BASIC:instantiated Connection: <Connection(server=Server(host='openldap', port=389, use_ssl=False, get_info='NO_INFO'), user='cn=admin,o=services', password='<stripped 8 characters of sensitive data>', auto_bind='NONE', version=3, authentication='SIMPLE', client_strategy='SYNC', auto_referrals=True, check_names=True, collect_usage=True, read_only=False, lazy=False, raise_exceptions=False)>
    DEBUG:ldap3:NETWORK:opening connection for <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - closed - <no socket> - tls not started - not listening - SyncStrategy>
    DEBUG:ldap3:BASIC:reset usage metrics
    DEBUG:ldap3:BASIC:start collecting usage metrics
    DEBUG:ldap3:BASIC:address for <ldap://openldap:389 - cleartext> resolved as <[<AddressFamily.AF_INET6: 23>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('fe80::215:5dff:fe8f:2f0d%20', 389, 0, 20)]>
    DEBUG:ldap3:BASIC:address for <ldap://openldap:389 - cleartext> resolved as <[<AddressFamily.AF_INET: 2>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('192.168.137.104', 389)]>
    DEBUG:ldap3:BASIC:obtained candidate address for <ldap://openldap:389 - cleartext>: <[<AddressFamily.AF_INET6: 23>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('fe80::215:5dff:fe8f:2f0d%20', 389, 0, 20)]> with mode IP_V6_PREFERRED
    DEBUG:ldap3:BASIC:obtained candidate address for <ldap://openldap:389 - cleartext>: <[<AddressFamily.AF_INET: 2>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('192.168.137.104', 389)]> with mode IP_V6_PREFERRED


    # Opening the connection (trying IPv6 then IPv4):

    DEBUG:ldap3:BASIC:try to open candidate address [<AddressFamily.AF_INET6: 23>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('fe80::215:5dff:fe8f:2f0d%20', 389, 0, 20)]
    DEBUG:ldap3:ERROR:<socket connection error: [WinError 10061] No connection could be made because the target machine actively refused it.> for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - closed - <local: [::]:50396 - remote: [None]:None> - tls not started - not listening - SyncStrategy>
    DEBUG:ldap3:BASIC:try to open candidate address [<AddressFamily.AF_INET: 2>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('192.168.137.104', 389)]
    DEBUG:ldap3:NETWORK:connection open for <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:49445 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:refreshing server info for <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:49445 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>


    # Authenticating to the LDAP server with the Simple Bind method:

    DEBUG:ldap3:BASIC:start BIND operation via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:49445 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:performing simple BIND for <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:49445 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:simple BIND request <{'version': 3, 'authentication': {'sasl': None, 'simple': '<stripped 8 characters of sensitive data>'}, 'name': 'cn=admin,o=services'}> sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:49445 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:new message id <1> generated
    DEBUG:ldap3:NETWORK:sending 1 ldap message for <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:49445 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:49445 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>:
    >>LDAPMessage:
    >> messageID=1
    >> protocolOp=ProtocolOp:
    >>  bindRequest=BindRequest:
    >>   version=3
    >>   name=b'cn=admin,o=services'
    >>   authentication=AuthenticationChoice:
    >>    simple=<stripped 8 characters of sensitive data>
    DEBUG:ldap3:NETWORK:sent 41 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:49445 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 14 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:49445 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 1 ldap messages via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:49445 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message received via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:49445 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>:
    <<LDAPMessage:
    << messageID=1
    << protocolOp=ProtocolOp:
    <<  bindResponse=BindResponse:
    <<   resultCode='invalidCredentials'
    <<   matchedDN=b''
    <<   diagnosticMessage=b''
    DEBUG:ldap3:PROTOCOL:BIND response <{'message': '', 'description': 'invalidCredentials', 'type': 'bindResponse', 'saslCreds': None, 'result': 49, 'dn': '', 'referrals': None}> received via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:49445 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:done BIND operation, result <False>


    # Performing the Search operation:

    DEBUG:ldap3:BASIC:start SEARCH operation via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:49445 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:SEARCH request <{'attributes': ['objectClass', 'sn'], 'dereferenceAlias': 3, 'filter': '(cn=test*)', 'timeLimit': 0, 'sizeLimit': 0, 'scope': 2, 'typesOnly': False, 'base': 'o=test'}> sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:49445 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:new message id <2> generated
    DEBUG:ldap3:NETWORK:sending 1 ldap message for <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:49445 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:49445 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>:
    >>LDAPMessage:
    >> messageID=2
    >> protocolOp=ProtocolOp:
    >>  searchRequest=SearchRequest:
    >>   baseObject=b'o=test'
    >>   scope='wholeSubtree'
    >>   derefAliases='derefAlways'
    >>   sizeLimit=0
    >>   timeLimit=0
    >>   typesOnly='False'
    >>   filter=Filter:
    >>    substringFilter=SubstringFilter:
    >>     type=b'cn'
    >>     substrings=Substrings:
    >>      Substring:
    >>       initial=b'test'
    >>   attributes=AttributeSelection:
    >>    b'objectClass'    b'sn'
    DEBUG:ldap3:NETWORK:sent 63 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:49445 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 114 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:49445 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 1 ldap messages via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:49445 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message received via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:49445 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>:
    <<LDAPMessage:
    << messageID=2
    << protocolOp=ProtocolOp:
    <<  searchResEntry=SearchResultEntry:
    <<   object=b'cn=testSASL,o=test'
    <<   attributes=PartialAttributeList:
    <<    PartialAttribute:
    <<     type=b'sn'
    <<     vals=Vals:
    <<      b'testSASL'
    <<    PartialAttribute:
    <<     type=b'objectClass'
    <<     vals=Vals:
    <<      b'inetOrgPerson'      b'organizationalPerson'      b'person'      b'top'
    DEBUG:ldap3:NETWORK:received 14 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:49445 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 1 ldap messages via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:49445 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message received via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:49445 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>:
    <<LDAPMessage:
    << messageID=2
    << protocolOp=ProtocolOp:
    <<  searchResDone=SearchResultDone:
    <<   resultCode='success'
    <<   matchedDN=b''
    <<   diagnosticMessage=b''
    DEBUG:ldap3:PROTOCOL:SEARCH response entry <{'attributes': {'sn': ['testSASL'], 'objectClass': ['inetOrgPerson', 'organizationalPerson', 'person', 'top']}, 'dn': 'cn=testSASL,o=test', 'type': 'searchResEntry', 'raw_attributes': {'sn': [b'testSASL'], 'objectClass': [b'inetOrgPerson', b'organizationalPerson', b'person', b'top']}}> received via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:49445 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:done SEARCH operation, result <True>


    # Closing the connnection (via the Unbind operation):

    DEBUG:ldap3:BASIC:start UNBIND operation via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:49445 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:UNBIND request sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:49445 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:new message id <3> generated
    DEBUG:ldap3:NETWORK:sending 1 ldap message for <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:49445 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:49445 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>:
    >>LDAPMessage:
    >> messageID=3
    >> protocolOp=ProtocolOp:
    >>  unbindRequest=b''
    DEBUG:ldap3:NETWORK:sent 7 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:49445 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:closing connection for <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:49445 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:connection closed for <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - closed - <no socket> - tls not started - not listening - SyncStrategy>
    DEBUG:ldap3:BASIC:stop collecting usage metrics
    DEBUG:ldap3:BASIC:done UNBIND operation, result <True>

These are the usage metrics of this session::

    Connection Usage:
      Time: [elapsed:        0:00:01.126074]
        Initial start time:  2015-07-16T07:40:46.871386
        Open socket time:    2015-07-16T07:40:46.871386
        Close socket time:   2015-07-16T07:40:47.997460
      Server:
        Servers from pool:   0
        Sockets open:        1
        Sockets closed:      1
        Sockets wrapped:     0
      Bytes:                 253
        Transmitted:         111
        Received:            142
      Messages:              6
        Transmitted:         3
        Received:            3
      Operations:            3
        Abandon:             0
        Bind:                1
        Add:                 0
        Compare:             0
        Delete:              0
        Extended:            0
        Modify:              0
        ModifyDn:            0
        Search:              1
        Unbind:              1
      Referrals:
        Received:            0
        Followed:            0
      Restartable tries:     0
        Failed restarts:     0
        Successful restarts: 0
