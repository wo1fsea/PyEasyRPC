# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
    Huang Quanyong (wo1fSea)
    quanyongh@foxmail.com
Date:
    2019/8/1
Description:
    test_set.py
----------------------------------------------------------------------------"""

import unittest
from pyeasyrpc.redis_collections.set import Set
from pyeasyrpc.redis_collections.redis_object import MsgPacker, PicklePacker


class RedisSetTestCase(unittest.TestCase):

    def test_set_msg_packer(self):
        self.__test_set("test_set_msg_pack", MsgPacker)

    def test_set_pickle_packer(self):
        self.__test_set("test_set_pickle_pack", PicklePacker)

    def __test_set(self, redis_key, packer):
        # test data
        data = {
            1, 2.0, "string",
        }

        s = Set(redis_key, packer)

        # get the same Set by key
        s2 = Set(redis_key, packer)

        s.clear()

        self.assertEqual(len(s), 0)

        for element in data:
            self.assertEqual(element in s, False)

        for element in data:
            s.add(element)

        self.assertEqual(len(s), len(data))

        for element in data:
            self.assertEqual(element in s, True)
            s.remove(element)
            self.assertEqual(element not in s, True)

        with self.assertRaises(KeyError) as context:
            s.remove("not found")

        self.assertTrue(isinstance(context.exception, KeyError))

        s.update(data)

        # test ==
        self.assertEqual(s.data, data)
        self.assertEqual(s, data)

        # test pop
        element = s.pop()
        self.assertTrue(element not in s)
        s.add(element)

        # test s2
        self.assertEqual(s2, data)

        for element in data:
            self.assertEqual(element in s, True)
            s.discard(element)
            self.assertEqual(element not in s, True)

        s.discard("not found")

        self.assertEqual(s, s2)
        s.add("one")
        self.assertEqual(s, s2)

        s2.clear()
        self.assertEqual(len(s), 0)

        # test op
        data0 = {1, 2, 3, 4, 5}
        data1 = {3, 4, 5, 6, 7}
        self.__test_set_op(
            Set(redis_key + "0", packer),
            Set(redis_key + "1", packer),
            data0,
            data1
        )
        self.__test_set_op(
            Set(redis_key + "0", packer),
            set(),
            data0,
            data1
        )
        self.__test_set_op(
            set(),
            Set(redis_key + "1", packer),
            data0,
            data1
        )

        data0 = {1, 2, 3, 4, 5}
        data1 = {1, 2, 3, 4, 5}
        self.__test_set_op(
            Set(redis_key + "0", packer),
            Set(redis_key + "1", packer),
            data0,
            data1
        )
        self.__test_set_op(
            Set(redis_key + "0", packer),
            set(),
            data0,
            data1
        )
        self.__test_set_op(
            set(),
            Set(redis_key + "1", packer),
            data0,
            data1
        )

        data0 = {1, 2, 3, 4, 5}
        data1 = {1, 2, 3}
        self.__test_set_op(
            Set(redis_key + "0", packer),
            Set(redis_key + "1", packer),
            data0,
            data1
        )
        self.__test_set_op(
            Set(redis_key + "0", packer),
            set(),
            data0,
            data1
        )
        self.__test_set_op(
            set(),
            Set(redis_key + "1", packer),
            data0,
            data1
        )

        data0 = {1, 2, 3, 4, 5}
        data1 = {1, 2, 3, 4, 5, 6, 7}
        self.__test_set_op(
            Set(redis_key + "0", packer),
            Set(redis_key + "1", packer),
            data0,
            data1
        )
        self.__test_set_op(
            Set(redis_key + "0", packer),
            set(),
            data0,
            data1
        )
        self.__test_set_op(
            set(),
            Set(redis_key + "1", packer),
            data0,
            data1
        )

    def __test_set_op(self, s0, s1, data0, data1):
        s0.clear()
        s1.clear()

        s0.update(data0)
        s1.update(data1)

        self.assertEqual(s0.difference(s1), data0.difference(data1))
        self.assertEqual(s0.intersection(s1), data0.intersection(data1))
        self.assertEqual(s0.symmetric_difference(s1), data0.symmetric_difference(data1))
        self.assertEqual(s0.isdisjoint(s1), data0.isdisjoint(data1))
        self.assertEqual(s0.issubset(s1), data0.issubset(data1))
        self.assertEqual(s0.issuperset(s1), data0.issuperset(data1))

        self.assertEqual(s0 == s1, data0 == data1)
        self.assertEqual(s0 != s1, data0 != data1)
        self.assertEqual(s0 >= s1, data0 >= data1)
        self.assertEqual(s0 > s1, data0 > data1)
        self.assertEqual(s0 <= s1, data0 <= data1)
        self.assertEqual(s0 < s1, data0 < data1)
        self.assertEqual(s0 - s1, data0 - data1)
        self.assertEqual(s0 & s1, data0 & data1)
        self.assertEqual(s0 | s1, data0 | data1)
        self.assertEqual(s0 ^ s1, data0 ^ data1)

        s0.clear()
        s0.update(data0)
        s0.difference_update(s1)
        self.assertEqual(s0, data0.difference(data1))

        s0.clear()
        s0.update(data0)
        s0.intersection_update(s1)
        self.assertEqual(s0, data0.intersection(data1))

        s0.clear()
        s0.update(data0)
        s0.symmetric_difference_update(s1)
        self.assertEqual(s0, data0.symmetric_difference(data1))

        s0.clear()
        s1.clear()


if __name__ == '__main__':
    unittest.main()
