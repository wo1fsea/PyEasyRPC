# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
    Huang Quanyong (wo1fSea)
    quanyongh@foxmail.com
Date:
    2019/8/1
Description:
    test_redis_object.py
----------------------------------------------------------------------------"""

import unittest
from pyeasyrpc.redis_collections.redis_object import RedisObject, MsgPacker, PicklePacker
from pyeasyrpc.redis_collections.dict import Dict
import time


class RedisObjectTestCase(unittest.TestCase):

    def test_set_msg_packer(self):
        self.__test_redis_object("test_redis_object_msg_pack", MsgPacker)

    def test_set_pickle_packer(self):
        self.__test_redis_object("test_redis_object_pickle_pack", PicklePacker)

    def __test_redis_object(self, redis_key, pack):
        obj = RedisObject(redis_key, pack)

        self.assertEqual(obj.key, redis_key)

        obj.clear()
        self.assertFalse(obj.exists)

        d = Dict(redis_key, pack)
        d["test"] = "test"

        self.assertTrue(obj.exists)

        d.set_expire(100)

        self.assertTrue(obj.exists)

        time.sleep(0.2)

        self.assertFalse(obj.exists)
