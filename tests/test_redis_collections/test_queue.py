# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
    Huang Quanyong (wo1fSea)
    quanyongh@foxmail.com
Date:
    2019/8/1
Description:
    test_queue.py
----------------------------------------------------------------------------"""

import unittest
from pyeasyrpc.redis_collections.queue import Queue
from pyeasyrpc.redis_collections.redis_object import MsgPacker, PicklePacker


class RedisQueueTestCase(unittest.TestCase):

    def test_queue_msg_packer(self):
        self.__test_queue("test_queue_msg_pack", MsgPacker)

    def test_queue_pickle_packer(self):
        self.__test_queue("test_queue_pickle_pack", PicklePacker)

    def __test_queue(self, redis_key, packer):
        q = Queue(redis_key, packer=packer)
        q.clear()

        self.assertEqual(q.get(), None)
        self.assertEqual(len(q), 0)

        for i in range(10):
            q.put(i)

        for i in range(10):
            self.assertEqual(q.get(), i)

        self.assertEqual(q.get(), None)

        max_len = 6
        q1 = Queue(redis_key, max_len=max_len, packer=packer)
        for i in range(10):
            q1.put(i)

        self.assertEqual(len(q1), max_len)
        for i in range(10):
            if i < q1.max_len:
                self.assertEqual(q.get(), (10 - max_len) + i)
            else:
                self.assertEqual(q.get(), None)

        q.clear()
        self.assertEqual(len(q), 0)
