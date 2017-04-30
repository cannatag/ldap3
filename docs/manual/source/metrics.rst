Connection metrics
##################

If you set the collect_usage parameter to True in a Connection object the metrics feature is activated.
You get the 'usage' attribute in the connection object populated with an instance of the ConnectionUsage class.

ConnectionUsage stores counters for each operation performed in the Connection, you get metrics for the following fields:

* initial_connection_start_time
* open_socket_start_time:
* connection_stop_time:
* servers_from_pool:
* open_sockets:
* closed_sockets:
* wrapped_sockets:
* bytes_transmitted:
* bytes_received:
* messages_transmitted:
* messages_received:
* operations:
* abandon_operations:
* bind_operations:
* add_operations:
* compare_operations:
* delete_operations:
* extended_operations:
* modify_operations:
* modify_dn_operations:
* search_operations:
* unbind_operations:
* referrals_received:
* referrals_followed:
* referrals_connections:
* restartable_failures:
* restartable_successes:

Metrics are properly collected while the connection is open, kept while it's closed and reset if the connection is used again.
While using a ServerPool or a restartable strategy the metrics are not reset when the server is changed.

You can reset the usage metrics with the connection.usage.reset() method.

You can print out the metrics at any time of execution of your code with::

    print(connection.usage)

and get the formatted metrics::

    Connection Usage:
      Time: [elapsed:        0:00:00.028885]
        Initial start time:  2015-06-29T01:44:17.772645
        Open socket time:    2015-06-29T01:44:17.772645
        Close socket time:   2015-06-29T01:44:17.801530
      Server:
        Servers from pool:   0
        Sockets open:        1
        Sockets closed:      1
        Sockets wrapped:     0
      Bytes:                 62
        Transmitted:         48
        Received:            14
      Messages:              3
        Transmitted:         2
        Received:            1
      Operations:            2
        Abandon:             0
        Bind:                1
        Add:                 0
        Compare:             0
        Delete:              0
        Extended:            0
        Modify:              0
        ModifyDn:            0
        Search:              0
        Unbind:              1
      Referrals:
        Received:            0
        Followed:            0
        Connections:         0
      Restartable tries:     0
        Failed restarts:     0
        Successful restarts: 0

