####################
The SEARCH operation
####################

The **Search** operation is used to request a server to return, subject to access controls and other restrictions,
a set of entries matching a search filter. This can be used to read attributes from a single entry, from entries
immediately subordinate to a particular entry, or from a whole subtree of entries. The filter syntax is described in RFC 4515 .

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
If the search filter contains the following characters you must use the relevant escape ASCII sequence, as per RFC4515
(section 3): '*' -> '\\\\2A', '(' -> '\\\\28', ')' -> '\\\\29', '\\' -> '\\\\5C', chr(0) -> '\\\\00'.

* search_scope: specifies how broad the search context is:

    * BASE: retrieves attributes of the entry specified in the search_base.

    * LEVEL: retrieves attributes of the entries specified in the search_base. The base must reference a container object.

    * SUBTREE: retrieves attributes of the entries specified in the search_base and all subordinate containers downward.

* dereference_aliases: specifies how the server must treat references to other entries:

    * DEREF_NEVER: never dereferences entries, returns alias objects instead. The alias contains the reference to the real entry.

    * DEREF_SEARCH: while searching subordinates of the base object, dereferences any alias within the search scope.
Dereferenced objects become the bases of further search scopes where the Search operation is also applied.
The server should eliminate duplicate entries that arise due to alias dereferencing while searching.

    * DEREF_BASE: dereferences aliases in locating the base object of the search, but not when searching subordinates
of the base object.

    * DEREF_ALWAYS: always returns the referenced entries, not the alias object.

* attributes: a single attribute or a list of attributes to be returned by the search (defaults to None).
If attributes is None no attribute is returned. If attributes is ALL_ATTRIBUTES all attributes are returned.

* size_limit: maximum number of entries returned by the search (defaults to None).
If None the whole set of found entries is returned, unless the server has a more restrictive rule.

* time_limit: number of seconds allowed for the search (defaults to None).
If None the search can take an unlimited amount of time, unless the server has a more restrictive rule.

* types_only: doesn't return attribute values.

* get_operational_attributes: if True returns information attributes (managed automatically by the server) for each entry.

* controls: additional controls to send in the request.

* paged_size: if paged_size is greater than 0 a simple paged search is executed as described in RFC2696 (defaults to None).
The search will return at most the specified number of entries.

* paged_criticality: if True the search will be executed only if the server is capable of performing a simple paged search.
If False and the server is not capable of performing a simple paged search a standard search will be executed.

* paged_cookie: an *opaque* string received in a paged paged search that must be sent back while requesting
subsequent entries of the search result.

The LDAP filter
---------------

The LDAP filter defines the conditions that must be fulfilled in order for the Search to match a given entry and must follow
the syntax defined in RFC 4515. The filter is composed of assertions that can be joined with AND (&) or OR (|) operators,
or negated with the NOT (!) operator. The AND, OR, and NOT choices can be used to form combinations of complex filters.
At least one filter element must be present in an AND or OR choice.

A filter is evaluated by the server to TRUE, FALSE, or Undefined.  A filter item evaluates to Undefined when the server
is not able to determine whether the assertion value matches an entry (for example when the matching rule is not defined
for an attribute, when the type of filter is not implemented by the server or when the value is invalid). If the filter
evaluates to TRUE for a particular entry the attributes requested in the Search operation are returned for that entry as
part of the Search result (subject to any applicable access control restrictions). If the filter evaluates to FALSE or
Undefined, then the entry is ignored for the Search operation.

An AND is TRUE if all the filters in the set evaluate to TRUE, FALSE if at least one filter is FALSE and Undefined otherwise.
An OR is TRUE if at least one filter evaluate to TRUE, FALSE if all the filters in the set evaluate to FALSE and Undefined
otherwise. A NOT is TRUE if the filter being negated is FALSE, FALSE if it is TRUE, and Undefined if it is Undefined.

