==================
Conversion helpers
==================

In the ldap3.utils.conv you can find some helpful function to apply encoding to/from unicode:

- ``to_unicode(obj, encoding=None)``: converts a byte object to unicode, if no encoding is specified with the ``encoding`` parameter the function
  tries to use the local environment encoding.

- ``to_raw((obj, encoding='utf-8')``: converts a string to bytes, using the specified encoding (default is utf-8)

- ``escape_filter_chars(text, encoding=None):``: escapes a string for using as a value in a filter assertion. Escaping is defined in RFC4515. If no
  encoding is defined tries to use the local environment encoding.

- `escape_bytes(bytes_value)``: applies LDAP escaping to a sequence of byte values so that it can be used in an LDAP Add or Modify operation.


These functions can be used in Python 2 or Python 3 with no code changes.