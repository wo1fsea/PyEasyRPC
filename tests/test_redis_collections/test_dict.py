# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
    Huang Quanyong (wo1fSea)
    quanyongh@foxmail.com
Date:
    2019/7/30
Description:
    test_dict.py
----------------------------------------------------------------------------"""

import unittest
from pyeasyrpc.redis_collections.dict import Dict
from pyeasyrpc.redis_collections.redis_object import MsgPacker, PicklePacker


class RedisDictTestCase(unittest.TestCase):

    def test_msg_packer(self):
        self.__base_test("msg_packer_test", MsgPacker)

    def test_pickle_packer(self):
        self.__base_test("pickle_packer_test", PicklePacker)

    def __base_test(self, redis_key, packer):
        d = Dict(redis_key, packer)
        d.clear()

        self.assertEqual(len(d), 0)

        d["int"] = 1
        d["float"] = 1.1
        d["string"] = "string"

        self.assertEqual(len(d), 3)

        d["dict"] = {"int": 1, "float": 1.1, "string": "string"}
        d["list"] = [0, "1", 2.0, 3]
        d["tuple"] = (0, "1", 2.0, 3)

        self.assertEqual(len(d), 6)

        self.assertEqual(d.get("not found"), None)
        self.assertEqual(d.get("not found", None), None)
        self.assertEqual(d.get("not found", 1), 1)

        d["found"] = "found"

        self.assertEqual("found" in d, True)
        self.assertEqual("found" not in d, False)
        self.assertEqual(d.get("found"), "found")

        del d["found"]
        self.assertEqual("found" in d, False)
        self.assertEqual("found" not in d, True)
        self.assertEqual(d.get("found"), None)

        self.assertEqual(d["int"], 1)
        self.assertEqual(d["float"], 1.1)
        self.assertEqual(d["string"], "string")
        self.assertEqual(d["dict"], {"int": 1, "float": 1.1, "string": "string"})
        self.assertSequenceEqual(d["list"], [0, "1", 2.0, 3])
        self.assertSequenceEqual(d["tuple"], (0, "1", 2.0, 3))

        # get the same Dict by key
        d2 = Dict(redis_key, packer)
        self.assertEqual(d2["int"], 1)
        self.assertEqual(d2["float"], 1.1)
        self.assertEqual(d2["string"], "string")
        self.assertEqual(d2["dict"], {"int": 1, "float": 1.1, "string": "string"})
        self.assertSequenceEqual(d2["list"], [0, "1", 2.0, 3])
        self.assertSequenceEqual(d2["tuple"], (0, "1", 2.0, 3))

        d2.clear()
        self.assertEqual(len(d), 0)


if __name__ == '__main__':
    unittest.main()
