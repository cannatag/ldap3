##########################
Extended Novell operations
##########################

Novell extended operations are specific for the Novell (NetIq) eDirectory LDAP Server and return and set the universal
password of the specified user::

    extend.novell
        extend.novell.get_bind_dn()
        extend.novell.get_universal_password(user)
        extend.novell.set_universal_password(user, new_password)
