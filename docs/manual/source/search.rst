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
