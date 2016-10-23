Tutorial: ldap3 Abstraction Layer - Writing data
################################################

Writing entries
---------------

Modify data on an LDAP server is easy with the Abstraction Layer, just add a new Entry with its Attribute values or change the Attribute values in
an existing Entry, then commit the pending changes to the DIT via the Writer cursor. You can obtain a Writer cursor in a number of ways:

* from a Reader Cursor, using the ``Writer.from_cursor()`` static method that populates the ``entries`` collection with a copy of the Entries
  from the Reader cursor.

* from a Search response, using the ``Writer.from_response()`` static method, that populates the ``entries`` collection with a copy of the Entries
  from the Search response.

* from a single Entry in a Reader cursor, using the ``entry_writable()`` method of the Entry, that returns a new Writable
  Entry (with its Writer cursor).

* from a single Entry in a Search response, using the ``entry_writable()`` method of the Entry, that returns a new Writable
  Entry (with its Writer cursor)

* as a new instance of the ldap3.Writer class, using ``Writer()``. This creates a new Writer cursor with an empty ``entries``
  collection. With this cursor you can only create new Entries.

Let's obtain a Writer cursor from the Reader we used in the previsous chapter::

    >>> w = Writer.from_cursor(r)
    >>> w

Entries in a Writer cursor are standard Python object, so you can modify them with standard Python code::

    >>>
