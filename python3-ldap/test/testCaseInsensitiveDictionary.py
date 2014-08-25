"""
Created on 2014.01.12

@author: Giovanni Cannata

Copyright 2014 Giovanni Cannata

This file is part of python3-ldap.

python3-ldap is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

python3-ldap is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with python3-ldap in the COPYING and COPYING.LESSER files.
If not, see <http://www.gnu.org/licenses/>.
"""

import unittest
from ldap3.utils.caseInsensitiveDictionary import CaseInsensitiveDict


class Test(unittest.TestCase):
    def test_create_empty_case_insensitive_dict(self):
        cid = CaseInsensitiveDict()
        self.assertTrue(isinstance(cid, CaseInsensitiveDict))

    def test_create_case_insensitive_dict_from_dict(self):
        dic = dict()
        dic['ONE'] = 1
        dic['TWO'] = 2
        dic[3] = 3
        cid = CaseInsensitiveDict(dic)
        self.assertEqual(cid['ONE'], 1)
        self.assertEqual(cid['one'], 1)
        self.assertEqual(cid['TWO'], 2)
        self.assertEqual(cid['two'], 2)
        self.assertEqual(cid[3], 3)

    def test_create_case_insensitive_dict_from_parameters(self):
        cid = CaseInsensitiveDict(one=1, two=2)
        self.assertEqual(cid['ONE'], 1)
        self.assertEqual(cid['one'], 1)
        self.assertEqual(cid['TWO'], 2)
        self.assertEqual(cid['two'], 2)

    def test_add_values_to_case_insentitive_dict(self):
        cid = CaseInsensitiveDict()
        cid['oNe'] = 1
        cid['tWo'] = 2
        cid[3] = 3
        self.assertEqual(cid['ONE'], 1)
        self.assertEqual(cid['one'], 1)
        self.assertEqual(cid['TWO'], 2)
        self.assertEqual(cid['two'], 2)
        self.assertEqual(cid[3], 3)

    def test_modify_value_in_case_insentitive_dict_invariant_key(self):
        cid = CaseInsensitiveDict()
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

    def test_modify_value_in_case_insentitive_dict_same_case_key(self):
        cid = CaseInsensitiveDict()
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

    def test_modify_value_in_case_insentitive_dict_different_case_key(self):
        cid = CaseInsensitiveDict()
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

    def test_delete_item_in_case_insentitive_dict_invariant_key(self):
        cid = CaseInsensitiveDict()
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
        except:
            self.assertTrue(False)

    def test_delete_item_in_case_insentitive_dict_same_case_key(self):
        cid = CaseInsensitiveDict()
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
        except:
            self.assertTrue(False)

        try:
            cid['ONE']
        except KeyError:
            self.assertTrue(True)
        except:
            self.assertTrue(False)

    def test_delete_item_in_case_insentitive_dict_different_case_key(self):
        cid = CaseInsensitiveDict()
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
        except:
            self.assertTrue(False)

        try:
            cid['ONE']
        except KeyError:
            self.assertTrue(True)
        except:
            self.assertTrue(False)

    def test_len_empty_case_insensitive_dict(self):
        cid = CaseInsensitiveDict()
        self.assertEqual(len(cid), 0)

    def test_len_case_insentitive_dict(self):
        cid = CaseInsensitiveDict()
        cid['oNe'] = 1
        cid['tWo'] = 2
        cid[3] = 3
        self.assertEqual(len(cid), 3)
        cid['ONE'] = 'ONE'
        self.assertEqual(len(cid), 3)

    def test_case_insensitive_dict_contains_invariant_key(self):
        cid = CaseInsensitiveDict()
        cid['oNe'] = 1
        cid['tWo'] = 2
        cid[3] = 3
        self.assertTrue(3 in cid)
        self.assertFalse('THREE' in cid)
        self.assertFalse(4 in cid)

    def test_case_insensitive_dict_contains_same_case_key(self):
        cid = CaseInsensitiveDict()
        cid['oNe'] = 1
        cid['tWo'] = 2
        cid[3] = 3
        self.assertTrue('oNe' in cid)
        self.assertFalse('THREE' in cid)
        self.assertFalse(4 in cid)

    def test_case_insensitive_dict_contains_different_case_key(self):
        cid = CaseInsensitiveDict()
        cid['oNe'] = 1
        cid['tWo'] = 2
        cid[3] = 3
        self.assertTrue('ONE' in cid)
        self.assertFalse('THREE' in cid)
        self.assertFalse(4 in cid)

    def test_copy_case_insensitive_dict(self):
        cid = CaseInsensitiveDict()
        cid['oNe'] = 1
        cid['tWo'] = 2
        cid[3] = 3

        cid2 = cid.copy()
        self.assertEqual(cid2['ONE'], 1)
        self.assertEqual(cid2['one'], 1)
        self.assertEqual(cid2['TWO'], 2)
        self.assertEqual(cid2['two'], 2)
        self.assertEqual(cid2[3], 3)

    def test_equality_case_insensitive_dict_with_same_case(self):
        cid = CaseInsensitiveDict()
        cid['one'] = 1
        cid['two'] = 2
        cid[3] = 3

        cid2 = CaseInsensitiveDict()
        cid2['one'] = 1
        cid2['two'] = 2
        cid2[3] = 3

        self.assertTrue(cid == cid2)

    def test_equality_case_insensitive_dict_with_different_case(self):
        cid = CaseInsensitiveDict()
        cid['one'] = 1
        cid['two'] = 2
        cid[3] = 3

        cid2 = CaseInsensitiveDict()
        cid2['ONE'] = 1
        cid2['TWO'] = 2
        cid2[3] = 3

        self.assertTrue(cid == cid2)

    def test_equality_case_insensitive_dict_with_same_case_dict(self):
        cid = CaseInsensitiveDict()
        cid['one'] = 1
        cid['two'] = 2
        cid[3] = 3

        dic = dict()
        dic['one'] = 1
        dic['two'] = 2
        dic[3] = 3

        self.assertTrue(cid == dic)


    def test_equality_case_insensitive_dict_with_different_case_dict(self):
        cid = CaseInsensitiveDict()
        cid['one'] = 1
        cid['two'] = 2
        cid[3] = 3

        dic = dict()
        dic['ONE'] = 1
        dic['TWO'] = 2
        dic[3] = 3

        self.assertTrue(cid == dic)

    def test_preserve_key_case_case_insensitive_dict(self):
        cid = CaseInsensitiveDict()
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