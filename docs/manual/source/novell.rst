##########################
Extended Novell operations
##########################

Novell extended operations are specific for the Novell (NetIq) eDirectory LDAP Server and return and set the universal
password of the specified user::

    extend.novell
        extend.novell.get_bind_dn()
        extend.novell.get_universal_password(user)
        extend.novell.set_universal_password(user, new_password)
        extend.novell.start_transaction()
        extend.novell.end_transaction(commit=True, controls)
        extend.novell.add_members_to_groups(members, groups, fix=True, transaction=True)
        extend.novell.remove_members_from_groups(members, groups, fix=True, transaction=True)
        extend.novell.check_groups_memberships(members, groups, fix=False, transaction=True)
        extend.novell.list_replicas()
        extend.novell.partition_entry_count()
        extend.novell.replica_info()
