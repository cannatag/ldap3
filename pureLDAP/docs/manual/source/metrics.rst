##################
Connection metrics
##################

If you set the collect_usage parameter to True in a Connection object creation the metrics system is activated.
You get the 'usage' attribute in the connection object populated with an instance of the ConnectionUsage class.

ConnectionUsage stores counters for each operation performed in the Connection, you get metrics for the following fields:

* initial_connection_start_time:
* open_socket_start_time:
* connection_stop_time:
* opened_sockets:
* closed_sockets:
* wrapped_sockets:
* bytes_transmitted:
* bytes_received:
* messages_transmitted:
* messages_received:
* operations:
* abandon_operations
* add_operations
* bind_operations
* compare_operations
* delete_operations
* extended_operations
* modify_operations
* modify_dn_operations
* search_operations
* unbind_operations
* restartable_failures
* restartable_successes
* servers_from_pool

Metrics are properly collected while the connection is open, stopped as the connection is closed and reset if the connection is used again.
While using a ServerPool or a restartable strategy the metrics are not reset when the server is changed.

You can reset the usage metrics with the connection.usage.reset() method.
