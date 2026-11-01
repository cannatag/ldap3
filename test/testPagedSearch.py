"""Paged search must stop when a server reports sizeLimitExceeded."""

import unittest
from unittest.mock import Mock

from ldap3.core.results import RESULT_SIZE_LIMIT_EXCEEDED, RESULT_SUCCESS
from ldap3.extend.standard.PagedSearch import paged_search_generator, paged_search_accumulator


class Test(unittest.TestCase):
    def connection(self, sync=True, thread_safe=False, raise_exceptions=False):
        connection = Mock()
        connection.check_names = False
        connection.auto_referrals = True
        connection.raise_exceptions = raise_exceptions
        connection.strategy.sync = sync
        connection.strategy.thread_safe = thread_safe
        return connection

    def page(self, connection, entries, result_code, cookie):
        result = {'result': result_code, 'referrals': None,
                  'description': 'sizeLimitExceeded' if result_code else 'success',
                  'dn': '', 'message': '', 'type': 'searchResDone',
                  'controls': {'1.2.840.113556.1.4.319': {'value': {'cookie': cookie}}}}
        response = [{'type': 'searchResEntry', 'dn': entry} for entry in entries]
        connection.result = result
        connection.response = response
        connection.get_response.return_value = (response, result)
        return (False, result, response, None) if connection.strategy.thread_safe else 1

    def check_size_limit(self, sync=True, thread_safe=False, accumulator=False):
        connection = self.connection(sync, thread_safe)

        def search(*args):
            self.assertEqual(connection.search.call_count, 1, 'requested another page after sizeLimitExceeded')
            return self.page(connection, ['cn=one', 'cn=two'], RESULT_SIZE_LIMIT_EXCEEDED, b'more')

        connection.search.side_effect = search
        search_function = paged_search_accumulator if accumulator else paged_search_generator
        response = list(search_function(connection, 'o=lab', '(cn=*)', size_limit=2))
        self.assertEqual({entry['dn'] for entry in response}, {'cn=one', 'cn=two'})
        self.assertEqual(connection.search.call_count, 1)
        self.assertTrue(connection.auto_referrals)

    def test_size_limit_with_cookie_sync(self):
        self.check_size_limit()

    def test_size_limit_with_cookie_async(self):
        self.check_size_limit(sync=False)

    def test_size_limit_with_cookie_thread_safe(self):
        self.check_size_limit(thread_safe=True)

    def test_size_limit_accumulator(self):
        self.check_size_limit(accumulator=True)

    def test_success_with_cookie_requests_next_page(self):
        connection = self.connection()

        def search(*args):
            if connection.search.call_count == 1:
                return self.page(connection, ['cn=one'], RESULT_SUCCESS, b'more')
            self.assertEqual(args[-1], b'more')
            return self.page(connection, ['cn=two'], RESULT_SUCCESS, b'')

        connection.search.side_effect = search
        response = list(paged_search_generator(connection, 'o=lab', '(cn=*)'))
        self.assertEqual([entry['dn'] for entry in response], ['cn=one', 'cn=two'])
        self.assertEqual(connection.search.call_count, 2)

    def test_size_limit_with_raise_exceptions_returns_partial_entries(self):
        connection = self.connection(raise_exceptions=True)
        connection.search.side_effect = lambda *args: self.page(
            connection, ['cn=one'], RESULT_SIZE_LIMIT_EXCEEDED, b'more')
        responses = paged_search_generator(connection, 'o=lab', '(cn=*)')
        self.assertEqual(next(responses)['dn'], 'cn=one')
        with self.assertRaises(StopIteration):
            next(responses)
        self.assertEqual(connection.search.call_count, 1)
