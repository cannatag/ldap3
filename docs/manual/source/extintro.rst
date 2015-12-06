Some extended operations are defined in the Connection object in the 'extend' attribute.

You can call the requested operation and get the extended result back as specified in the relevant RFC or documentation
The result dictionary is augmented with the specific keys of the extended response.

Extended operations are logically grouped by their use and vendor. Ask for other extended operation
implementations on the support site of ldap3.

To use an extended operation just call it in the usual way, the payload is properly encoded and decoded. for example::

    c = Connection(....)
    c.bind()
    i_am = c.extend.standard.who_am_i()

When available you should get the response value as the return value of the function and as an additional field of
the ``result`` dictionary.
