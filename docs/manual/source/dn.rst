DN parsing
##########

``ldap3.utils.dn`` offers functions to work with DNs:

* ``parse_dn(dn, escape=False, strip=False)``: Parses a DN into syntactic components, and validates it.
* ``to_dn(iterator, decompose=False, remove_space=False, space_around_equal=False, separate_rdn=False)`` takes an iterator and converts it to a list of DN parts.
* ``safe_dn(dn, decompose=False, reverse=False)``: Normalizes and escapes a DN. If the DN is a sequence, it is joined first.
* ``to_rdn(dn, decompose=False)``: Returns a list of RDN for the DN.
* ``escape_rdn(rdn)``: Escapes according to RFC 4514 to prevent injection attacks.

parse_dn
--------

Parses a DN into syntactic components. This also validates the DN syntactically, and raises ``LDAPInvalidDnError`` if the DN is invalid.

The result is a list of 3-tuples:

* The attribute type, e.g. "cn"
* Attribute value ("admin")
* The separator, if set: ``,`` (COMMA) or ``+`` (PLUS), or empty string.

Example::

   >>> parse_dn("uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org")
   [('uid', 'admin', ','), ('cn', 'users', ','), ('cn', 'accounts', ','), ('dc', 'demo1', ','), ('dc', 'freeipa', ','), ('dc', 'org', '')]

An invalid DN::

   >>> parse_dn("uid=a#dmin,cn=users")
   Traceback (most recent call last):
     -- snip --
   ldap3.core.exceptions.LDAPInvalidDnError: special character # must be escaped

Escaping the invalid character::

   >>> parse_dn("uid=a#dmin,cn=users", escape=True)
   [('uid', 'a\\#dmin', ','), ('cn', 'users', '')]

Stripping whitespace::

   >>> parse_dn("uid=admin ,cn=users", strip=True)
   [('uid', 'admin', ','), ('cn', 'users', '')]

Without ``strip=True``, this would result in the following exception::

   ldap3.core.exceptions.LDAPInvalidDnError: SPACE must be escaped as trailing character of attribute value

Escaping and stripping can be used simultaneously, if course.


to_dn
-----

tbd

safe_rdn
--------

tbd

to_rdn
------

tbd

escape_rdn
----------

tbd
