# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
    Huang Quanyong (wo1fSea)
    quanyongh@foxmail.com
Date:
    2019/8/1
Description:
    test_mail_box.py
----------------------------------------------------------------------------"""

import unittest
import time
from pyeasyrpc.redis_collections.redis_object import MsgPacker, PicklePacker
from pyeasyrpc.redis_collections.mailbox import Mailbox


class RedisMailboxTestCase(unittest.TestCase):

    def test_mailbox_msg_packer(self):
        self.__test_redis_mailbox("test_redis_mailbox_msg_pack", MsgPacker)

    def test_mailbox_pickle_packer(self):
        self.__test_redis_mailbox("test_redis_mailbox_pickle_pack", PicklePacker)

    def __test_redis_mailbox(self, channel, packer):
        mb_receive = Mailbox(channel, packer=packer)
        mb_send = Mailbox(channel, packer=packer)
        mb_receive.subscribe()

        mb_send.set_message(1)
        self.assertTrue(mb_receive.get_message(), 1)

        mb_send.set_message(1.1)
        self.assertTrue(mb_receive.get_message(), 1.1)

        mb_send.set_message(1)
        self.assertTrue(mb_receive.get_message(), 1)

        msg_data = {
            "int": 1,
            "float": 2.,
            "string": "string",
            "dict": {"int": 1, "float": 2., "string": "string"},
            "list": [0, "1", 2.0, 3],
            # MsgPacker do not support tuple
            "tuple": (0, "1", 2.0, 3) if packer is PicklePacker else [0, "1", 2.0, 3],
        }

        sign = [0]

        def msg_handler(data):
            sign[0] += 1
            self.assertEqual(msg_data, data)

        mb_receive_with_handler = Mailbox(channel, msg_handler=msg_handler, packer=packer)
        mb_receive_with_handler.subscribe()
        mb_send.set_message(msg_data)
        mb_receive_with_handler.get_message()

        self.assertEqual(sign[0], 1)

        mb_receive_with_handler.run_in_background()
        mb_send.set_message(msg_data)
        mb_send.set_message(msg_data)
        mb_send.set_message(msg_data)

        time.sleep(1)
        mb_receive_with_handler.stop_background_thread()
        mb_send.set_message(msg_data)

        self.assertEqual(sign[0], 4)
