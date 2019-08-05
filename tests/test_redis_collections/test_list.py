# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
    Huang Quanyong (wo1fSea)
    quanyongh@foxmail.com
Date:
    2019/8/1
Description:
    test_list.py
----------------------------------------------------------------------------"""

import unittest
from pyeasyrpc.redis_collections.list import List
from pyeasyrpc.redis_collections.redis_object import MsgPacker, PicklePacker


class RedisListTestCase(unittest.TestCase):

    def test_list_msg_packer(self):
        self.__test_list("test_list_msg_pack", MsgPacker)

    def test_list_pickle_packer(self):
        self.__test_list("test_list_pickle_pack", PicklePacker)

    def __test_list(self, redis_key, packer):
        # test data
        data = [
            1,
            2.0,
            "string",
            {"int": 1, "float": 2., "string": "string"},
            [0, "1", 2.0, 3],
        ]

        l = List(redis_key, packer)

        l.clear()
        self.assertEqual(len(l), 0)
        l.extend(data)
        self.assertEqual(l, data)
        self.assertEqual(l.data, data)
        self.assertEqual(len(l), len(data))

        l.clear()
        for d in data:
            self.assertFalse(d in l)
            l.append(d)
            self.assertTrue(d in l)

        for d in data:
            self.assertTrue(d in l)
            l.remove(d)
            self.assertFalse(d in l)

        l.clear()

        test_l = list()
        i = 0
        for ii in range(10):
            i = i // 2

            test_l.insert(i, i)
            l.insert(i, i)

            self.assertEqual(l, test_l)
            self.assertEqual(l.count(i), l.count(i))
            self.assertEqual(l.index(i), l.index(i))

        test_l.reverse()
        l.reverse()
        self.assertEqual(l, test_l)

        test_l.sort()
        l.sort()
        test_l.insert(0, 100)
        l.insert(0, 100)

        self.assertEqual(l, test_l)
