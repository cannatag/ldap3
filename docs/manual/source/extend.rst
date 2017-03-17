Extend namespace
################

LDAP standard operations are quite simple, so the protocol allows the LDAP server vendor to add Extended operations
used to perform more complex operation. You can use the Connection.extended() operation to execute any operation
defined by the LDAP server vendor but it's hard to properly define the "payload" of the operation because you must describe
the operation parameters in the ASN.1 notation as requested by the server and encode them with BER encoding.

The *extend* namespace of the Connection object includes a predefined set of extended (or complex) LDAP operations that can
be performed in a simple way. The namespace is partitioned in sub-namespaces, the first is for extended operations defined in
the standard LDAP RFCs, the others groups operations for specific kinds of LDAP server.

You can call the requested operation and get the extended result back as specified in the relevant RFC or documentation
The result dictionary is augmented with the specific keys returned by the extended response.

To use an extended operation just call it in the usual way, the payload is properly encoded and decoded. for example::

    c = Connection(...)
    c.bind()
    i_am = c.extend.standard.who_am_i()

You get the response value as the return value of the function and as an additional field of
the ``result`` dictionary.


.. toctree::
   :maxdepth: 2

   standard
   novell
   microsoft

