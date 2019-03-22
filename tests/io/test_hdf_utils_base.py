# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 15:07:16 2017

@author: Suhas Somnath
"""
from __future__ import division, print_function, unicode_literals, absolute_import
import unittest
import os
import sys
import h5py
import numpy as np
import socket

sys.path.append("../../pyUSID/")
from pyUSID.io import hdf_utils, io_utils
from pyUSID import __version__
from platform import platform

from . import data_utils


if sys.version_info.major == 3:
    unicode = str


class TestHDFUtilsBase(unittest.TestCase):

    def setUp(self):
        data_utils.make_beps_file()

    def tearDown(self):
        data_utils.delete_existing_file(data_utils.std_beps_path)

    def test_get_attr_illegal_01(self):
        with self.assertRaises(TypeError):
            hdf_utils.get_attr(np.arange(3), 'units')

    def test_get_attr_illegal_02(self):
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            with self.assertRaises(TypeError):
                hdf_utils.get_attr(h5_f['/Raw_Measurement/source_main'], 14)

    def test_get_attr_illegal_03(self):
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            with self.assertRaises(TypeError):
                hdf_utils.get_attr(h5_f['/Raw_Measurement/source_main'], ['quantity', 'units'])

    def test_get_attr_illegal_04(self):
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            with self.assertRaises(KeyError):
                hdf_utils.get_attr(h5_f['/Raw_Measurement/source_main'], 'non_existent')

    def test_get_attr_legal_01(self):
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            returned = hdf_utils.get_attr(h5_f['/Raw_Measurement/source_main'], 'units')
            self.assertEqual(returned, 'A')

    def test_get_attr_legal_02(self):
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            returned = hdf_utils.get_attr(h5_f['/Raw_Measurement/Position_Indices'], 'labels')
            self.assertTrue(np.all(returned == ['X', 'Y']))

    def test_get_attr_legal_03(self):
        attrs = {'att_1': 'string_val', 'att_2': 1.2345,
                 'att_3': [1, 2, 3, 4], 'att_4': ['str_1', 'str_2', 'str_3']}
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            h5_group = h5_f['/Raw_Measurement/source_main-Fitter_000']
            for key, expected_value in attrs.items():
                self.assertTrue(np.all(hdf_utils.get_attr(h5_group, key) == expected_value))

    def test_get_attributes_01(self):
        attrs = {'att_1': 'string_val', 'att_2': 1.2345,
                 'att_3': [1, 2, 3, 4], 'att_4': ['str_1', 'str_2', 'str_3']}
        sub_attrs = ['att_1', 'att_4', 'att_3']
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            h5_group = h5_f['/Raw_Measurement/source_main-Fitter_000']
            returned_attrs = hdf_utils.get_attributes(h5_group, sub_attrs)
            self.assertIsInstance(returned_attrs, dict)
            for key in sub_attrs:
                self.assertTrue(np.all(returned_attrs[key] == attrs[key]))

    def test_get_attributes_all(self):
        attrs = {'att_1': 'string_val', 'att_2': 1.2345,
                 'att_3': [1, 2, 3, 4], 'att_4': ['str_1', 'str_2', 'str_3']}
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            h5_group = h5_f['/Raw_Measurement/source_main-Fitter_000']
            returned_attrs = hdf_utils.get_attributes(h5_group)
            self.assertIsInstance(returned_attrs, dict)
            for key in attrs.keys():
                self.assertTrue(np.all(returned_attrs[key] == attrs[key]))

    def test_get_attributes_illegal(self):
        sub_attrs = ['att_1', 'att_4', 'does_not_exist']
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            h5_group = h5_f['/Raw_Measurement/source_main-Fitter_000']
            with self.assertRaises(KeyError):
                _ = hdf_utils.get_attributes(h5_group, sub_attrs)

    def test_get_auxillary_datasets_single(self):
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            h5_main = h5_f['/Raw_Measurement/source_main']
            h5_pos = h5_f['/Raw_Measurement/Position_Indices']
            [ret_val] = hdf_utils.get_auxiliary_datasets(h5_main, aux_dset_name='Position_Indices')
            self.assertEqual(ret_val, h5_pos)

    def test_get_auxillary_datasets_single(self):
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            h5_main = h5_f['/Raw_Measurement/source_main']
            h5_pos = h5_f['/Raw_Measurement/Position_Indices']
            [ret_val] = hdf_utils.get_auxiliary_datasets(h5_main, aux_dset_name='Position_Indices')
            self.assertEqual(ret_val, h5_pos)

    def test_get_auxillary_datasets_multiple(self):
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            h5_main = h5_f['/Raw_Measurement/source_main']
            h5_pos_inds = h5_f['/Raw_Measurement/Position_Indices']
            h5_pos_vals = h5_f['/Raw_Measurement/Position_Values']
            ret_val = hdf_utils.get_auxiliary_datasets(h5_main, aux_dset_name=['Position_Indices',
                                                                               'Position_Values'])
            self.assertEqual(set(ret_val), set([h5_pos_inds, h5_pos_vals]))

    def test_get_auxillary_datasets_all(self):
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            h5_main = h5_f['/Raw_Measurement/source_main']
            expected = [h5_f['/Raw_Measurement/Position_Indices'],
                        h5_f['/Raw_Measurement/Position_Values'],
                        h5_f['/Raw_Measurement/Spectroscopic_Indices'],
                        h5_f['/Raw_Measurement/Spectroscopic_Values']]
            ret_val = hdf_utils.get_auxiliary_datasets(h5_main)
            self.assertEqual(set(expected), set(ret_val))

    def test_get_auxillary_datasets_illegal(self):
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            h5_main = h5_f['/Raw_Measurement/source_main']
            with self.assertRaises(KeyError):
                _ = hdf_utils.get_auxiliary_datasets(h5_main, aux_dset_name='Does_Not_Exist')

    def test_get_h5_obj_refs_legal_01(self):
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            h5_obj_refs = [h5_f,
                              4.123,
                              np.arange(6),
                              h5_f['/Raw_Measurement/Position_Indices'],
                              h5_f['/Raw_Measurement/source_main-Fitter_000'],
                              h5_f['/Raw_Measurement/source_main-Fitter_000/Spectroscopic_Indices'],
                              h5_f['/Raw_Measurement/Spectroscopic_Values']]
            chosen_objs = [h5_f['/Raw_Measurement/Position_Indices'],
                              h5_f['/Raw_Measurement/source_main-Fitter_000'],
                              h5_f['/Raw_Measurement/source_main-Fitter_000/Spectroscopic_Indices']]

            target_ref_names = ['Position_Indices', 'source_main-Fitter_000', 'Spectroscopic_Indices']

            returned_h5_objs = hdf_utils.get_h5_obj_refs(target_ref_names, h5_obj_refs)

            self.assertEqual(set(chosen_objs), set(returned_h5_objs))

    def test_get_h5_obj_refs_same_name(self):
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            h5_obj_refs = [h5_f['/Raw_Measurement/source_main-Fitter_001/Spectroscopic_Indices'],
                           h5_f['/Raw_Measurement/source_main-Fitter_000/Spectroscopic_Indices'],
                           h5_f['/Raw_Measurement/Spectroscopic_Values']]
            expected_objs = [h5_f['/Raw_Measurement/source_main-Fitter_001/Spectroscopic_Indices'],
                             h5_f['/Raw_Measurement/source_main-Fitter_000/Spectroscopic_Indices']]

            target_ref_names = ['Spectroscopic_Indices']

            returned_h5_objs = hdf_utils.get_h5_obj_refs(target_ref_names, h5_obj_refs)

            self.assertEqual(set(expected_objs), set(returned_h5_objs))

    def test_find_dataset_legal(self):
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            h5_group = h5_f['/Raw_Measurement/']
            expected_dsets = [h5_f['/Raw_Measurement/Spectroscopic_Indices'],
                              h5_f['/Raw_Measurement/source_main-Fitter_000/Spectroscopic_Indices'],
                              h5_f['/Raw_Measurement/source_main-Fitter_001/Spectroscopic_Indices']]
            ret_val = hdf_utils.find_dataset(h5_group, 'Spectroscopic_Indices')
            self.assertEqual(set(ret_val), set(expected_dsets))

    def test_find_dataset_illegal(self):
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            h5_group = h5_f['/Raw_Measurement/']
            ret_val = hdf_utils.find_dataset(h5_group, 'Does_Not_Exist')
            self.assertEqual(len(ret_val), 0)

    def test_find_results_groups_legal(self):
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            h5_main = h5_f['/Raw_Measurement/source_main']
            expected_groups = [h5_f['/Raw_Measurement/source_main-Fitter_000'],
                               h5_f['/Raw_Measurement/source_main-Fitter_001']]
            ret_val = hdf_utils.find_results_groups(h5_main, 'Fitter')
            self.assertEqual(set(ret_val), set(expected_groups))

    def test_find_results_groups_illegal(self):
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            h5_main = h5_f['/Raw_Measurement/source_main']
            ret_val = hdf_utils.find_results_groups(h5_main, 'Blah')
            self.assertEqual(len(ret_val), 0)

    def test_check_for_matching_attrs_dset_no_attrs(self):
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            h5_main = h5_f['/Raw_Measurement/source_main']
            self.assertTrue(hdf_utils.check_for_matching_attrs(h5_main, new_parms=None))

    def test_check_for_matching_attrs_dset_matching_attrs(self):
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            h5_main = h5_f['/Raw_Measurement/source_main']
            attrs = {'units': 'A', 'quantity':'Current'}
            self.assertTrue(hdf_utils.check_for_matching_attrs(h5_main, new_parms=attrs))

    def test_check_for_matching_attrs_dset_one_mismatched_attrs(self):
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            h5_main = h5_f['/Raw_Measurement/source_main']
            attrs = {'units': 'A', 'blah': 'meh'}
            self.assertFalse(hdf_utils.check_for_matching_attrs(h5_main, new_parms=attrs))

    def test_check_for_matching_attrs_grp(self):
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            h5_main = h5_f['/Raw_Measurement/source_main-Fitter_000']
            attrs = {'att_1': 'string_val', 'att_2': 1.2345,
                     'att_3': [1, 2, 3, 4], 'att_4': ['str_1', 'str_2', 'str_3']}
            self.assertTrue(hdf_utils.check_for_matching_attrs(h5_main, new_parms=attrs))

    def test_check_for_matching_attrs_grp_mismatched_types_01(self):
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            h5_main = h5_f['/Raw_Measurement/source_main-Fitter_000']
            attrs = {'att_4': 'string_val'}
            self.assertFalse(hdf_utils.check_for_matching_attrs(h5_main, new_parms=attrs))

    def test_check_for_matching_attrs_grp_mismatched_types_02(self):
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            h5_main = h5_f['/Raw_Measurement/source_main-Fitter_000']
            attrs = {'att_1': ['str_1', 'str_2', 'str_3']}
            self.assertFalse(hdf_utils.check_for_matching_attrs(h5_main, new_parms=attrs))

    def test_check_for_matching_attrs_grp_mismatched_types_03(self):
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            h5_main = h5_f['/Raw_Measurement/source_main-Fitter_000']
            attrs = {'att_4': [1, 4.234, 'str_3']}
            self.assertFalse(hdf_utils.check_for_matching_attrs(h5_main, new_parms=attrs))

    def test_check_for_matching_attrs_grp_mismatched_types_04(self):
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            h5_main = h5_f['/Raw_Measurement/source_main-Fitter_000']
            attrs = {'att_4': [1, 4.234, 45]}
            self.assertFalse(hdf_utils.check_for_matching_attrs(h5_main, new_parms=attrs))

    def test_check_for_old_exact_match(self):
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            h5_main = h5_f['/Raw_Measurement/source_main']
            attrs = {'att_1': 'string_val', 'att_2': 1.2345,
                     'att_3': [1, 2, 3, 4], 'att_4': ['str_1', 'str_2', 'str_3']}
            [h5_ret_grp] = hdf_utils.check_for_old(h5_main, 'Fitter', new_parms=attrs, target_dset=None)
            self.assertEqual(h5_ret_grp, h5_f['/Raw_Measurement/source_main-Fitter_000'])

    def test_check_for_old_subset_but_match(self):
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            h5_main = h5_f['/Raw_Measurement/source_main']
            attrs = {'att_2': 1.2345,
                     'att_3': [1, 2, 3, 4], 'att_4': ['str_1', 'str_2', 'str_3']}
            [h5_ret_grp] = hdf_utils.check_for_old(h5_main, 'Fitter', new_parms=attrs, target_dset=None)
            self.assertEqual(h5_ret_grp, h5_f['/Raw_Measurement/source_main-Fitter_000'])

    def test_check_for_old_exact_match_02(self):
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            h5_main = h5_f['/Raw_Measurement/source_main']
            attrs = {'att_1': 'other_string_val', 'att_2': 5.4321,
                     'att_3': [4, 1, 3], 'att_4': ['s', 'str_2', 'str_3']}
            [h5_ret_grp] = hdf_utils.check_for_old(h5_main, 'Fitter', new_parms=attrs, target_dset=None)
            self.assertEqual(h5_ret_grp, h5_f['/Raw_Measurement/source_main-Fitter_001'])

    def test_check_for_old_fail_01(self):
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            h5_main = h5_f['/Raw_Measurement/source_main']
            attrs = {'att_1': [4, 1, 3], 'att_2': ['s', 'str_2', 'str_3'],
                     'att_3': 'other_string_val', 'att_4': 5.4321}
            ret_val = hdf_utils.check_for_old(h5_main, 'Fitter', new_parms=attrs, target_dset=None)
            self.assertIsInstance(ret_val, list)
            self.assertEqual(len(ret_val), 0)

    def test_check_for_old_fail_02(self):
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            h5_main = h5_f['/Raw_Measurement/source_main']
            attrs = {'att_x': [4, 1, 3], 'att_z': ['s', 'str_2', 'str_3'],
                     'att_y': 'other_string_val', 'att_4': 5.4321}
            ret_val = hdf_utils.check_for_old(h5_main, 'Fitter', new_parms=attrs, target_dset=None)
            self.assertIsInstance(ret_val, list)
            self.assertEqual(len(ret_val), 0)

    def test_create_index_group_first_group(self):
        file_path = 'test.h5'
        data_utils.delete_existing_file(file_path)
        with h5py.File(file_path) as h5_f:
            h5_group = hdf_utils.create_indexed_group(h5_f, 'Hello')
            self.assertIsInstance(h5_group, h5py.Group)
            self.assertEqual(h5_group.name, '/Hello_000')
            self.assertEqual(h5_group.parent, h5_f)
            self.__verify_book_keeping_attrs(h5_group)

            h5_sub_group = hdf_utils.create_indexed_group(h5_group, 'Test')
            self.assertIsInstance(h5_sub_group, h5py.Group)
            self.assertEqual(h5_sub_group.name, '/Hello_000/Test_000')
            self.assertEqual(h5_sub_group.parent, h5_group)
            self.__verify_book_keeping_attrs(h5_sub_group)
        os.remove(file_path)

    def test_create_index_group_second(self):
        file_path = 'test.h5'
        data_utils.delete_existing_file(file_path)
        with h5py.File(file_path) as h5_f:
            h5_group_1 = hdf_utils.create_indexed_group(h5_f, 'Hello')
            self.assertIsInstance(h5_group_1, h5py.Group)
            self.assertEqual(h5_group_1.name, '/Hello_000')
            self.assertEqual(h5_group_1.parent, h5_f)
            self.__verify_book_keeping_attrs(h5_group_1)

            h5_group_2 = hdf_utils.create_indexed_group(h5_f, 'Hello')
            self.assertIsInstance(h5_group_2, h5py.Group)
            self.assertEqual(h5_group_2.name, '/Hello_001')
            self.assertEqual(h5_group_2.parent, h5_f)
            self.__verify_book_keeping_attrs(h5_group_2)
        os.remove(file_path)

    def test_create_index_group_w_suffix_(self):
        file_path = 'test.h5'
        data_utils.delete_existing_file(file_path)
        with h5py.File(file_path) as h5_f:
            h5_group = hdf_utils.create_indexed_group(h5_f, 'Hello_')
            self.assertIsInstance(h5_group, h5py.Group)
            self.assertEqual(h5_group.name, '/Hello_000')
            self.assertEqual(h5_group.parent, h5_f)
            self.__verify_book_keeping_attrs(h5_group)
        os.remove(file_path)

    def test_create_index_group_empty_base_name(self):
        file_path = 'test.h5'
        data_utils.delete_existing_file(file_path)
        with h5py.File(file_path) as h5_f:
            with self.assertRaises(ValueError):
                _ = hdf_utils.create_indexed_group(h5_f, '    ')

        os.remove(file_path)

    def test_create_results_group_first(self):
        file_path = 'test.h5'
        data_utils.delete_existing_file(file_path)
        with h5py.File(file_path) as h5_f:
            h5_dset = h5_f.create_dataset('Main', data=[1, 2, 3])
            h5_group = hdf_utils.create_results_group(h5_dset, 'Tool')
            self.assertIsInstance(h5_group, h5py.Group)
            self.assertEqual(h5_group.name, '/Main-Tool_000')
            self.assertEqual(h5_group.parent, h5_f)
            self.__verify_book_keeping_attrs(h5_group)

            h5_dset = h5_group.create_dataset('Main_Dataset', data=[1, 2, 3])
            h5_sub_group = hdf_utils.create_results_group(h5_dset, 'SHO_Fit')
            self.assertIsInstance(h5_sub_group, h5py.Group)
            self.assertEqual(h5_sub_group.name, '/Main-Tool_000/Main_Dataset-SHO_Fit_000')
            self.assertEqual(h5_sub_group.parent, h5_group)
            self.__verify_book_keeping_attrs(h5_sub_group)
        os.remove(file_path)

    def test_create_results_group_second(self):
        file_path = 'test.h5'
        data_utils.delete_existing_file(file_path)
        with h5py.File(file_path) as h5_f:
            h5_dset = h5_f.create_dataset('Main', data=[1, 2, 3])
            h5_group = hdf_utils.create_results_group(h5_dset, 'Tool')
            self.assertIsInstance(h5_group, h5py.Group)
            self.assertEqual(h5_group.name, '/Main-Tool_000')
            self.assertEqual(h5_group.parent, h5_f)
            self.__verify_book_keeping_attrs(h5_group)

            h5_sub_group = hdf_utils.create_results_group(h5_dset, 'Tool')
            self.assertIsInstance(h5_sub_group, h5py.Group)
            self.assertEqual(h5_sub_group.name, '/Main-Tool_001')
            self.assertEqual(h5_sub_group.parent, h5_f)
            self.__verify_book_keeping_attrs(h5_sub_group)
        os.remove(file_path)

    def test_create_results_group_empty_tool_name(self):
        file_path = 'test.h5'
        data_utils.delete_existing_file(file_path)
        with h5py.File(file_path) as h5_f:
            h5_dset = h5_f.create_dataset('Main', data=[1, 2, 3])
            with self.assertRaises(ValueError):
                _ = hdf_utils.create_results_group(h5_dset, '   ')
        os.remove(file_path)

    def test_create_results_group_not_dataset(self):
        file_path = 'test.h5'
        data_utils.delete_existing_file(file_path)
        with h5py.File(file_path) as h5_f:
            with self.assertRaises(TypeError):
                _ = hdf_utils.create_results_group(h5_f, 'Tool')

        os.remove(file_path)

    def test_assign_group_index_existing(self):
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            h5_group = h5_f['/Raw_Measurement']
            ret_val = hdf_utils.assign_group_index(h5_group, 'source_main-Fitter')
            self.assertEqual(ret_val, 'source_main-Fitter_002')

    def test_assign_group_index_new(self):
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            h5_group = h5_f['/Raw_Measurement']
            ret_val = hdf_utils.assign_group_index(h5_group, 'blah_')
            self.assertEqual(ret_val, 'blah_000')

    def test_write_legal_atts_to_grp(self):
        file_path = 'test.h5'
        data_utils.delete_existing_file(file_path)
        with h5py.File(file_path) as h5_f:

            h5_group = h5_f.create_group('Blah')

            attrs = {'att_1': 'string_val', 'att_2': 1.234, 'att_3': [1, 2, 3.14, 4],
                     'att_4': ['s', 'tr', 'str_3']}

            hdf_utils.write_simple_attrs(h5_group, attrs)

            for key, expected_val in attrs.items():
                self.assertTrue(np.all(hdf_utils.get_attr(h5_group, key) == expected_val))

        os.remove(file_path)

    def test_write_legal_atts_to_dset_01(self):
        file_path = 'test.h5'
        data_utils.delete_existing_file(file_path)
        with h5py.File(file_path) as h5_f:

            h5_dset = h5_f.create_dataset('Test', data=np.arange(3))

            attrs = {'att_1': 'string_val',
                     'att_2': 1.2345,
                     'att_3': [1, 2, 3, 4],
                     'att_4': ['str_1', 'str_2', 'str_3']}

            hdf_utils.write_simple_attrs(h5_dset, attrs)

            self.assertEqual(len(h5_dset.attrs), len(attrs))

            for key, expected_val in attrs.items():
                self.assertTrue(np.all(hdf_utils.get_attr(h5_dset, key) == expected_val))

        os.remove(file_path)

    def test_is_editable_h5_read_only(self):
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            h5_group = h5_f['/Raw_Measurement']
            h5_main = h5_f['/Raw_Measurement/Ancillary']
            self.assertFalse(hdf_utils.is_editable_h5(h5_group))
            self.assertFalse(hdf_utils.is_editable_h5(h5_f))
            self.assertFalse(hdf_utils.is_editable_h5(h5_main))

    def test_is_editable_h5_r_plus(self):
        with h5py.File(data_utils.std_beps_path, mode='r+') as h5_f:
            h5_group = h5_f['/Raw_Measurement']
            h5_main = h5_f['/Raw_Measurement/Ancillary']
            self.assertTrue(hdf_utils.is_editable_h5(h5_group))
            self.assertTrue(hdf_utils.is_editable_h5(h5_f))
            self.assertTrue(hdf_utils.is_editable_h5(h5_main))

    def test_is_editable_h5_w(self):
        file_path = 'test.h5'
        data_utils.delete_existing_file(file_path)
        with h5py.File(file_path) as h5_f:
            h5_dset = h5_f.create_dataset('Test', data=np.arange(3))
            h5_group = h5_f.create_group('blah')
            self.assertTrue(hdf_utils.is_editable_h5(h5_group))
            self.assertTrue(hdf_utils.is_editable_h5(h5_f))
            self.assertTrue(hdf_utils.is_editable_h5(h5_dset))

        os.remove(file_path)

    def test_is_editable_h5_illegal(self):
        # wrong kind of object
        with self.assertRaises(TypeError):
            _ = hdf_utils.is_editable_h5(np.arange(4))

        # closed file
        with h5py.File(data_utils.std_beps_path, mode='r') as h5_f:
            h5_group = h5_f['/Raw_Measurement']

        with self.assertRaises(ValueError):
            _ = hdf_utils.is_editable_h5(h5_group)

    def test_link_h5_obj_as_alias(self):
        file_path = 'link_as_alias.h5'
        data_utils.delete_existing_file(file_path)
        with h5py.File(file_path) as h5_f:

            h5_main = h5_f.create_dataset('main', data=np.arange(5))
            h5_anc = h5_f.create_dataset('Ancillary', data=np.arange(3))
            h5_group = h5_f.create_group('Results')

            # Linking to dataset:
            hdf_utils.link_h5_obj_as_alias(h5_main, h5_anc, 'Blah')
            hdf_utils.link_h5_obj_as_alias(h5_main, h5_group, 'Something')
            self.assertEqual(h5_f[h5_main.attrs['Blah']], h5_anc)
            self.assertEqual(h5_f[h5_main.attrs['Something']], h5_group)

            # Linking ot Group:
            hdf_utils.link_h5_obj_as_alias(h5_group, h5_main, 'Center')
            hdf_utils.link_h5_obj_as_alias(h5_group, h5_anc, 'South')
            self.assertEqual(h5_f[h5_group.attrs['Center']], h5_main)
            self.assertEqual(h5_f[h5_group.attrs['South']], h5_anc)

            # Linking to file:
            hdf_utils.link_h5_obj_as_alias(h5_f, h5_main, 'Paris')
            hdf_utils.link_h5_obj_as_alias(h5_f, h5_group, 'France')
            self.assertEqual(h5_f[h5_f.attrs['Paris']], h5_main)
            self.assertEqual(h5_f[h5_f.attrs['France']], h5_group)

            # Non h5 object
            with self.assertRaises(TypeError):
                hdf_utils.link_h5_obj_as_alias(h5_group, np.arange(5), 'Center')

            # H5 reference but not the object
            with self.assertRaises(TypeError):
                hdf_utils.link_h5_obj_as_alias(h5_group, h5_f.attrs['Paris'], 'Center')

        os.remove(file_path)

    def test_link_h5_objects_as_attrs(self):
        file_path = 'link_h5_objects_as_attrs.h5'
        data_utils.delete_existing_file(file_path)
        with h5py.File(file_path) as h5_f:

            h5_main = h5_f.create_dataset('main', data=np.arange(5))
            h5_anc = h5_f.create_dataset('Ancillary', data=np.arange(3))
            h5_group = h5_f.create_group('Results')

            hdf_utils.link_h5_objects_as_attrs(h5_f, [h5_anc, h5_main, h5_group])
            for exp, name in zip([h5_main, h5_anc, h5_group], ['main', 'Ancillary', 'Results']):
                self.assertEqual(exp, h5_f[h5_f.attrs[name]])

            # Single object
            hdf_utils.link_h5_objects_as_attrs(h5_main, h5_anc)
            self.assertEqual(h5_f[h5_main.attrs['Ancillary']], h5_anc)

            # Linking to a group:
            hdf_utils.link_h5_objects_as_attrs(h5_group, [h5_anc, h5_main])
            for exp, name in zip([h5_main, h5_anc], ['main', 'Ancillary']):
                self.assertEqual(exp, h5_group[h5_group.attrs[name]])

            with self.assertRaises(TypeError):
                hdf_utils.link_h5_objects_as_attrs(h5_main, np.arange(4))

        os.remove(file_path)

    def __verify_book_keeping_attrs(self, h5_obj):
        time_stamp = io_utils.get_time_stamp()
        in_file = h5_obj.attrs['timestamp']
        self.assertEqual(time_stamp[:time_stamp.rindex('_')], in_file[:in_file.rindex('_')])
        self.assertEqual(__version__, h5_obj.attrs['pyUSID_version'])
        self.assertEqual(socket.getfqdn(), h5_obj.attrs['machine_id'])
        self.assertEqual(platform(), h5_obj.attrs['platform'])

    def test_write_book_keeping_attrs_file(self):
        file_path = 'test.h5'
        data_utils.delete_existing_file(file_path)
        with h5py.File(file_path) as h5_f:
            hdf_utils.write_book_keeping_attrs(h5_f)
            self.__verify_book_keeping_attrs(h5_f)
        os.remove(file_path)

    def test_write_book_keeping_attrs_group(self):
        file_path = 'test.h5'
        data_utils.delete_existing_file(file_path)
        with h5py.File(file_path) as h5_f:
            h5_g = h5_f.create_group('group')
            hdf_utils.write_book_keeping_attrs(h5_g)
            self.__verify_book_keeping_attrs(h5_g)
        os.remove(file_path)

    def test_write_book_keeping_attrs_dset(self):
        file_path = 'test.h5'
        data_utils.delete_existing_file(file_path)
        with h5py.File(file_path) as h5_f:
            h5_dset = h5_f.create_dataset('dset', data=[1, 2, 3])
            hdf_utils.write_book_keeping_attrs(h5_dset)
            self.__verify_book_keeping_attrs(h5_dset)
        os.remove(file_path)

    def test_write_book_keeping_attrs_invalid(self):
        with self.assertRaises(TypeError):
            hdf_utils.write_book_keeping_attrs(np.arange(4))

    def test_link_as_main(self):
        file_path = 'link_as_main.h5'
        data_utils.delete_existing_file(file_path)
        with h5py.File(file_path) as h5_f:
            h5_raw_grp = h5_f.create_group('Raw_Measurement')

            num_rows = 3
            num_cols = 5
            num_cycles = 2
            num_cycle_pts = 7

            source_dset_name = 'source_main'

            source_pos_data = np.vstack((np.tile(np.arange(num_cols), num_rows),
                                         np.repeat(np.arange(num_rows), num_cols))).T
            pos_attrs = {'units': ['nm', 'um'], 'labels': ['X', 'Y']}

            h5_pos_inds = h5_raw_grp.create_dataset('Position_Indices', data=source_pos_data, dtype=np.uint16)
            data_utils.write_aux_reg_ref(h5_pos_inds, pos_attrs['labels'], is_spec=False)
            data_utils.write_string_list_as_attr(h5_pos_inds, pos_attrs)

            h5_pos_vals = h5_raw_grp.create_dataset('Position_Values', data=source_pos_data, dtype=np.float32)
            data_utils.write_aux_reg_ref(h5_pos_vals, pos_attrs['labels'], is_spec=False)
            data_utils.write_string_list_as_attr(h5_pos_vals, pos_attrs)

            source_spec_data = np.vstack((np.tile(np.arange(num_cycle_pts), num_cycles),
                                          np.repeat(np.arange(num_cycles), num_cycle_pts)))
            source_spec_attrs = {'units': ['V', ''], 'labels': ['Bias', 'Cycle']}

            h5_source_spec_inds = h5_raw_grp.create_dataset('Spectroscopic_Indices', data=source_spec_data,
                                                            dtype=np.uint16)
            data_utils.write_aux_reg_ref(h5_source_spec_inds, source_spec_attrs['labels'], is_spec=True)
            data_utils.write_string_list_as_attr(h5_source_spec_inds, source_spec_attrs)

            h5_source_spec_vals = h5_raw_grp.create_dataset('Spectroscopic_Values', data=source_spec_data,
                                                            dtype=np.float32)
            data_utils.write_aux_reg_ref(h5_source_spec_vals, source_spec_attrs['labels'], is_spec=True)
            data_utils.write_string_list_as_attr(h5_source_spec_vals, source_spec_attrs)

            source_main_data = np.random.rand(num_rows * num_cols, num_cycle_pts * num_cycles)
            h5_source_main = h5_raw_grp.create_dataset(source_dset_name, data=source_main_data)
            data_utils.write_safe_attrs(h5_source_main, {'units': 'A', 'quantity': 'Current'})

            self.assertFalse(hdf_utils.check_if_main(h5_source_main))

            # Now need to link as main!
            hdf_utils.link_as_main(h5_source_main, h5_pos_inds, h5_pos_vals, h5_source_spec_inds, h5_source_spec_vals)

            # Finally:
            self.assertTrue(hdf_utils.check_if_main(h5_source_main))

        os.remove(file_path)

    def test_link_as_main_size_mismatch(self):
        file_path = 'link_as_main.h5'
        data_utils.delete_existing_file(file_path)
        with h5py.File(file_path) as h5_f:
            h5_raw_grp = h5_f.create_group('Raw_Measurement')

            num_rows = 3
            num_cols = 5
            num_cycles = 2
            num_cycle_pts = 7

            source_dset_name = 'source_main'

            source_pos_data = np.vstack((np.tile(np.arange(num_cols), num_rows),
                                         np.repeat(np.arange(num_rows), num_cols))).T
            pos_attrs = {'units': ['nm', 'um'], 'labels': ['X', 'Y']}

            h5_pos_inds = h5_raw_grp.create_dataset('Position_Indices', data=source_pos_data, dtype=np.uint16)
            data_utils.write_aux_reg_ref(h5_pos_inds, pos_attrs['labels'], is_spec=False)
            data_utils.write_string_list_as_attr(h5_pos_inds, pos_attrs)

            h5_pos_vals = h5_raw_grp.create_dataset('Position_Values', data=source_pos_data, dtype=np.float32)
            data_utils.write_aux_reg_ref(h5_pos_vals, pos_attrs['labels'], is_spec=False)
            data_utils.write_string_list_as_attr(h5_pos_vals, pos_attrs)

            source_spec_data = np.vstack((np.tile(np.arange(num_cycle_pts), num_cycles),
                                          np.repeat(np.arange(num_cycles), num_cycle_pts)))
            source_spec_attrs = {'units': ['V', ''], 'labels': ['Bias', 'Cycle']}

            h5_source_spec_inds = h5_raw_grp.create_dataset('Spectroscopic_Indices', data=source_spec_data,
                                                            dtype=np.uint16)
            data_utils.write_aux_reg_ref(h5_source_spec_inds, source_spec_attrs['labels'], is_spec=True)
            data_utils.write_string_list_as_attr(h5_source_spec_inds, source_spec_attrs)

            h5_source_spec_vals = h5_raw_grp.create_dataset('Spectroscopic_Values', data=source_spec_data,
                                                            dtype=np.float32)
            data_utils.write_aux_reg_ref(h5_source_spec_vals, source_spec_attrs['labels'], is_spec=True)
            data_utils.write_string_list_as_attr(h5_source_spec_vals, source_spec_attrs)

            source_main_data = np.random.rand(num_rows * num_cols, num_cycle_pts * num_cycles)
            h5_source_main = h5_raw_grp.create_dataset(source_dset_name, data=source_main_data)
            data_utils.write_safe_attrs(h5_source_main, {'units': 'A', 'quantity': 'Current'})

            self.assertFalse(hdf_utils.check_if_main(h5_source_main))

            # Swap the order of the datasets to cause a clash in the shapes
            with self.assertRaises(ValueError):
                hdf_utils.link_as_main(h5_source_main, h5_source_spec_inds, h5_pos_vals, h5_pos_inds,
                                       h5_source_spec_vals)

        os.remove(file_path)

    def test_copy_attributes_file_dset(self):
        file_path = 'test.h5'
        easy_attrs = {'1_string': 'Current', '1_number': 35.23}
        also_easy_attr = {'N_numbers': [1, -53.6, 0.000463]}
        hard_attrs = {'N_strings': np.array(['a', 'bc', 'def'], dtype='S')}
        data_utils.delete_existing_file(file_path)
        with h5py.File(file_path) as h5_f:
            h5_f.attrs.update(easy_attrs)
            h5_f.attrs.update(also_easy_attr)
            h5_f.attrs.update(hard_attrs)
            h5_dset = h5_f.create_dataset('Main_01', data=[1, 2, 3])
            hdf_utils.copy_attributes(h5_f, h5_dset)
            for key, val in easy_attrs.items():
                self.assertEqual(val, h5_dset.attrs[key])
            for key, val in also_easy_attr.items():
                self.assertTrue(np.all([x == y for x, y in zip(val, h5_dset.attrs[key])]))
            for key, val in hard_attrs.items():
                self.assertTrue(np.all([x == y for x, y in zip(val, h5_dset.attrs[key])]))
        os.remove(file_path)

    def test_copy_attributes_group_dset(self):
        file_path = 'test.h5'
        easy_attrs = {'1_string': 'Current', '1_number': 35.23}
        also_easy_attr = {'N_numbers': [1, -53.6, 0.000463]}
        hard_attrs = {'N_strings': np.array(['a', 'bc', 'def'], dtype='S')}
        data_utils.delete_existing_file(file_path)
        with h5py.File(file_path) as h5_f:
            h5_group = h5_f.create_group('Group')
            h5_group.attrs.update(easy_attrs)
            h5_group.attrs.update(also_easy_attr)
            h5_group.attrs.update(hard_attrs)
            h5_dset = h5_f.create_dataset('Main_01', data=[1, 2, 3])
            hdf_utils.copy_attributes(h5_group, h5_dset)
            for key, val in easy_attrs.items():
                self.assertEqual(val, h5_dset.attrs[key])
            for key, val in also_easy_attr.items():
                self.assertTrue(np.all([x == y for x, y in zip(val, h5_dset.attrs[key])]))
            for key, val in hard_attrs.items():
                self.assertTrue(np.all([x == y for x, y in zip(val, h5_dset.attrs[key])]))
        os.remove(file_path)

    def test_copy_attributes_dset_w_reg_ref_group_but_skipped(self):
        file_path = 'test.h5'
        data_utils.delete_existing_file(file_path)
        data = np.random.rand(5, 7)
        easy_attrs = {'1_string': 'Current', '1_number': 35.23}
        with h5py.File(file_path) as h5_f:
            h5_dset_source = h5_f.create_dataset('Source', data=data)
            h5_dset_source.attrs.update(easy_attrs)
            h5_dset_sink = h5_f.create_dataset('Sink', data=data)
            reg_refs = {'even_rows': (slice(0, None, 2), slice(None)),
                        'odd_rows': (slice(1, None, 2), slice(None))}
            for reg_ref_name, reg_ref_tuple in reg_refs.items():
                h5_dset_source.attrs[reg_ref_name] = h5_dset_source.regionref[reg_ref_tuple]

            hdf_utils.copy_attributes(h5_dset_source, h5_dset_sink, skip_refs=True)

            self.assertEqual(len(h5_dset_sink.attrs), len(easy_attrs))
            for key, val in easy_attrs.items():
                self.assertEqual(val, h5_dset_sink.attrs[key])

        os.remove(file_path)

    def test_copy_attributes_dset_w_reg_ref_group_to_file(self):
        file_path = 'test.h5'
        data_utils.delete_existing_file(file_path)
        data = np.random.rand(5, 7)
        easy_attrs = {'1_string': 'Current', '1_number': 35.23}
        with h5py.File(file_path) as h5_f:
            h5_dset_source = h5_f.create_dataset('Source', data=data)
            h5_dset_source.attrs.update(easy_attrs)
            reg_refs = {'even_rows': (slice(None), slice(0, None, 2)),
                        'odd_rows': (slice(None), slice(1, None, 2))}
            for reg_ref_name, reg_ref_tuple in reg_refs.items():
                h5_dset_source.attrs[reg_ref_name] = h5_dset_source.regionref[reg_ref_tuple]

            if sys.version_info.major == 3:
                with self.assertWarns(UserWarning):
                    hdf_utils.copy_attributes(h5_dset_source, h5_f, skip_refs=False)
            else:
                hdf_utils.copy_attributes(h5_dset_source, h5_f, skip_refs=False)

            self.assertEqual(len(h5_f.attrs), len(easy_attrs))
            for key, val in easy_attrs.items():
                self.assertEqual(val, h5_f.attrs[key])

        os.remove(file_path)

    def test_copy_attributes_dset_w_reg_ref_group(self):
        file_path = 'test.h5'
        data_utils.delete_existing_file(file_path)
        data = np.random.rand(5, 7)
        easy_attrs = {'1_string': 'Current', '1_number': 35.23}
        with h5py.File(file_path) as h5_f:
            h5_dset_source = h5_f.create_dataset('Source', data=data)
            h5_dset_source.attrs.update(easy_attrs)
            h5_dset_sink = h5_f.create_dataset('Sink', data=data)
            reg_refs = {'even_rows': (slice(0, None, 2), slice(None)),
                        'odd_rows': (slice(1, None, 2), slice(None))}
            for reg_ref_name, reg_ref_tuple in reg_refs.items():
                h5_dset_source.attrs[reg_ref_name] = h5_dset_source.regionref[reg_ref_tuple]

            hdf_utils.copy_attributes(h5_dset_source, h5_dset_sink, skip_refs=False)

            self.assertEqual(len(h5_dset_sink.attrs), len(reg_refs) + len(easy_attrs))
            for key, val in easy_attrs.items():
                self.assertEqual(val, h5_dset_sink.attrs[key])

            self.assertTrue('labels' not in h5_dset_sink.attrs.keys())

            expected_data = [data[0:None:2, :], data[1:None:2, :]]
            written_data = [h5_dset_sink[h5_dset_sink.attrs['even_rows']],
                            h5_dset_sink[h5_dset_sink.attrs['odd_rows']]]

            for exp, act in zip(expected_data, written_data):
                self.assertTrue(np.allclose(exp, act))

        os.remove(file_path)

    def test_copy_attributes_illegal_to_from_reg_ref(self):
        file_path = 'test.h5'
        data_utils.delete_existing_file(file_path)
        data = np.random.rand(5, 7)
        with h5py.File(file_path) as h5_f:
            h5_dset_source = h5_f.create_dataset('Source', data=data)
            h5_dset_dest = h5_f.create_dataset('Sink', data=data[:-1, :-1])
            reg_refs = {'even_rows': (slice(0, None, 2), slice(None)),
                        'odd_rows': (slice(1, None, 2), slice(None))}
            for reg_ref_name, reg_ref_tuple in reg_refs.items():
                h5_dset_source.attrs[reg_ref_name] = h5_dset_source.regionref[reg_ref_tuple]

            if sys.version_info.major == 3:
                with self.assertWarns(UserWarning):
                    hdf_utils.copy_attributes(h5_dset_source, h5_dset_dest, skip_refs=False)
            else:
                hdf_utils.copy_attributes(h5_dset_source, h5_dset_dest, skip_refs=False)

    def test_copy_main_attributes_valid(self):
        file_path = 'test.h5'
        main_attrs = {'quantity': 'Current', 'units': 'nA'}
        data_utils.delete_existing_file(file_path)
        with h5py.File(file_path) as h5_f:
            h5_dset_source = h5_f.create_dataset('Main_01', data=[1, 23])
            h5_dset_source.attrs.update(main_attrs)
            h5_group = h5_f.create_group('Group')
            h5_dset_sink = h5_group.create_dataset('Main_02', data=[4, 5])
            hdf_utils.copy_main_attributes(h5_dset_source, h5_dset_sink)
            for key, val in main_attrs.items():
                self.assertEqual(val, h5_dset_sink.attrs[key])
        os.remove(file_path)

    def test_copy_main_attributes_no_main_attrs(self):
        file_path = 'test.h5'
        data_utils.delete_existing_file(file_path)
        with h5py.File(file_path) as h5_f:
            h5_dset_source = h5_f.create_dataset('Main_01', data=[1, 23])
            h5_group = h5_f.create_group('Group')
            h5_dset_sink = h5_group.create_dataset('Main_02', data=[4, 5])
            with self.assertRaises(KeyError):
                hdf_utils.copy_main_attributes(h5_dset_source, h5_dset_sink)
        os.remove(file_path)

    def test_copy_main_attributes_wrong_objects(self):
        file_path = 'test.h5'
        data_utils.delete_existing_file(file_path)
        with h5py.File(file_path) as h5_f:
            h5_dset_source = h5_f.create_dataset('Main_01', data=[1, 23])
            h5_group = h5_f.create_group('Group')
            with self.assertRaises(TypeError):
                hdf_utils.copy_main_attributes(h5_dset_source, h5_group)
            with self.assertRaises(TypeError):
                hdf_utils.copy_main_attributes(h5_group, h5_dset_source)
        os.remove(file_path)

    def test_create_empty_dataset_same_group_new_attrs(self):
        file_path = 'test.h5'
        existing_attrs = {'a': 1, 'b': 'Hello'}
        easy_attrs = {'1_string': 'Current', '1_number': 35.23}
        data_utils.delete_existing_file(file_path)
        with h5py.File(file_path) as h5_f:
            h5_dset_source = h5_f.create_dataset('Source', data=[1, 2, 3])
            h5_dset_source.attrs.update(existing_attrs)
            h5_duplicate = hdf_utils.create_empty_dataset(h5_dset_source, np.float16, 'Duplicate', new_attrs=easy_attrs)
            self.assertIsInstance(h5_duplicate, h5py.Dataset)
            self.assertEqual(h5_duplicate.parent, h5_dset_source.parent)
            self.assertEqual(h5_duplicate.name, '/Duplicate')
            self.assertEqual(h5_duplicate.dtype, np.float16)
            for key, val in easy_attrs.items():
                self.assertEqual(val, h5_duplicate.attrs[key])
            for key, val in existing_attrs.items():
                self.assertEqual(val, h5_duplicate.attrs[key])

        os.remove(file_path)

    def test_create_empty_dataset_diff_groups(self):
        file_path = 'test.h5'
        existing_attrs = {'a': 1, 'b': 'Hello'}
        easy_attrs = {'1_string': 'Current', '1_number': 35.23}
        data_utils.delete_existing_file(file_path)
        with h5py.File(file_path) as h5_f:
            h5_dset_source = h5_f.create_dataset('Source', data=[1, 2, 3])
            h5_dset_source.attrs.update(existing_attrs)
            h5_group = h5_f.create_group('Group')
            h5_duplicate = hdf_utils.create_empty_dataset(h5_dset_source, np.float16, 'Duplicate',
                                                          h5_group=h5_group, new_attrs=easy_attrs)
            self.assertIsInstance(h5_duplicate, h5py.Dataset)
            self.assertEqual(h5_duplicate.parent, h5_group)
            self.assertEqual(h5_duplicate.name, '/Group/Duplicate')
            self.assertEqual(h5_duplicate.dtype, np.float16)
            for key, val in easy_attrs.items():
                self.assertEqual(val, h5_duplicate.attrs[key])
            for key, val in existing_attrs.items():
                self.assertEqual(val, h5_duplicate.attrs[key])

        os.remove(file_path)

    def test_create_empty_dataset_w_region_refs(self):
        file_path = 'test.h5'
        data_utils.delete_existing_file(file_path)
        data = np.random.rand(5, 7)
        main_attrs = {'quantity': 'Current', 'units': 'nA'}
        with h5py.File(file_path) as h5_f:
            h5_dset_source = h5_f.create_dataset('Source', data=data)
            h5_dset_source.attrs.update(main_attrs)
            reg_refs = {'even_rows': (slice(0, None, 2), slice(None)),
                        'odd_rows': (slice(1, None, 2), slice(None))}

            for reg_ref_name, reg_ref_tuple in reg_refs.items():
                h5_dset_source.attrs[reg_ref_name] = h5_dset_source.regionref[reg_ref_tuple]

            h5_copy = hdf_utils.create_empty_dataset(h5_dset_source, np.float16, 'Existing')

            for reg_ref_name in reg_refs.keys():
                self.assertTrue(isinstance(h5_copy.attrs[reg_ref_name], h5py.RegionReference))
                self.assertTrue(h5_dset_source[h5_dset_source.attrs[reg_ref_name]].shape == h5_copy[
                    h5_copy.attrs[reg_ref_name]].shape)

        os.remove(file_path)

    def test_create_empty_dataset_existing_dset_name(self):
        file_path = 'test.h5'
        data_utils.delete_existing_file(file_path)
        with h5py.File(file_path) as h5_f:
            h5_dset_source = h5_f.create_dataset('Source', data=[1, 2, 3])
            _ = h5_f.create_dataset('Existing', data=[4, 5, 6])
            if sys.version_info.major == 3:
                with self.assertWarns(UserWarning):
                    h5_duplicate = hdf_utils.create_empty_dataset(h5_dset_source, np.float16, 'Existing')
            else:
                h5_duplicate = hdf_utils.create_empty_dataset(h5_dset_source, np.float16, 'Existing')
            self.assertIsInstance(h5_duplicate, h5py.Dataset)
            self.assertEqual(h5_duplicate.name, '/Existing')
            self.assertTrue(np.allclose(h5_duplicate[()], np.zeros(3)))
            self.assertEqual(h5_duplicate.dtype, np.float16)
        os.remove(file_path)


if __name__ == '__main__':
    unittest.main()