"""
"""

# Created on 2017.01.15
#
# Author: Giovanni Cannata
#
# Copyright 2017 - 2020 Giovanni Cannata
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

from ldap3.utils.ciDict import CaseInsensitiveWithAliasDict


class Test(unittest.TestCase):
    # these tests are the same for CaseInsensitiveDict
    def test_create_empty(self):
        cid = CaseInsensitiveWithAliasDict()
        self.assertTrue(isinstance(cid, CaseInsensitiveWithAliasDict))

    def test_create_from_dict(self):
        dic = dict()
        dic['ONE'] = 1
        dic['TWO'] = 2
        dic[3] = 3
        cid = CaseInsensitiveWithAliasDict(dic)
        self.assertEqual(cid['ONE'], 1)
        self.assertEqual(cid['one'], 1)
        self.assertEqual(cid['TWO'], 2)
        self.assertEqual(cid['two'], 2)
        self.assertEqual(cid[3], 3)

    def test_create_from_parameters(self):
        cid = CaseInsensitiveWithAliasDict(one=1, two=2)
        self.assertEqual(cid['ONE'], 1)
        self.assertEqual(cid['one'], 1)
        self.assertEqual(cid['TWO'], 2)
        self.assertEqual(cid['two'], 2)

    def test_add_values(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe'] = 1
        cid['tWo'] = 2
        cid[3] = 3
        self.assertEqual(cid['ONE'], 1)
        self.assertEqual(cid['one'], 1)
        self.assertEqual(cid['TWO'], 2)
        self.assertEqual(cid['two'], 2)
        self.assertEqual(cid[3], 3)

    def test_modify_value_immutable_key(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe'] = 1
        cid['tWo'] = 2
        cid[3] = 3
        self.assertEqual(cid[3], 3)
        cid[3] = 'Three'
        self.assertEqual(cid['ONE'], 1)
        self.assertEqual(cid['oNe'], 1)
        self.assertEqual(cid['TWO'], 2)
        self.assertEqual(cid['tWo'], 2)
        self.assertEqual(cid[3], 'Three')

    def test_modify_value_same_case_key(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe'] = 1
        cid['tWo'] = 2
        cid[3] = 3
        self.assertEqual(cid['ONE'], 1)
        self.assertEqual(cid['oNe'], 1)
        cid['oNe'] = 'ONE'
        self.assertEqual(cid['ONE'], 'ONE')
        self.assertEqual(cid['oNe'], 'ONE')
        self.assertEqual(cid['TWO'], 2)
        self.assertEqual(cid['two'], 2)
        self.assertEqual(cid[3], 3)

    def test_modify_value_different_case_key(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe'] = 1
        cid['tWo'] = 2
        cid[3] = 3
        self.assertEqual(cid['ONE'], 1)
        self.assertEqual(cid['oNe'], 1)
        cid['one'] = 'ONE'
        self.assertEqual(cid['ONE'], 'ONE')
        self.assertEqual(cid['oNe'], 'ONE')
        self.assertEqual(cid['TWO'], 2)
        self.assertEqual(cid['two'], 2)
        self.assertEqual(cid[3], 3)

    def test_delete_item_immutable_key(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe'] = 1
        cid['tWo'] = 2
        cid[3] = 3
        self.assertEqual(cid[3], 3)
        del cid[3]
        self.assertEqual(cid['ONE'], 1)
        self.assertEqual(cid['oNe'], 1)
        self.assertEqual(cid['TWO'], 2)
        self.assertEqual(cid['tWo'], 2)
        try:
            cid[3]
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)
        else:
            self.fail('key still present')
    def test_delete_item_same_case_key(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe'] = 1
        cid['tWo'] = 2
        cid[3] = 3
        self.assertEqual(cid['ONE'], 1)
        self.assertEqual(cid['oNe'], 1)
        del cid['oNe']
        self.assertEqual(cid['TWO'], 2)
        self.assertEqual(cid['two'], 2)
        self.assertEqual(cid[3], 3)

        try:
            cid['oNe']
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)
        else:
            self.fail('key still present')
        try:
            cid['ONE']
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)
        else:
            self.fail('key still present')

    def test_delete_item_different_case_key(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe'] = 1
        cid['tWo'] = 2
        cid[3] = 3
        self.assertEqual(cid['ONE'], 1)
        self.assertEqual(cid['oNe'], 1)
        del cid['one']
        self.assertEqual(cid['TWO'], 2)
        self.assertEqual(cid['two'], 2)
        self.assertEqual(cid[3], 3)
        try:
            cid['oNe']
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)
        else:
            self.fail('key still present')
        try:
            cid['ONE']
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)
        else:
            self.fail('key still present')

    def test_len_empty(self):
        cid = CaseInsensitiveWithAliasDict()
        self.assertEqual(len(cid), 0)

    def test_len(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe'] = 1
        cid['tWo'] = 2
        cid[3] = 3
        self.assertEqual(len(cid), 3)
        cid['ONE'] = 'ONE'
        self.assertEqual(len(cid), 3)

    def test_contains_immutable_key(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe'] = 1
        cid['tWo'] = 2
        cid[3] = 3
        self.assertTrue(3 in cid)
        self.assertFalse('THREE' in cid)
        self.assertFalse(4 in cid)

    def test_contains_same_case_key(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe'] = 1
        cid['tWo'] = 2
        cid[3] = 3
        self.assertTrue('oNe' in cid)
        self.assertFalse('THREE' in cid)
        self.assertFalse(4 in cid)

    def test_contains_different_case_key(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe'] = 1
        cid['tWo'] = 2
        cid[3] = 3
        self.assertTrue('ONE' in cid)
        self.assertFalse('THREE' in cid)
        self.assertFalse(4 in cid)

    def test_copy(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe'] = 1
        cid['tWo'] = 2
        cid[3] = 3

        cid2 = cid.copy()
        self.assertEqual(cid2['ONE'], 1)
        self.assertEqual(cid2['one'], 1)
        self.assertEqual(cid2['TWO'], 2)
        self.assertEqual(cid2['two'], 2)
        self.assertEqual(cid2[3], 3)

    def test_equality_with_same_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['one'] = 1
        cid['two'] = 2
        cid[3] = 3

        cid2 = CaseInsensitiveWithAliasDict()
        cid2['one'] = 1
        cid2['two'] = 2
        cid2[3] = 3

        self.assertEqual(cid, cid2)

    def test_equality_with_different_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['one'] = 1
        cid['two'] = 2
        cid[3] = 3

        cid2 = CaseInsensitiveWithAliasDict()
        cid2['ONE'] = 1
        cid2['TWO'] = 2
        cid2[3] = 3

        self.assertEqual(cid, cid2)

    def test_equality_with_same_case_dict(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['one'] = 1
        cid['two'] = 2
        cid[3] = 3

        dic = dict()
        dic['one'] = 1
        dic['two'] = 2
        dic[3] = 3

        self.assertEqual(cid, dic)

    def test_equality_with_different_case_dict(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['one'] = 1
        cid['two'] = 2
        cid[3] = 3

        dic = dict()
        dic['ONE'] = 1
        dic['TWO'] = 2
        dic[3] = 3

        self.assertEqual(cid, dic)

    def test_preserve_key_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['One'] = 1
        cid['Two'] = 2
        cid[3] = 3
        key_list = list(cid.keys())
        self.assertTrue('One' in key_list)
        self.assertTrue('Two' in key_list)
        self.assertTrue(3 in key_list)
        self.assertFalse('ONE' in key_list)
        self.assertFalse('one' in key_list)
        self.assertFalse('TWO' in key_list)
        self.assertFalse('TWO' in key_list)
        self.assertFalse(4 in key_list)

    # These tests are the same tests adapted to CaseInsensitiveWithAliasDict
    
    def test_add_values(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe', 'oNe-A'] = 1
        cid['tWo'] = 2
        cid[3] = 3
        self.assertEqual(cid['ONE'], 1)
        self.assertEqual(cid['one'], 1)
        self.assertEqual(cid['TWO'], 2)
        self.assertEqual(cid['two'], 2)
        self.assertEqual(cid[3], 3)
        self.assertEqual(cid['one-a'], 1)
        self.assertEqual(cid['oNe-A'], 1)

    def test_modify_value_in_immutable_key(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe'] = 1
        cid['tWo'] = 2
        cid[3, 4] = 3
        self.assertEqual(cid[3], 3)
        cid[3] = 'Three'
        self.assertEqual(cid['ONE'], 1)
        self.assertEqual(cid['oNe'], 1)
        self.assertEqual(cid['TWO'], 2)
        self.assertEqual(cid['tWo'], 2)
        self.assertEqual(cid[3], 'Three')
        self.assertEqual(cid[4], 'Three')

    def test_modify_value_in_same_case_key(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe', 'oNe-A'] = 1
        cid['tWo'] = 2
        cid[3] = 3
        self.assertEqual(cid['ONE'], 1)
        self.assertEqual(cid['oNe'], 1)
        self.assertEqual(cid['ONE-A'], 1)

        cid['oNe'] = 'ONE'
        self.assertEqual(cid['ONE'], 'ONE')
        self.assertEqual(cid['oNe'], 'ONE')
        self.assertEqual(cid['TWO'], 2)
        self.assertEqual(cid['two'], 2)
        self.assertEqual(cid[3], 3)
        self.assertEqual(cid['ONE-A'], 'ONE')

    def test_modify_value_in_different_case_key(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe', 'oNe-A'] = 1
        cid['tWo'] = 2
        cid[3] = 3
        self.assertEqual(cid['ONE'], 1)
        self.assertEqual(cid['oNe'], 1)
        self.assertEqual(cid['ONE-A'], 1)
        cid['one'] = 'ONE'
        self.assertEqual(cid['ONE'], 'ONE')
        self.assertEqual(cid['oNe'], 'ONE')
        self.assertEqual(cid['TWO'], 2)
        self.assertEqual(cid['two'], 2)
        self.assertEqual(cid[3], 3)
        self.assertEqual(cid['ONE-A'], 'ONE')

    def test_delete_item_in_immutable_key(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe'] = 1
        cid['tWo'] = 2
        cid[3, 4] = 3
        self.assertEqual(cid[3], 3)
        del cid[3]
        self.assertEqual(cid['ONE'], 1)
        self.assertEqual(cid['oNe'], 1)
        self.assertEqual(cid['TWO'], 2)
        self.assertEqual(cid['tWo'], 2)
        try:
            cid[3]
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)
        else:
            self.fail('key still present')
        try:
            cid[4]
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)
        else:
            self.fail('key still present')

    def test_delete_item_in_same_case_key(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe', 'oNe-A'] = 1
        cid['tWo'] = 2
        cid[3] = 3
        self.assertEqual(cid['ONE'], 1)
        self.assertEqual(cid['oNe'], 1)
        self.assertEqual(cid['ONE-a'], 1)
        self.assertEqual(cid['oNe-a'], 1)
        del cid['oNe']
        self.assertEqual(cid['TWO'], 2)
        self.assertEqual(cid['two'], 2)
        self.assertEqual(cid[3], 3)

        try:
            cid['oNe']
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.fail()
        else:
            self.fail('key still present')
        try:
            cid['ONE']
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)
        else:
            self.fail('key still present')
        try:
            cid['oNe-A']
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)
        else:
            self.fail('key still present')
        try:
            cid['ONE-A']
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)
        else:
            self.fail('key still present')

    def test_delete_item_in_different_case_key(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe', 'oNe-A'] = 1
        cid['tWo'] = 2
        cid[3] = 3
        self.assertEqual(cid['ONE'], 1)
        self.assertEqual(cid['oNe'], 1)
        self.assertEqual(cid['ONE-a'], 1)
        self.assertEqual(cid['oNe-a'], 1)
        del cid['one']
        self.assertEqual(cid['TWO'], 2)
        self.assertEqual(cid['two'], 2)
        self.assertEqual(cid[3], 3)
        try:
            cid['oNe']
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)
        else:
            self.fail('key still present')
        try:
            cid['ONE']
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)
        else:
            self.fail('key still present')
        try:
            cid['oNe-a']
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)
        else:
            self.fail('key still present')
        try:
            cid['ONE-a']
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)
        else:
            self.fail('key still present')
    def test_len(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe', 'oNe-A'] = 1
        cid['tWo'] = 2
        cid[3] = 3
        self.assertEqual(len(cid), 3)
        cid['ONE-A'] = 'ONE'
        self.assertEqual(cid['ONE'], 'ONE')
        self.assertEqual(len(cid), 3)

    def test_contains_immutable_key(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe'] = 1
        cid['tWo'] = 2
        cid[3, 4] = 3
        self.assertTrue(3 in cid)
        self.assertTrue(4 in cid)
        self.assertFalse('THREE' in cid)
        self.assertFalse(5 in cid)

    def test_contains_same_case_key(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe', 'oNe-a'] = 1
        cid['tWo'] = 2
        cid[3] = 3
        self.assertTrue('oNe' in cid)
        self.assertTrue('oNe-a' in cid)
        self.assertFalse('THREE' in cid)
        self.assertFalse(4 in cid)

    def test_contains_different_case_key(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe', 'oNe-a'] = 1
        cid['tWo'] = 2
        cid[3] = 3
        self.assertTrue('ONE' in cid)
        self.assertTrue('ONE-A' in cid)
        self.assertFalse('THREE' in cid)
        self.assertFalse(4 in cid)

    def test_copy(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe', 'oNe-A'] = 1
        cid['tWo'] = 2
        cid[3, 4] = 3

        cid2 = cid.copy()
        self.assertEqual(cid2['ONE'], 1)
        self.assertEqual(cid2['one'], 1)
        self.assertEqual(cid2['TWO'], 2)
        self.assertEqual(cid2['two'], 2)
        self.assertEqual(cid2[3], 3)
        self.assertEqual(cid2['oNe-A'], 1)
        self.assertEqual(cid2['ONE-A'], 1)
        self.assertEqual(cid2[4], 3)

    def test_equality_with_same_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['one', 'oNe-A'] = 1
        cid['two'] = 2
        cid[3] = 3

        cid2 = CaseInsensitiveWithAliasDict()
        cid2['one'] = 1
        cid2['two'] = 2
        cid2[3, 4] = 3

        self.assertEqual(cid, cid2)

    def test_equality_with_different_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['one', 'oNe-A'] = 1
        cid['two'] = 2
        cid[3] = 3

        cid2 = CaseInsensitiveWithAliasDict()
        cid2['ONE', 'ONE-A'] = 1
        cid2['TWO'] = 2
        cid2[3] = 3

        self.assertEqual(cid, cid2)

    def test_equality_with_same_case_dict(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['one', 'oNe-A'] = 1
        cid['two'] = 2
        cid[3] = 3

        dic = dict()
        dic['one'] = 1
        dic['two'] = 2
        dic[3] = 3

        self.assertEqual(cid, dic)

    def test_equality_with_different_case_dict(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['one', 'oNe-A'] = 1
        cid['two'] = 2
        cid[3] = 3

        dic = dict()
        dic['ONE'] = 1
        dic['TWO'] = 2
        dic[3] = 3

        self.assertEqual(cid, dic)

    def test_preserve_key_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['One', 'oNe-A'] = 1
        cid['Two'] = 2
        cid[3] = 3
        key_list = list(cid.keys())
        self.assertTrue('One' in key_list)
        self.assertTrue('Two' in key_list)
        self.assertTrue(3 in key_list)
        self.assertFalse('ONE' in key_list)
        self.assertFalse('one' in key_list)
        self.assertFalse('TWO' in key_list)
        self.assertFalse('TWO' in key_list)
        self.assertFalse(4 in key_list)
        self.assertFalse('oNe-A' in key_list)

    # These are specific tests for CaseInsensitiveWithAliasDict

    def test_add_alias_to_key_same_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe'] = 1
        cid['tWo'] = 2
        cid.set_alias('oNe', 'oNe-A')
        self.assertEqual(len(cid), 2)
        self.assertEqual(cid['oNe'], 1)
        self.assertEqual(cid['oNe-A'], 1)
        self.assertEqual(cid['tWo'], 2)

    def test_add_alias_to_key_different_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe'] = 1
        cid['tWo'] = 2
        cid.set_alias('ONE', 'oNe-A')
        self.assertEqual(len(cid), 2)
        self.assertEqual(cid['oNe'], 1)
        self.assertEqual(cid['oNe-A'], 1)
        self.assertEqual(cid['tWo'], 2)

    def test_implicit_add_multiple_aliases_to_same_key(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe', 'oNe-A', 'oNe-B'] = 1
        cid['tWo'] = 2
        self.assertEqual(len(cid), 2)
        self.assertEqual(cid['oNe'], 1)
        self.assertEqual(cid['oNe-A'], 1)
        self.assertEqual(cid['oNe-B'], 1)
        self.assertEqual(cid['tWo'], 2)

    def test_explicit_add_multiple_aliases_to_same_key_same_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe'] = 1
        cid['tWo'] = 2
        cid.set_alias('oNe', 'oNe-A')
        cid.set_alias('oNe', 'oNe-B')
        self.assertEqual(len(cid), 2)
        self.assertEqual(cid['oNe'], 1)
        self.assertEqual(cid['oNe-A'], 1)
        self.assertEqual(cid['oNe-B'], 1)
        self.assertEqual(cid['tWo'], 2)

    def test_explicit_add_multiple_aliases_to_same_key_different_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe'] = 1
        cid['tWo'] = 2
        cid.set_alias('ONE', 'oNe-A')
        cid.set_alias('ONE', 'oNe-B')
        self.assertEqual(len(cid), 2)
        self.assertEqual(cid['oNe'], 1)
        self.assertEqual(cid['oNe-A'], 1)
        self.assertEqual(cid['oNe-B'], 1)
        self.assertEqual(cid['tWo'], 2)

    def test_implicit_add_multiple_aliases_to_different_key(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe', 'oNe-A', 'oNe-B'] = 1
        cid['tWo', 'tWo-A', 'tWo-B'] = 2
        self.assertEqual(len(cid), 2)
        self.assertEqual(cid['oNe'], 1)
        self.assertEqual(cid['oNe-A'], 1)
        self.assertEqual(cid['oNe-B'], 1)
        self.assertEqual(cid['tWo'], 2)
        self.assertEqual(cid['tWo-A'], 2)
        self.assertEqual(cid['tWo-B'], 2)

    def test_explicit_add_multiple_aliases_to_different_key_same_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe'] = 1
        cid['tWo'] = 2
        cid.set_alias('oNe', 'oNe-A')
        cid.set_alias('oNe', 'oNe-B')
        cid.set_alias('tWo', 'tWo-A')
        cid.set_alias('tWo', 'tWo-B')
        self.assertEqual(len(cid), 2)
        self.assertEqual(cid['oNe'], 1)
        self.assertEqual(cid['oNe-A'], 1)
        self.assertEqual(cid['oNe-B'], 1)
        self.assertEqual(cid['tWo-A'], 2)
        self.assertEqual(cid['tWo-B'], 2)
        self.assertEqual(cid['tWo'], 2)

    def test_explicit_add_multiple_alias_to_different_key_different_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe'] = 1
        cid['tWo'] = 2
        cid.set_alias('ONE', 'oNe-A')
        cid.set_alias('ONE', 'oNe-B')
        cid.set_alias('TWO', 'tWo-A')
        cid.set_alias('TWO', 'tWo-B')
        self.assertEqual(len(cid), 2)
        self.assertEqual(cid['oNe'], 1)
        self.assertEqual(cid['oNe-A'], 1)
        self.assertEqual(cid['oNe-B'], 1)
        self.assertEqual(cid['tWo-A'], 2)
        self.assertEqual(cid['tWo-B'], 2)
        self.assertEqual(cid['tWo'], 2)

    def test_explicit_single_add_multiple_aliases_to_same_key_same_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe'] = 1
        cid['tWo'] = 2
        cid.set_alias('oNe', ['oNe-A', 'oNe-B'])
        cid.set_alias('tWo', ['tWo-A', 'tWo-B'])
        self.assertEqual(len(cid), 2)
        self.assertEqual(cid['oNe'], 1)
        self.assertEqual(cid['oNe-A'], 1)
        self.assertEqual(cid['oNe-B'], 1)
        self.assertEqual(cid['tWo-A'], 2)
        self.assertEqual(cid['tWo-B'], 2)
        self.assertEqual(cid['tWo'], 2)

    def test_explicit_add_multiple_aliases_to_same_key_different_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe'] = 1
        cid['tWo'] = 2
        cid.set_alias('ONE', ['oNe-A', 'oNe-B'])
        cid.set_alias('TWO', ['tWo-A', 'tWo-B'])
        self.assertEqual(len(cid), 2)
        self.assertEqual(cid['oNe'], 1)
        self.assertEqual(cid['oNe-A'], 1)
        self.assertEqual(cid['oNe-B'], 1)
        self.assertEqual(cid['tWo-A'], 2)
        self.assertEqual(cid['tWo-B'], 2)
        self.assertEqual(cid['tWo'], 2)

    def test_modify_value_by_key_same_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe', 'oNe-A', 'oNe-B'] = 1
        cid['tWo'] = 2
        cid['oNe'] = 3
        self.assertEqual(len(cid), 2)
        self.assertEqual(cid['oNe'], 3)
        self.assertEqual(cid['oNe-A'], 3)
        self.assertEqual(cid['oNe-B'], 3)

    def test_modify_value_by_key_different_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe', 'oNe-A', 'oNe-B'] = 1
        cid['tWo'] = 2
        cid['ONE'] = 3
        self.assertEqual(len(cid), 2)
        self.assertEqual(cid['oNe'], 3)
        self.assertEqual(cid['oNe-A'], 3)
        self.assertEqual(cid['oNe-B'], 3)

    def test_modify_value_by_alias_same_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe', 'oNe-A', 'oNe-B'] = 1
        cid['tWo'] = 2
        cid['oNe-B'] = 3
        self.assertEqual(len(cid), 2)
        self.assertEqual(cid['oNe'], 3)
        self.assertEqual(cid['oNe-A'], 3)
        self.assertEqual(cid['oNe-B'], 3)

    def test_modify_value_by_alias_different_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe', 'oNe-A', 'oNe-B'] = 1
        cid['tWo'] = 2
        cid['ONE-A'] = 3
        self.assertEqual(len(cid), 2)
        self.assertEqual(cid['oNe'], 3)
        self.assertEqual(cid['oNe-A'], 3)
        self.assertEqual(cid['oNe-B'], 3)

    def test_delete_key_same_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe', 'oNe-A', 'oNe-B'] = 1
        cid['tWo'] = 2
        self.assertEqual(len(cid), 2)
        del cid['oNe']
        self.assertEqual(len(cid), 1)
        try:
            cid['oNe']
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)
        else:
            self.fail('key still present')
        try:
            cid['oNe-A']
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)
        else:
            self.fail('key still present')
        try:
            cid['oNe-B']
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)
        else:
            self.fail('key still present')
        self.assertEqual(cid._store, dict(tWo=2))
        self.assertEqual(cid._aliases, dict())
        self.assertEqual(cid._alias_keymap, dict())

    def test_delete_key_different_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe', 'oNe-A', 'oNe-B'] = 1
        cid['tWo'] = 2
        self.assertEqual(len(cid), 2)
        del cid['ONE']
        self.assertEqual(len(cid), 1)
        try:
            cid['oNe']
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)
        else:
            self.fail('key still present')
        try:
            cid['oNe-A']
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)
        else:
            self.fail('key still present')
        try:
            cid['oNe-B']
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)
        else:
            self.fail('key still present')
        self.assertEqual(cid._store, dict(tWo=2))
        self.assertEqual(cid._aliases, dict())
        self.assertEqual(cid._alias_keymap, dict())

    def test_delete_alias_same_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe', 'oNe-A', 'oNe-B'] = 1
        cid['tWo'] = 2
        self.assertEqual(len(cid), 2)
        del cid['oNe-A']
        self.assertEqual(len(cid), 2)
        self.assertEqual(cid['oNe'], 1)
        self.assertEqual(cid['oNe-B'], 1)
        try:
            cid['oNe-A']
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)
        else:
            self.fail('key still present')
        self.assertEqual(cid._store, {'oNe': 1, 'tWo': 2})
        self.assertEqual(cid._aliases, {'one-b': 'one'})
        self.assertEqual(cid._alias_keymap, {'one': ['one-b']})

    def test_delete_alias_different_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe', 'oNe-A', 'oNe-B'] = 1
        cid['tWo'] = 2
        self.assertEqual(len(cid), 2)
        del cid['ONE-A']
        self.assertEqual(len(cid), 2)
        self.assertEqual(cid['oNe'], 1)
        self.assertEqual(cid['oNe-B'], 1)
        try:
            cid['oNe-A']
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)
        else:
            self.fail('key still present')
        self.assertEqual(cid._store, {'oNe': 1, 'tWo': 2})
        self.assertEqual(cid._aliases, {'one-b': 'one'})
        self.assertEqual(cid._alias_keymap, {'one': ['one-b']})

    def test_explicit_remove_alias_same_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe', 'oNe-A', 'oNe-B'] = 1
        cid['tWo'] = 2
        self.assertEqual(len(cid), 2)
        cid.remove_alias('oNe-A')
        self.assertEqual(len(cid), 2)
        self.assertEqual(cid['oNe'], 1)
        self.assertEqual(cid['oNe-B'], 1)
        try:
            cid['oNe-A']
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)
        else:
            self.fail('key still present')
        self.assertEqual(cid._store, {'oNe': 1, 'tWo': 2})
        self.assertEqual(cid._aliases, {'one-b': 'one'})
        self.assertEqual(cid._alias_keymap, {'one': ['one-b']})

    def test_explicit_remove_alias_same_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe', 'oNe-A', 'oNe-B'] = 1
        cid['tWo'] = 2
        self.assertEqual(len(cid), 2)
        cid.remove_alias('oNe-A')
        self.assertEqual(len(cid), 2)
        self.assertEqual(cid['oNe'], 1)
        self.assertEqual(cid['oNe-B'], 1)
        try:
            cid['oNe-A']
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)
        else:
            self.fail('key still present')
        self.assertEqual(cid._store, {'oNe': 1, 'tWo': 2})
        self.assertEqual(cid._aliases, {'one-b': 'one'})
        self.assertEqual(cid._alias_keymap, {'one': ['one-b']})

    def test_explicit_remove_alias_different_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe', 'oNe-A', 'oNe-B'] = 1
        cid['tWo'] = 2
        self.assertEqual(len(cid), 2)
        cid.remove_alias('ONE-A')
        self.assertEqual(len(cid), 2)
        self.assertEqual(cid['oNe'], 1)
        self.assertEqual(cid['oNe-B'], 1)
        try:
            cid['oNe-A']
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)
        else:
            self.fail('key still present')
        self.assertEqual(cid._store, {'oNe': 1, 'tWo': 2})
        self.assertEqual(cid._aliases, {'one-b': 'one'})
        self.assertEqual(cid._alias_keymap, {'one': ['one-b']})

    def test_explicit_single_remove_aliases_same_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe', 'oNe-A', 'oNe-B'] = 1
        cid['tWo'] = 2
        self.assertEqual(len(cid), 2)
        cid.remove_alias(['oNe-A', 'oNe-B'])
        self.assertEqual(len(cid), 2)
        self.assertEqual(cid['oNe'], 1)
        try:
            cid['oNe-A']
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)
        else:
            self.fail('key still present')
        try:
            cid['oNe-B']
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)
        else:
            self.fail('key still present')

        self.assertEqual(cid._store, {'oNe': 1, 'tWo': 2})
        self.assertEqual(cid._aliases, {})
        self.assertEqual(cid._alias_keymap, {})

    def test_explicit_single_remove_aliases_different_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe', 'oNe-A', 'oNe-B'] = 1
        cid['tWo'] = 2
        self.assertEqual(len(cid), 2)
        cid.remove_alias(['ONE-A', 'ONE-B'])
        self.assertEqual(len(cid), 2)
        self.assertEqual(cid['oNe'], 1)
        try:
            cid['oNe-A']
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)
        try:
            cid['oNe-B']
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)

        self.assertEqual(cid._store, {'oNe': 1, 'tWo': 2})
        self.assertEqual(cid._aliases, {})
        self.assertEqual(cid._alias_keymap, {})

    def test_add_same_alias_twice_to_same_key_same_case(self):
        cid = CaseInsensitiveWithAliasDict()
        try:
            cid['oNe', 'oNe-A', 'oNe-A'] = 1
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.fail('wrong exception')

        self.assertEqual(cid._store, {'oNe': 1})
        self.assertEqual(cid._aliases, {'one-a': 'one'})
        self.assertEqual(cid._alias_keymap, {'one': ['one-a']})

    def test_add_same_alias_twice_to_same_key_different_case(self):
        cid = CaseInsensitiveWithAliasDict()
        try:
            cid['oNe', 'oNe-A', 'ONE-A'] = 1
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.fail('wrong exception')

        self.assertEqual(cid._store, {'oNe': 1})
        self.assertEqual(cid._aliases, {'one-a': 'one'})
        self.assertEqual(cid._alias_keymap, {'one': ['one-a']})

    def test_explicit_add_same_alias_twice_to_same_key_same_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe'] = 1
        try:
            cid.set_alias('oNe', ['oNe-A', 'oNe-A'])
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.fail('wrong exception')

        self.assertEqual(cid._store, {'oNe': 1})
        self.assertEqual(cid._aliases, {'one-a': 'one'})
        self.assertEqual(cid._alias_keymap, {'one': ['one-a']})

    def test_explicit_add_same_alias_twice_to_same_key_different_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe'] = 1
        try:
            cid.set_alias('ONE', ['oNe-A', 'ONE-A'])
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.fail('wrong exception')

        self.assertEqual(cid._store, {'oNe': 1})
        self.assertEqual(cid._aliases, {'one-a': 'one'})
        self.assertEqual(cid._alias_keymap, {'one': ['one-a']})

    def test_add_same_alias_to_different_key_same_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe', 'oNe-A'] = 1
        try:
            cid['tWo', 'oNe-A'] = 2
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.fail('wrong exception')
        else:
            self.fail('double alias')
        self.assertEqual(cid._store, {'oNe': 1, 'tWo': 2})
        self.assertEqual(cid._aliases, {'one-a': 'one'})
        self.assertEqual(cid._alias_keymap, {'one': ['one-a']})

    def test_add_same_alias_to_different_key_different_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe', 'oNe-A'] = 1
        try:
            cid['tWo', 'ONE-A'] = 2
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.fail('wrong exception')
        else:
            self.fail('double alias')
        self.assertEqual(cid._store, {'oNe': 1, 'tWo': 2})
        self.assertEqual(cid._aliases, {'one-a': 'one'})
        self.assertEqual(cid._alias_keymap, {'one': ['one-a']})

    def test_explicit_add_same_alias_to_different_key_same_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe', 'oNe-A'] = 1
        cid['tWo'] = 2
        try:
            cid.set_alias('tWo', 'oNe-A')
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.fail('wrong exception')
        else:
            self.fail('double alias')
        self.assertEqual(cid._store, {'oNe': 1, 'tWo': 2})
        self.assertEqual(cid._aliases, {'one-a': 'one'})
        self.assertEqual(cid._alias_keymap, {'one': ['one-a']})

    def test_explicit_add_same_alias_to_different_key_different_case(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe', 'oNe-A'] = 1
        cid['tWo'] = 2
        try:
            cid.set_alias('TWO', 'ONE-A')
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.fail('wrong exception')
        else:
            self.fail('double alias')
        self.assertEqual(cid._store, {'oNe': 1, 'tWo': 2})
        self.assertEqual(cid._aliases, {'one-a': 'one'})
        self.assertEqual(cid._alias_keymap, {'one': ['one-a']})

    def test_explicit_add_alias_to_unexistent_key(self):
        cid = CaseInsensitiveWithAliasDict()
        cid['oNe', 'oNe-A'] = 1
        cid['tWo'] = 2
        try:
            cid.set_alias('THREE', 'THREE-A')
        except KeyError:
            self.assertTrue(True)
        except Exception:
            self.fail('wrong exception')
        else:
            # self.fail('double alias')
            pass
        self.assertEqual(cid._store, {'oNe': 1, 'tWo': 2})
        self.assertEqual(cid._aliases, {'one-a': 'one'})
        self.assertEqual(cid._alias_keymap, {'one': ['one-a']})
