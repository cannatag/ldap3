"""A shared Server exposes a complete schema while another connection refreshes it."""

import copy
import unittest
from threading import Event, Thread
from unittest.mock import Mock, patch

from ldap3 import Server, SchemaInfo, DsaInfo
from ldap3.protocol.formatters.standard import format_attribute_values


ATTRIBUTES = {'attributeTypes': ["( 1.2.3 NAME 'counter' SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 SINGLE-VALUE )"]}


class Test(unittest.TestCase):
    def check_refresh(self, sync=True, thread_safe=False, pause_formatter=False):
        server = Server('dummy')
        old_schema = SchemaInfo('cn=schema', copy.deepcopy(ATTRIBUTES), {})
        server.attach_schema_info(old_schema)
        server.attach_dsa_info(DsaInfo({'subschemaSubentry': ['cn=schema']}, {}))
        attributes = copy.deepcopy(ATTRIBUTES)
        attributes['counter'] = [b'42']
        response = [{'attributes': attributes, 'raw_attributes': {'counter': [b'42']}}]
        connection = Mock()
        connection.strategy.no_real_dsa = False
        connection.strategy.pooled = False
        connection.strategy.sync = sync
        connection.strategy.thread_safe = thread_safe
        connection.result = {'result': 0}
        connection.response = response
        connection.search.return_value = (True, connection.result, response, None) if thread_safe else 1
        connection.get_response.return_value = (response, connection.result)
        started = Event()
        resume = Event()
        errors = []

        def pause():
            started.set()
            if not resume.wait(5):
                raise AssertionError('refresh was not resumed')

        def build(*args):
            if not pause_formatter:
                pause()
            return SchemaInfo(*args)

        def formatter(value):
            if pause_formatter:
                pause()
            return int(value)

        server.custom_formatter = {'counter': formatter}

        def refresh():
            try:
                server._get_schema_info(connection)
            except Exception as error:
                errors.append(error)

        with patch('ldap3.core.server.SchemaInfo', side_effect=build):
            worker = Thread(target=refresh)
            worker.start()
            try:
                self.assertTrue(started.wait(5), 'refresh did not start')
                self.assertIs(server.schema, old_schema)
                self.assertEqual(format_attribute_values(server.schema, 'counter', [b'7'], None), 7)
            finally:
                resume.set()
                worker.join(5)
            self.assertFalse(worker.is_alive(), 'refresh did not finish')
            self.assertEqual(errors, [])
        self.assertIsNot(server.schema, old_schema)
        self.assertEqual(server.schema.other['counter'], 42)

    def test_sync_schema_construction(self):
        self.check_refresh()

    def test_async_schema_construction(self):
        self.check_refresh(sync=False)

    def test_thread_safe_schema_construction(self):
        self.check_refresh(thread_safe=True)

    def test_sync_schema_formatting(self):
        self.check_refresh(pause_formatter=True)

    def test_async_schema_formatting(self):
        self.check_refresh(sync=False, pause_formatter=True)

    def test_thread_safe_schema_formatting(self):
        self.check_refresh(thread_safe=True, pause_formatter=True)
