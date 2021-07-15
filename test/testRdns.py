""" Unit tests for utilities around reverse dns lookup """

# Created on 2020.09.16
#
# Author: Azaria Zornberg
#
# Copyright 2020 Giovanni Cannata
# Copyright 2020 Azaria Zornberg
#
# This file is part of ldap3.
#
# ldap3 is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ldap3 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ldap3 in the COPYING and COPYING.LESSER files.
# If not, see <http://www.gnu.org/licenses/>.

import unittest
from socket import gaierror

from ldap3.core.rdns import ReverseDnsSetting, get_hostname_by_addr, is_ip_addr


class Test(unittest.TestCase):

    def test_no_broken_backwards_compat_in_enum(self):
        fail_msg = ('Changing the mapping of reverse dns enum types to numeric values will break backwards '
                    'compatibility for existing clients on older versions of the ldap3 package. If new enum types '
                    'are added or functionally changed, please use new values')
        self.assertEqual(ReverseDnsSetting.OFF, (0,), fail_msg)
        self.assertEqual(ReverseDnsSetting.REQUIRE_RESOLVE_ALL_ADDRESSES, (1,), fail_msg)
        self.assertEqual(ReverseDnsSetting.REQUIRE_RESOLVE_IP_ADDRESSES_ONLY, (2,), fail_msg)
        self.assertEqual(ReverseDnsSetting.OPTIONAL_RESOLVE_ALL_ADDRESSES, (3,), fail_msg)
        self.assertEqual(ReverseDnsSetting.OPTIONAL_RESOLVE_IP_ADDRESSES_ONLY, (4,), fail_msg)

        fail_msg = ('Removing values from the set of supported values for reverse dns settings will break '
                    'backwards compatibility for existing clients on older versions of the ldap3 package. '
                    'Please do not remove values.')
        self.assertTrue(ReverseDnsSetting.OFF in ReverseDnsSetting.SUPPORTED_VALUES, fail_msg)
        self.assertTrue(ReverseDnsSetting.REQUIRE_RESOLVE_ALL_ADDRESSES in ReverseDnsSetting.SUPPORTED_VALUES, fail_msg)
        self.assertTrue(ReverseDnsSetting.REQUIRE_RESOLVE_IP_ADDRESSES_ONLY in ReverseDnsSetting.SUPPORTED_VALUES, fail_msg)
        self.assertTrue(ReverseDnsSetting.OPTIONAL_RESOLVE_ALL_ADDRESSES in ReverseDnsSetting.SUPPORTED_VALUES, fail_msg)
        self.assertTrue(ReverseDnsSetting.OPTIONAL_RESOLVE_IP_ADDRESSES_ONLY in ReverseDnsSetting.SUPPORTED_VALUES, fail_msg)

    def test_ipv4_ip_addr_checking(self):
        valid = is_ip_addr('10.254.76.5')
        self.assertTrue(valid, 'IPv4 addresses should be identified as ip addresses')

    def test_ipv6_ip_addr_checking(self):
        full_addr = '2001:0db8:0000:0000:0000:ff00:0042:8329'
        zeros_reduced_addr = '2001:db8:0:0:0:ff00:42:8329'  # equivalent to above
        consecutive_zeros_removed_addr = '2001:db8::ff00:42:8329'  # equivalent to above

        for valid_ipv6_addr in [full_addr, zeros_reduced_addr, consecutive_zeros_removed_addr]:
            valid = is_ip_addr(valid_ipv6_addr)
            self.assertTrue(valid, 'IPv6 addresses should be identified as ip addresses regardless of format. {}'.format(valid_ipv6_addr))

    def test_hostname_ip_addr_checking(self):
        valid = is_ip_addr('ldap.example.com')
        self.assertFalse(valid, 'Hostnames should not be identified as ip addresses')

    def test_success_required_option_for_lookup(self):
        addr_that_fails_to_resolve = '10.254.76.09212'  # this address isn't valid so it'll fail to resolve
        # try:
        with self.assertRaises(gaierror, msg='An exception should be raised when invoking get_hostname_by_addr with default options for an address that cannot resolve'):
            host = get_hostname_by_addr(addr_that_fails_to_resolve)

        with self.assertRaises(gaierror, msg='An exception should be raised when invoking get_hostname_by_addr with success_required set to True for an address that cannot resolve.'):
            host = get_hostname_by_addr(addr_that_fails_to_resolve, success_required=True)

        host = get_hostname_by_addr(addr_that_fails_to_resolve, success_required=False)
        self.assertIsNone(host, 'An null host should be returned when invoking get_hostname_by_addr with success_required set to False for an address that cannot resolve.')
