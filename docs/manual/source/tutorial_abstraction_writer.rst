Tutorial: ldap3 Abstraction Layer - Writing data
################################################

Writing entries
---------------

To add or update entries on an LDAP server you must apply modifications to Entries in a Writer cursor and then commit the pending
changes to the DIT. By design a Writer Cursor has no Search capability because it can be only used to create new Entries or to
modify Entries already retrieved by a Reader cursor or by an LDAP Search operation. You can get a Writer cursor in a number of ways:

* from a Reader Cursor, using the ``from_cursor()`` static method that populates the ``entries`` collection with a copy of Entries
  from the original cursor

* from a Search response, using the ``from_response`` static method, that populates the ``entries`` collection with a copy of Entries
  from the original Search response

* from a single Entry in a Reader cursor, using the ``entry_writable()`` method of the Entry, that returns a new Entry (with a temporary Writer Cursor)

* from a single Entry in a Search response, using the ``entry_writable()`` method of the Entry, that returns a new Entry (with a temporary Writer Cursor)

* as a new instance of the ldap3.Writer class, this creates a Writer with an empty ``entries`` collection where can only create new Entries.

Let's obtain a Writer cursor from the Reader we used in the previsous chapter::

    >>> w = Writer.from_cursor(r)
    >>> w


Once you have obtained a Writer cursor you can modify its Entries in the usual pythonic way: