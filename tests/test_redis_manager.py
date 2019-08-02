# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
    Huang Quanyong (wo1fSea)
    quanyongh@foxmail.com
Date:
    2019/7/30
Description:
    test_redis_manager.py
----------------------------------------------------------------------------"""

import unittest
from pyeasyrpc.rpc_manager import RPCManager


class RPCManagerTestCase(unittest.TestCase):

    def setUp(self):
        self._rpc_manager = RPCManager()

    def test_register_service(self):

        data0 = {
            "service_name": "service_name_test0",
            "method_list": [
                "test_method0",
                "test_method1",
                "test_method2",
                "test_method3",
                "test_method4",
            ]
        }

        service_uuid = self._rpc_manager.register_service(
            **data0
        )

        self.assertTrue(service_uuid in self._rpc_manager.get_service_instance_list("service_name_test0"))
        self.assertEqual(service_uuid, self._rpc_manager.get_service_instance_low_loss("service_name_test0"))
        self.assertEqual(service_uuid, self._rpc_manager.get_service_instance_random("service_name_test0"))