A filter is formed by 3 parts: the attribute name, a matching operator, and the matched value. The filter itself is surrounded
by parentheses, as in "(sn=Smith)". The LDAP schema defines how each attribute matching rule and ordering rule is evaluated.

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
attribute, this filter item should be treated as an equality filter by the server. The approximate algorithm, if available,
is local to the server so you should check your server documentation to see if this matching operator can be used.

* EXTENSIBLE (attribute:=value): in the extensible filter the attribute part of the filter is augmented with other
information (separated by a colon ":" as in "(o:dn:=Ace Industry)") to achieve particular search behaviours. Please
check the documentation of your LDAP server to see what EXTENSIBLE syntax is available.


NOT, AND and OR
+++++++++++++++

You can negate the result of a filter with the NOT (!) operator as in::

    (!(sn=Smith))  # retrieves all entries where the sn is not Smith

You can join more than one attributes with the AND (%) and the OR (|) operator to create a complex filter. The AND and
OR operator have their own parentheses that include all the filter in the set::

    (&(givenName=A*)(sn=Smith))  # retrieves all entries where sn attribute is Smith and givenName starts with A.
    (|(sn=Smith)(sn=Johnson))  # retrieves all entries where sn is Smith or Johnson.

You can even mix the NOT, AND and OR to form a more complex filter as in::

    (|(&(objectClass=inetOrgPerson)(!(cn=Smith))(cn=admin*))  # retrieves all entries whose cn starts with admin and all entries
    of class inetOrgPerson with a surname different from Smith


Search scope and aliases
------------------------

The scope of the search specifies how broad the search context will be. The ldap database is a hierarchical structure
(similar to a traditional file system) with a root and with container and leaf objects. a container can be stored in other
containers, but not in a leaf object. It must be clear that containers and leafs structure has nothing to do with the group
and group membership objects. A group (groupOfNames) object is a leaf object with a member attribute that conteins references
to other leaf objects.

The only way to know if an object is a container or a leaf object is to query the LDAP server schema for that object's class.

There are three possible scopes:

* BASE: the scope is constrained to the entry named by search_base.

* LEVEL: the scope is constrained to the immediate subordinates of the entry named by search_base.

* SUBTREE: the scope is constrained to the entry named by search_base and to all its subordinates.

An object can be an alias of another one defined somewhere in the LDAP data structure (it is similar to a link inside the
LDAP database). While searching you can specify if "dereference" must be applied to the found aliases. The act of dereferencing
an alias includes recursively dereferencing aliases that refer to aliases. The LDAP server should detect looping while
dereferencing aliases in order to prevent denial-of-service attacks of this nature.

There are four possible ways of manage aliases while searching:

* DEREF_NEVER: never dereferences entries, returns alias objects instead. The alias contains the reference to the real entry.

* DEREF_SEARCH: while searching subordinates of the base object, dereferences any alias within the search scope.
Dereferenced objects become the bases of further search scopes where the Search operation is also applied. If the search
scope is SUBTREE, the Search continues in the subtree(s) of any dereferenced object. If the search scope is LEVEL, the
search is applied to any dereferenced objects and is not applied to their subordinates.
Servers should eliminate duplicate entries that arise due to alias dereferencing while searching.

* DEREF_BASE: dereferences aliases in locating the base object of the search, but not when searching subordinates
of the base object.

* DEREF_ALWAYS: Dereference aliases both in searching and in locating the base object of the Search.


Attributes
----------
There are two kind of attributes defined in the LDAP schema: User attributes and Operational Attributes. User attribute
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
entry found in the search the ldap3 library request you to specify at least one attribute in the attributes list, else it
will perform a "1.1" Search request that returns only the dn of the entries found. To get all the user attributes you can
use::

    attributes=ldap3.ALL_ATTRIBUTE

while to get all the user and all the operational attributes you can use::

    attributes=[ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES]


Keep in mind that the server can decide to not return some operational attribute if they are not explicitly requested
(because they may take a long time or many resources to be computed), so if you need a specific attribute is better to
request it explicitly.

To request the operational attributes you can even set the get_operational_attributes parameter to True.



