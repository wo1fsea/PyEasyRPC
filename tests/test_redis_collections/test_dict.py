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

    def test_dict_msg_packer(self):
        self.__test_dict("msg_packer_test", MsgPacker)

    def test_dict_pickle_packer(self):
        self.__test_dict("pickle_packer_test", PicklePacker)

    def __test_dict(self, redis_key, packer):
        # test data
        data = {
            "int": 1,
            "float": 2.,
            "string": "string",
            "dict": {"int": 1, "float": 2., "string": "string"},
            "list": [0, "1", 2.0, 3],
            "tuple": (0, "1", 2.0, 3),
        }
        d = Dict(redis_key, packer)
        # get the same Dict by key
        d2 = Dict(redis_key, packer)

        d.clear()

        self.assertEqual(len(d), 0)

        d["int"] = data["int"]
        d["float"] = data["float"]
        d["string"] = data["string"]

        self.assertEqual(len(d), 3)

        d["dict"] = data["dict"]
        d["list"] = data["list"]
        d["tuple"] = data["tuple"]

        self.assertEqual(len(d), 6)

        self.assertEqual(d.get("not found"), None)
        self.assertEqual(d.get("not found", None), None)
        self.assertEqual(d.get("not found", 1), 1)

        d["found"] = "found"

        self.assertEqual("found" in d, True)
        self.assertEqual("found" not in d, False)
        self.assertEqual(d.get("found"), "found")

        # test setdefault
        self.assertEqual(d.setdefault("found", None), "found")
        self.assertEqual(d.setdefault("not found", "not found"), "not found")

        self.assertEqual(d.get("not found"), "not found")

        del d["not found"]
        del d["found"]

        self.assertEqual("found" in d, False)
        self.assertEqual("found" not in d, True)
        self.assertEqual(d.get("found"), None)

        self.assertEqual(d["int"], data["int"])
        self.assertEqual(d["float"], data["float"])
        self.assertEqual(d["string"], data["string"])
        self.assertEqual(d["dict"], data["dict"])
        self.assertSequenceEqual(d["list"], data["list"])
        self.assertSequenceEqual(d["tuple"], data["tuple"])

        # test keys
        self.assertSequenceEqual(sorted(d.keys()), sorted(data.keys()))
        # test iter
        self.assertSequenceEqual(sorted(d), sorted(data.keys()))
        # TODO: test values
        # TODO: test items

        # test redis type
        self.assertEqual(d.Redis_Type, d.get_type())

        # test d2
        self.assertEqual(d2["int"], data["int"])
        self.assertEqual(d2["float"], data["float"])
        self.assertEqual(d2["string"], data["string"])
        self.assertEqual(d2["dict"], data["dict"])
        self.assertSequenceEqual(d2["list"], data["list"])
        self.assertSequenceEqual(d2["tuple"], data["tuple"])

        # test pop
        self.assertEqual(d.pop("int"), 1)

        with self.assertRaises(KeyError) as context:
            d.pop("int")
        self.assertTrue(isinstance(context.exception, KeyError))

        self.assertEqual(d.pop("int", None), None)

        # test ==
        self.assertEqual(d2, d.data)

        # raw
        d.set_raw("count", 1)
        d.increase_by("count", 10)

        self.assertEqual(int(d.get_raw("count")), 11)

        d.increase_by("count", 0.5)
        self.assertEqual(float(d.get_raw("count")), 11.5)

        # clean up
        d2.clear()
        self.assertEqual(len(d), 0)