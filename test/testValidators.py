import unittest
from datetime import datetime

from ldap3.protocol.formatters.validators import validate_integer, validate_boolean, validate_bytes, validate_generic_single_value, validate_time
from ldap3.core.timezone import OffsetTzInfo

class Test(unittest.TestCase):
    def test_int_validator_valid_number(self):
        validated = validate_integer(1)
        self.assertTrue(validated)

    def test_int_validator_invalid_number(self):
        validated = validate_integer(1.2)
        self.assertFalse(validated)

    def test_int_validator_valid_number_sequence(self):
        validated = validate_integer([1, 2, 3])
        self.assertTrue(validated)

    def test_int_validator_invalid_number_sequence(self):
        validated = validate_integer([1, 1.2, 3])
        self.assertFalse(validated)

    def test_int_validator_valid_string_number(self):
        validated = validate_integer('1')
        self.assertEqual(validated, 1)

    def test_int_validator_invalid_string_number(self):
        validated = validate_integer('1.2')
        self.assertFalse(validated)

    def test_int_validator_valid_string_number_sequence(self):
        validated = validate_integer(['1', '2', '3'])
        self.assertEqual(validated, [1, 2, 3])

    def test_int_validator_invalid_string_number_sequence(self):
        validated = validate_integer(['1', '1.2', '3'])
        self.assertFalse(validated)

    def test_int_validator_invalid_type_1(self):
        validated = validate_integer(True)
        self.assertFalse(validated)

    def test_int_validator_invalid_type_2(self):
        validated = validate_integer(False)
        self.assertFalse(validated)

    def test_int_validator_invalid_type_3(self):
        validated = validate_integer(Ellipsis)
        self.assertFalse(validated)

    def test_int_validator_invalid_type_4(self):
        validated = validate_integer(object)
        self.assertFalse(validated)

    def test_boolean_validator_valid_bool_true(self):
        validated = validate_boolean(True)
        self.assertEqual(validated, 'TRUE')

    def test_boolean_validator_valid_bool_false(self):
        validated = validate_boolean(False)
        self.assertEqual(validated, 'FALSE')

    def test_boolean_validator_valid_str_true_1(self):
        validated = validate_boolean('True')
        self.assertEqual(validated, 'TRUE')

    def test_boolean_validator_valid_str_false_1(self):
        validated = validate_boolean('False')
        self.assertEqual(validated, 'FALSE')

    def test_boolean_validator_valid_str_true_2(self):
        validated = validate_boolean('TrUe')
        self.assertEqual(validated, 'TRUE')

    def test_boolean_validator_valid_str_false_2(self):
        validated = validate_boolean('FaLsE')
        self.assertEqual(validated, 'FALSE')

    def test_boolean_validator_invalid_int_1(self):
        validated = validate_boolean(0)
        self.assertFalse(validated)

    def test_boolean_validator_invalid_int_2(self):
        validated = validate_boolean(1)
        self.assertFalse(validated)

    def test_boolean_validator_invalid_str_1(self):
        validated = validate_boolean('')
        self.assertFalse(validated)

    def test_boolean_validator_invalid_str_2(self):
        validated = validate_boolean('abc')
        self.assertFalse(validated)

    def test_bytes_validator_valid_bytes(self):
        validated = validate_bytes(bytes([1, 2, 3]))
        self.assertTrue(validated)

    def test_bytes_validator_invalid_str(self):
        if str is bytes:  # Python 2
            validated = validate_bytes(unicode('abc'))
        else:
            validated = validate_bytes('abc')

        self.assertFalse(validated)

    def test_bytes_validator_invalid_object(self):
        validated = validate_bytes(object)
        self.assertFalse(validated)

    def test_validate_generic_single_value_valid_1(self):
        validated = validate_generic_single_value(1)
        self.assertTrue(validated)

    def test_validate_generic_single_value_valid_2(self):
        validated = validate_generic_single_value('abc')
        self.assertTrue(validated)

    def test_validate_generic_single_value_valid_3(self):
        validated = validate_generic_single_value(object)
        self.assertTrue(validated)

    def test_validate_generic_single_value_invalid_1(self):
        validated = validate_generic_single_value((1, 2))
        self.assertFalse(validated)

    def test_validate_generic_single_value_invalid_2(self):
        validated = validate_generic_single_value([1, 2])
        self.assertFalse(validated)

    def test_validate_generic_single_value_invalid_3(self):
        validated = validate_generic_single_value((a for a in range(2)))
        self.assertFalse(validated)

    def test_validate_time_valid_datetime(self):
        validated = validate_time(datetime.now())
        self.assertTrue(validated)

    def test_validate_time_valid_datetime_with_timezone(self):
        validated = validate_time(datetime.now(OffsetTzInfo(0, 'UTC')))
        self.assertTrue(validated)

    def test_validate_time_valid_str(self):
        validated = validate_time('20170317094232Z')
        self.assertTrue(validated)

    def test_validate_time_valid_str_with_timezone(self):
        validated = validate_time('20170317094232+0100')
        self.assertTrue(validated)

    def test_validate_time_invalid_str_1(self):
        validated = validate_time('abc')
        self.assertFalse(validated)

    def test_validate_time_invalid_str_2(self):
        validated = validate_time('20170317254201Z')
        self.assertFalse(validated)

    def test_validate_time_invalid_str_with_timezone(self):
        validated = validate_time('20170317094232+24')
        self.assertFalse(validated)
