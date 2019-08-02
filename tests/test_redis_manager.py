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
import time
from pyeasyrpc.rpc_manager import RPCManager


class RPCManagerTestCase(unittest.TestCase):

    def setUp(self):
        self.service_til = 0.5
        self.service_heartbeat_interval = 0.1
        RPCManager.SERVICE_TTL = self.service_til
        RPCManager.SERVICE_HEARTBEAT_INTERVAL = self.service_heartbeat_interval
        self._rpc_manager = RPCManager()

    def test_register_service(self):
        service_name0 = "test0"

        data0 = {
            "service_name": service_name0,
            "method_list": [
                "test_method0",
                "test_method1",
                "test_method2",
                "test_method3",
                "test_method4",
            ]
        }

        data0_1 = {
            "service_name": service_name0,
            "method_list": [
                "test_method0",
                "test_method1",
                "test_method2",
                "test_method3",
            ]
        }

        service_uuid = self._rpc_manager.register_service(
            **data0
        )

        self.assertTrue(service_uuid in self._rpc_manager.get_service_uuid_set(service_name0))

        self.assertEqual(service_uuid, self._rpc_manager.get_alive_service_uuid_low_loss(service_name0))
        self.assertEqual(service_uuid, self._rpc_manager.get_alive_service_uuid_random(service_name0))

        with self.assertRaises(TypeError) as context:
            self._rpc_manager.register_service(
                **data0_1
            )

        self.assertTrue(isinstance(context.exception, TypeError))

        self._rpc_manager.unregister_service(service_name0, service_uuid)
        self.assertFalse(self._rpc_manager.get_alive_service_uuid_set(service_name0))

        service_uuid = self._rpc_manager.register_service(
            **data0
        )
        time.sleep(self.service_til + 0.1)
        self.assertFalse(self._rpc_manager.get_alive_service_uuid_set(service_name0))
        self._rpc_manager.unregister_service(service_name0, service_uuid)

        service_uuid = self._rpc_manager.register_service(
            enable_multi_instance=False,
            **data0
        )

        with self.assertRaises(TypeError) as context:
            self._rpc_manager.register_service(
                **data0
            )

        self.assertTrue(isinstance(context.exception, TypeError))
        # clean up
        self._rpc_manager.unregister_service(service_name0, service_uuid)
