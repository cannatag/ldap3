import unittest
from datetime import datetime
from uuid import UUID

from ldap3.protocol.formatters.validators import validate_integer, validate_boolean, validate_bytes, validate_generic_single_value, validate_time, validate_zero_and_minus_one_and_positive_int, validate_uuid_le
from ldap3.core.timezone import OffsetTzInfo
from ldap3.utils.port_validators import check_port, check_port_and_port_list


from ldap3.protocol.convert import prepare_filter_for_sending


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

    def test_validate_minus_one_zero_greater_than_zero(self):
        validated = validate_zero_and_minus_one_and_positive_int(0)
        self.assertTrue(validated)
        validated = validate_zero_and_minus_one_and_positive_int(-1)
        self.assertTrue(validated)
        validated = validate_zero_and_minus_one_and_positive_int(1)
        self.assertTrue(validated)
        validated = validate_zero_and_minus_one_and_positive_int(2)
        self.assertTrue(validated)
        validated = validate_zero_and_minus_one_and_positive_int(-2)
        self.assertFalse(validated)
        validated = validate_zero_and_minus_one_and_positive_int('0')
        self.assertTrue(validated)
        validated = validate_zero_and_minus_one_and_positive_int('-1')
        self.assertTrue(validated)
        validated = validate_zero_and_minus_one_and_positive_int('1')
        self.assertTrue(validated)
        validated = validate_zero_and_minus_one_and_positive_int('2')
        self.assertTrue(validated)
        validated = validate_zero_and_minus_one_and_positive_int('-2')
        self.assertFalse(validated)
        validated = validate_zero_and_minus_one_and_positive_int([0])
        self.assertTrue(validated)
        validated = validate_zero_and_minus_one_and_positive_int([-1])
        self.assertTrue(validated)
        validated = validate_zero_and_minus_one_and_positive_int([1])
        self.assertTrue(validated)
        validated = validate_zero_and_minus_one_and_positive_int([2])
        self.assertTrue(validated)
        validated = validate_zero_and_minus_one_and_positive_int([-2])
        self.assertFalse(validated)
        validated = validate_zero_and_minus_one_and_positive_int(['0'])
        self.assertTrue(validated)
        validated = validate_zero_and_minus_one_and_positive_int(['-1'])
        self.assertTrue(validated)
        validated = validate_zero_and_minus_one_and_positive_int(['1'])
        self.assertTrue(validated)
        validated = validate_zero_and_minus_one_and_positive_int(['2'])
        self.assertTrue(validated)
        validated = validate_zero_and_minus_one_and_positive_int('-2')
        self.assertFalse(validated)


    def test_check_port(self):
        assert check_port("0") == 'Source port must be an integer'
        assert check_port(0) is None
        assert check_port(65535) is None
        assert check_port(-1) == 'Source port must in range from 0 to 65535'
        assert check_port(65536) == 'Source port must in range from 0 to 65535'

    def test_check_port_and_port_list(self):
        assert check_port_and_port_list("0", None) == 'Source port must be an integer'
        assert check_port_and_port_list(0, None) is None
        assert check_port_and_port_list(65535, None) is None
        assert check_port_and_port_list(-1, None) == 'Source port must in range from 0 to 65535'
        assert check_port_and_port_list(65536, None) == 'Source port must in range from 0 to 65535'

    def test_validate_uuid_le_no_5C(self):
        uuid_str = '86f66df5-9b0e-4f7d-a6ef-1b897469dcaa'
        validated = validate_uuid_le(uuid_str)
        self.assertEqual(validated, UUID(hex=uuid_str).bytes_le)

        uuid_str = '{86f66df5-9b0e-4f7d-a6ef-1b897469dcaa}'
        validated = validate_uuid_le(uuid_str)
        self.assertEqual(validated, UUID(hex=uuid_str).bytes_le)

        uuid_str = '86f66df5-9b0e-4f7d-a6ef-1b897469dcaa'
        validated = validate_uuid_le("\\f5\\6d\\f6\\86\\0e\\9b\\7d\\4f\\a6\\ef\\1b\\89\\74\\69\\dc\\aa")
        self.assertEqual(validated, UUID(hex=uuid_str).bytes_le)

    def test_validate_uuid_le_5C_no_valid_hex(self):
        # Issue #894
        uuid_str = '1f3e2261-b35c-4065-98e3-3c243f695446'
        validated = validate_uuid_le(uuid_str)
        self.assertEqual(validated, UUID(hex=uuid_str).bytes_le)

    def test_validate_uuid_le_5C_valid_hex(self):
        # Issue #1000, but 0x4143 -> AD -> happens to be a valid hex number
        uuid_str = 'db6ffb06-5c7e-4341-a899-7eda79866582'
        validated = validate_uuid_le(uuid_str)
        self.assertEqual(validated, UUID(hex=uuid_str).bytes_le)

    def test_validate_uuid_le_5C_valid_hex_prepared(self):
        # Issue #1000, prepare_filter_for_sending applied
        uuid_str = 'db6ffb06-5c7e-4341-a899-7eda79866582'
        validated = prepare_filter_for_sending(validate_uuid_le(uuid_str))
        self.assertEqual(validated, UUID(hex=uuid_str).bytes_le)

    def test_validate_uuid_le_5C_outofrange_hex_prepared(self):
        # Issue #1000, but 0x2D43 -> -C -> happens to be a invalid (negative) hex number
        uuid_str = 'db6ffb06-5c7e-432d-a899-7eda79866582'
        validated = prepare_filter_for_sending(validate_uuid_le(uuid_str))
        self.assertEqual(validated, UUID(hex=uuid_str).bytes_le)
