Tutorial: ldap3 Abstraction Layer - Writing data
################################################

Writing entries
---------------

By design a Writer Cursor has no Search capability because it can be only used to create new Entries or to modify the Entries in a Reader
cursor or in an LDAP Search operation.

Instead of the search_* methods the Writer has the following methods:

- from_cursor: creates a Writer cursor from a Reader cursor, populated with a copy of the Entries in the Reader cursor

- from_response: create a Writer cursor from a Search operation response, populated with a copy of the Entries in the Search response

- commit: writes all the pending changes to the DIT

- discard: discards all the pending changes

- new: creates a new Entry

- refresh_entry: re-reads the Entry from the DIT
