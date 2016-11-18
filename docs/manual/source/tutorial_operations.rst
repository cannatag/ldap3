#############################
Tutorial: Database operations
#############################

.. warning:: **A more pythonic LDAP**: LDAP operations look clumsy and hard-to-use because they reflect the old-age idea that time-consuming operations
    should be done on the client to not clutter and hog the server with unneeded elaboration. ldap3 includes a fully functional **Abstraction
    Layer** that lets you interact with the DIT in a modern and *pythonic* way. With the Abstraction Layer you don't need to directly issue any
    LDAP operation at all.

In the previous chapter of this tutorial we have tried to access some data in the LDAP database. As any system that stores data, LDAP lets you perform
the standard CRUD (Create, Read, Update, Delete) operations, but their usage is someway rudimentary.
Again, if you think of the intended use of the original DAP protocol (storing key-values pairs related to an entry in a phone directory)
this makes sense: an entry is written once, seldom modified, and eventually deleted, so the create (**Add** in LDAP), update (**Modify** or **ModifyDn**)
and delete (**Delete**) operations have a very basic usage while the Read (**Search**) operation is richer in options, but lacks many capabilities
you would expect in a modern query language (as 1 to N relationship, joining views, or server data manipulation). Nonetheless almost everything you can do
in a modern database can be equally done with LDAP. Furthermore consider that even if an LDAP server can be accessed by multiple clients simultaneously,
the LDAP protocol itself has no notion of "transaction", so if you want to issue multiple Add or Modify operations in an atomic way (to keep data
consistent), you must investigate the extended operations of the specific LDAP server you're connecting to to check if it provides transactions for
multiple operations via Controls or Extended operations.

.. note:: Synchronous vs Asynchronous: you can submit operations to the server in two different ways: **synchronous** mode and **asynchronous**
    mode. While with the former you send the request and immediately get the response, in the latter the ldap3 library constantly listens to the
    server (it uses one independent thread for each connection). When you send a request you must store its *message id* (a unique number that
    ldap3 stamps on every message of your LDAP session) in your code so you can later query the Connection object for the relevant response when
    it's ready. You'll probably stick with the synchronous mode, because nowadays LDAP servers are fast to respond, but the asynchronous mode is
    still useful if your program is event-driven (maybe using an asynchronous event loop).

    ldap3 supports both of this models with its different *communication strategies*.

