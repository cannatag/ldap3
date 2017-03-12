Schema
======

An LDAP server store information about *types* it can handle in its **schema**. The schema includes all information needed by a client to correctly performs
LDAP operations. Let's examine an LDAP server schema::

    >>> server.schema
    DSA Schema from: cn=schema
      Attribute types:{'ipaNTTrustForestTrustInfo': Attribute type: 2.16.840.1.113730.3.8.11.17
      Short name: ipaNTTrustForestTrustInfo
      Description: Forest trust information for a trusted domain object
      Equality rule: octetStringMatch
      Syntax: 1.3.6.1.4.1.1466.115.121.1.40 [('1.3.6.1.4.1.1466.115.121.1.40', 'LDAP_SYNTAX', 'Octet String', 'RFC4517')]
      'ntUserCreateNewAccount': Attribute type: 2.16.840.1.113730.3.1.42
      Short name: ntUserCreateNewAccount
      Description: Netscape defined attribute type
      Single Value: True
      Syntax: 1.3.6.1.4.1.1466.115.121.1.15 [('1.3.6.1.4.1.1466.115.121.1.15', 'LDAP_SYNTAX', 'Directory String', 'RFC4517')]
      Extensions:
        X-ORIGIN: Netscape NT Synchronization
      'passwordGraceUserTime': Attribute type: 2.16.840.1.113730.3.1.998
      Short name: passwordGraceUserTime, pwdGraceUserTime
      Description: Netscape defined password policy attribute type
      Single Value: True
      Usage: Directory operation
      Syntax: 1.3.6.1.4.1.1466.115.121.1.15 [('1.3.6.1.4.1.1466.115.121.1.15', 'LDAP_SYNTAX', 'Directory String', 'RFC4517')]
      Extensions:
        X-ORIGIN: Netscape Directory Server
      'nsslapd-ldapilisten': Attribute type: 2.16.840.1.113730.3.1.2229
      Short name: nsslapd-ldapilisten
      Description: Netscape defined attribute type
      Single Value: True
      Syntax: 1.3.6.1.4.1.1466.115.121.1.15 [('1.3.6.1.4.1.1466.115.121.1.15', 'LDAP_SYNTAX', 'Directory String', 'RFC4517')]
      Extensions:
        X-ORIGIN: Netscape Directory Server
      'bootParameter': Attribute type: 1.3.6.1.1.1.1.23
      Short name: bootParameter
      Description: Standard LDAP attribute type
      Syntax: 1.3.6.1.4.1.1466.115.121.1.26 [('1.3.6.1.4.1.1466.115.121.1.26', 'LDAP_SYNTAX', 'IA5 String', 'RFC4517')]
      Extensions:
        X-ORIGIN: RFC 2307

      <...long list of descriptors...>


The schema is a very long list that describes what kind of data types the LDAP server understands. It also specifies
what attributes can be stored in each class. Some classes are containers for other entries (either container or leaf)
and are used to build the hierarchy of the DIT. Container entries can have attributes too.
One important specification in the schema is if the attribute is *multi-valued* or not. A multi-valued attribute can store one or more values.
Every LDAP server must at least support the standard LDAP3 schema but can have additional custom classes and attributes.
The schema defines also the *syntaxes* and the *matching rules* of the different kind of data types stored in the LDAP.

.. note::
   Object classes and attributes are independent objects. An attribute is not a "child" of a class neither a
   class is a "parent" of any attribute. Classes and attributes are linked in the schema with the ``MAY`` and ``MUST`` options
   of the object class definition that specify what attributes an entry can contain and which of them are mandatory.

.. note::
   There are 3 different types of object classes: **ABSTRACT** (used only when defining the class hierarchy), **STRUCTURAL** (used to
   create concrete entries) and **AUXILIARY** (used to add additional attributes to an entry). Only one structural class can be used
   in an entry, while many auxiliary classes can be added to the same entry. Adding an object class to an entry simply means
   that the attributes defined in that object class can be stored in that entry.

If the ldap3 library is aware of the schema used by the LDAP server it will try to automatically convert data retrieved by the Search
operation to their representation. An integer will be returned as an int, a generalizedDate as a datetime object and so on.
If you don't read the schema all the values are returned as bytes and unicode strings. You can control this behaviour with
the ``get_info`` parameter of the Server object and the ``check_names`` parameter of the Connection object.

The schema can be extended by the user, but the LDAP RFCs don't specify how this operation must be performed, so each LDAP server has its
own method of adding classes and attributes to the schema.

Operational attributes
----------------------
The LDAP server store *operational* information on each entry. This information is used by the internal mechanism of the server and *can* be made
available to the user via an **operational attribute** that can usually be read but not written.

To request all operational attribute in a search you can use the ``+`` (PLUS) character as an attribute name. Keep in mind that the server
may not return some operational attribute if they are not explicitly requested (because they may take a long time or many resources to be computed),
so if you need a specific attribute is better to request it explicitly.

Some server may not return attribute information in the schema. In this case the ldap3 library is not aware of them. This can lead to some erratic
behaviour, especially in the Abstraction Layer of ldap3.

In this case you can tell ldap3 to not check for a specific attribute::

    from ldap3 import get_config_parameter, set_config_parameter
    attrs = get_config_parameter('ATTRIBUTES_EXCLUDED_FROM_CHECK')
    attrs.extend(['memberOf', 'entryUUID', 'pwdChangedTime'])  # # all the missing attributes you need
    set_config_parameter('ATTRIBUTES_EXCLUDED_FROM_CHECK', attrs)

Now the missing attributes can be used in searches.

Then, if you're using the Abstraction Layer you must instruct the ObjectDef to query for those attributes too. For example, if you
want to query *inetOrgPerson* in a Reader Cursor of the Abstraction Layer::

    from ldap3 import Connection, ObjectDef, Reader
    c = Connection('my_server', 'my_user', 'my_password')
    c.bind()
    person = ObjectDef('inetOrgPerson', c)  # read the object class hierarchy schema from the server
    person += ['memberOf', 'entryUUID', 'pwdChangedTime'] # this creates the missing AttrDef in the ObjectDef
    r = Reader(c, person, 'my_base')
    r.serch()

when you query the ``r`` cursor you'll get back the missing attributes too.