LDAP also provides the **Compare** operation that returns True only if an attribute has the value you specify in the request. Even if this operation seems
redundant (you could read the attribute and perform the comparison using more powerful tools in your code) you need it to check for the presence
of a value (even in a multi-valued attribute) without having the permission to read it. This obviuosly relies upon some "access restriction" mechanism
that must be present on the server. LDAP doesn't specify how this mechanism works, so each LDAP server has its specific way of handling authorization.
The Compare operation is also used to check the validity of a password (that you can't read) without performing a Bind operation with the specific user.

After any synchronous operation, you'll find the following attributes populated in the Connection object:

* ``result``: the result of the last operation (as returned by the server)
* ``response``: the entries found (if the last operation is a Search)
* ``entries``: the entries found exposed via the ldap3 Abstraction Layer (if the last operation is a Search)
* ``last_error``: the error, if any,  occurred in the last operation
* ``bound``: True if the connection is bound to the server
* ``listening``: True if the socket is listening to the server
* ``closed``: True if the socket is not open

Create an Entry
===============
Let's try to add some data to the LDAP DIT::

    >>> # Create a container for new entries
    >>> conn.add('ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', 'organizationalUnit')
    True
    >>> # Add a new user
    >>> conn.add('cn=b.young,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', 'inetOrgPerson', {'givenName': 'Beatrix', 'sn': 'Young', 'departmentNumber': 'DEV', 'telephoneNumber': 1111})
    True

As you can see we have created a container object and stored a new user in it. You passed the full DN as the first parameter, the objectClass (or objectClasses)
as second parameter and a dictonary of attributes as the third parameter. Some attributes are mandatory when adding a new object. You can check the schema to know which are
the mandatory attributes you need to provide to successfully create a new object.

Looking at the schema for the *inetOrgPerson* object class we find that there are no mandatory attributes::

    >>> server.schema.object_classes['inetOrgPerson']
    Object class: 2.16.840.1.113730.3.2.2
      Short name: inetOrgPerson
      Superior: organizationalPerson
      May contain attributes: audio, businessCategory, carLicense, departmentNumber, displayName, employeeNumber, employeeType, givenName, homePhone, homePostalAddress, initials, jpegPhoto, labeledURI, mail, manager, mobile, o, pager, photo, roomNumber, secretary, uid, userCertificate, x500UniqueIdentifier, preferredLanguage, userSMIMECertificate, userPKCS12
      Extensions:
        X-ORIGIN: RFC 2798

The *inetOrgPerson* object class is a subclass of the *organizationalPerson* object that again doesn't include any mandatory attributes::

    >>> server.schema.object_classes['organizationalPerson']
    Object class: 2.5.6.7
      Short name: organizationalPerson
      Superior: person
      May contain attributes: title, x121Address, registeredAddress, destinationIndicator, preferredDeliveryMethod, telexNumber, teletexTerminalIdentifier, internationalISDNNumber, facsimileTelephoneNumber, street, postOfficeBox, postalCode, postalAddress, physicalDeliveryOfficeName, ou, st, l
      Extensions:
        X-ORIGIN: RFC 4519
      OidInfo: ('2.5.6.7', 'OBJECT_CLASS', 'organizationalPerson', 'RFC4519')

The *organizationalPerson* object class is a subclass of the *person* object where we finally find two mandatory attributes::

    >>> server.schema.object_classes['person']
    Object class: 2.5.6.6
      Short name: person
      Superior: top
      Must contain attributes: sn, cn
      May contain attributes: userPassword, telephoneNumber, seeAlso, description
      Extensions:
        X-ORIGIN: RFC 4519
      OidInfo: ('2.5.6.6', 'OBJECT_CLASS', 'person', 'RFC4519')

The *person* object class is a subclass of the *top* object. Let's walk up the hierarchy chain::

    Object class: 2.5.6.0
      Short name: top
      Must contain attributes: objectClass
      Extensions:
        X-ORIGIN: RFC 4512
      OidInfo: ('2.5.6.0', 'OBJECT_CLASS', 'top', 'RFC4512')

*top* is the root of all LDAP classes and defines a single mandatory attributes *objectClass*. Now we know that to successfully create an *inetOrgPerson* we need to provide
the *sn*, the *cn* and the *objectClass* attributes at creation time. Let's read the objectClass attribute of the user we created::

    >>> conn.search('ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', '(cn=*)', attributes=['objectClass'])
    True
    >>> conn.entries[0]
    DN: cn=b.young,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org - STATUS: Read - READ TIME: 2016-10-09T17:36:44.100248
    objectClass: inetOrgPerson
                 organizationalPerson
                 person
                 top

You can see that *objectClass* is composed of all the hierarchical structure from *inetOrgPerson* to *top*. This means that you can add any of the optional
attribute defined in each class of the hierarchy. If you had some *auxiliary* class to the entry you must be sure to satisfy its mandatory attributes.

Rename an entry
===============
Renaming an entry in LDAP means changing its RDN (*Relative Distinguished Name*) without changing the container where the entry is stored.
It is performed with the ModifyDN operation::

    >>> conn.modify_dn('cn=b.young,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', 'cn=b.smith')
    True

You have changed the RDN (that in this case uses the *cn* as naming attribute) of the entry from "b.young" to "b.smith". Let's check if the new value
is properly stored in the DIT::

    >>> conn.search('ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', '(cn=b.smith)', attributes=['objectclass', 'sn', 'cn', 'givenname'])
    True
    >>> conn.entries[0]
    DN: cn=b.smith,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org - STATUS: Read - READ TIME: 2016-10-11T23:51:28.731000
    cn: b.smith
    givenname: Beatrix
    objectclass: inetOrgPerson
                 organizationalPerson
                 person
                 top
    sn: Young

As you can see the new *cn* value has been stored in the *cn* attribute. To be consistent in our example we should change the *sn* (surname) from Young to Smith.
To achieve this we must wait until we introduce the Modify LDAP operation, the most difficult to use of all the LDAP operations, to update this entry.

Move entries
============
ModifyDn is really a two-face operation. You can use it to rename an entry (as in the previous example) or to move an entry to another container.
But you cannot perform this two operations together::

    >>> # Create a container for moved entries
    >>> conn.add('ou=moved, ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', 'organizationalUnit')
    True
    >>> conn.modify_dn('cn=b.smith,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', 'cn=b.smith', new_superior='ou=moved, ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org')
    True

Quite surprisingly you must provide the very same RDN even if this cannot be changed while moving the object. This could be a problem when moving entries
programmatically because you have to break up the DN to its RDNs (remember that each "step" in the DN is really an independent entry with its own RDN.

ldap3 provides the ``safe_rdn()`` helper function to return the RDN of a DN::

    >>> from ldap3.utils.dn import safe_rdn
    >>> safe_rdn('cn=b.smith,ou=moved,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org')
    [cn=b.smith]

Keep in mind that LDAP support a (quite obscure) "multi-rdn" naming option where each part of the RDN is separated with the + character::

    >>> safe_rdn('cn=b.smith+sn=young,ou=moved,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org')
    ['cn=b.smith', 'sn=young']

Update an entry
===============
To change the attributes of an object you must use the Modify operation. There are three kinds of modifications in LDAP: add, delete and replace.
**Add** is used to add values to an attribute, and creates the attribute if it doesn't exist. **Delete** deletes values from an attribute and if no values are listed, or if all
current values are listed, remove the entire attribute. **Replace** replaces all existing values of an attribute with some new values, creating the attribute if it
don't already exist.  A replace with no value will delete the entire attribute if it exists, and it is ignored if the attribute doesn't exist.

The hard part in the Modify operation is that you can mix in a single operation the three kinds of modification for a single entry with one or more attributes
each with one or more values! So the Modify operation syntax is quite complex: you must provide a DN, a dictionary of attributes and for each
attribute a list of modifications where each modification is a tuple with the modification type and the list of values. Let's add a new value to the sn attribute::

    >>> from ldap3 import MODIFY_ADD, MODIFY_REPLACE, MODIFY_DELETE
    >>> conn.modify('cn=b.smith,ou=moved,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', {'sn': [(MODIFY_ADD, ['Smyth'])]})
    True
    >>> conn.search('ou=moved,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', '(cn=b.smith)', attributes=['cn', 'sn'])
    True
    >>> conn.entries[0]
    DN: cn=b.smith,ou=moved,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org - STATUS: Read - READ TIME: 2016-10-15T08:35:39.691000
        cn: b.smith
        sn: Young
            Smyth

Now remove the old value::

    >>> conn.modify('cn=b.smith,ou=moved,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', {'sn': [(MODIFY_DELETE, ['Young'])]})
    True
    >>> conn.search('ou=moved,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', '(cn=b.smith)', attributes=['cn', 'sn'])
    True
    >>> conn.entries[0]
    DN: cn=b.smith,ou=moved,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org - STATUS: Read - READ TIME: 2016-10-15T08:35:40.331000
        cn: b.smith
        sn: Smyth

There is a typo in the previous modify operation (Smyth instead of Smith), let's fix it, replacing values with the right one::

    >>> conn.modify('cn=b.smith,ou=moved,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', {'sn': [(MODIFY_REPLACE, ['Smith'])]})
    True
    >>> conn.search('ou=moved,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', '(cn=b.smith)', attributes=['cn', 'sn'])
    True
    >>> conn.entries[0]
    DN: cn=b.smith,ou=moved,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org - STATUS: Read - READ TIME: 2016-10-15T08:35:40.972000
        cn: b.smith
        sn: Smith

Changes in a modify operation can be combined and the syntax of the operation soon becomes complex::

    >>> conn.modify('cn=b.smith,ou=moved,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', {'sn': [(MODIFY_ADD, ['Young', 'Johnson']), (MODIFY_DELETE, ['Smith'])], 'givenname': [(MODIFY_REPLACE, ['Mary', 'Jane'])]})
    True
    >>> conn.search('ou=moved,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', '(cn=b.smith)', attributes=['cn', 'sn', 'givenName'])
    True
    >>> conn.entries[0]
    DN: cn=b.smith,ou=moved,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org - STATUS: Read - READ TIME: 2016-10-15T08:55:47.585000
        cn: b.smith
        givenName: Mary
                   Jane
        sn: Young
            Johnson

Here you've added 2 values to the *sn* then removed the 'Smith' value from it and replaced the *givenName* with other 2 values, removing all older values.

.. warning:: The MODIFY_REPLACE modification has a misleading name. One could expect it replaces a value with another, but new values only are provided
    in the Modify operation. What the MODIFY_REPLACE really does is to remove **all** values and add the new values provided.
    There is no replace at all.

.. note:: The ldap3 Abstraction Layer allows you to use a much more simple and pythonic syntax to achieve the same results.

Checking attribute values
=========================
Very specific to LDAP, and usually not found in other kind of databases, is the **Compare** operation. With this operation you can check if an attribute
has a certain value even if you're not able to read it. LDAP doesn't provide a standard authorization access mechanism, so the use of this operation
is related to how the vendor has implemented the authorizazion mechanism in the LDAP server you're connecting to.

Let's assume that you don't have the right to read the *departmentNumber* attribute, and you would like to check if the 'b.smith'
user is in the 'DEV' department::

    >>> conn.compare('cn=b.smith,ou=moved,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', 'departmentNumber', 'DEV')
    True
    >>> conn.compare('cn=b.smith,ou=moved,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', 'departmentNumber', 'QA')
    False

The Compare operation is quite primitive: you can only provide a single attribute and a single value to test against. The operation returns ``True`` only if one
of the values of the attribute is equal to the value provided. Only a single value can be used and no wildcard is allowed.

The only practical use of the Compare operation is when you, as an user with administrative role, want to check the password of another user without
actually bind with that user's credentials. In this case you can test the value againts the ``userPassword`` attribute. Keep in mind the that this
only works with the Simple Password authentication method, because for other methods passwords may be stored in a different attribute, or externally to
the DIT. Also passwords can (and should) be stored with some encryption mechanism. You must read the documentation of your LDAP server to see if passwords can
be successfully checked with the Compare operation.

What's next
-----------
In the next chapter of this tutorial we will start using the **Abstraction Layer**, that hides all the LDAP machinery and
let you use standard Python objects to perform the CRUD (Create, Read, Update, Delete) operation that you expect to find in a
decent database interface. It uses an **ORM** (*Object Relational Mapper*) to link entries in the DIT with standard Python objects and
let you operate on this object in a pythonic way.

Let's move back the 'b.smith* entry to its original context and values and let's create a few more entries in that context::

    >>> conn.modify_dn('cn=b.smith,ou=moved,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', 'cn=b.smith', new_superior='ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org')
    True
    >>> conn.modify('cn=b.smith,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', {'sn': [(MODIFY_DELETE, ['Johnson'])], 'givenname': [(MODIFY_REPLACE, ['Beatrix'])]})
    True
    >>> conn.modify_dn('cn=b.smith,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', 'cn=b.young')
    >>> conn.add('cn=m.johnson,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', 'inetOrgPerson', {'givenName': 'Mary Ann', 'sn': 'Johnson', 'departmentNumber': 'DEV', 'telephoneNumber': 2222})
    True
    >>> conn.add('cn=q.gray,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', 'inetOrgPerson', {'givenName': 'Quentin', 'sn': 'Gray', 'departmentNumber': 'QA', 'telephoneNumber': 3333})
    True

There should be now three entries in the 'ldap3-tutorial' context. We will use them in the next parts of this tutorial.



