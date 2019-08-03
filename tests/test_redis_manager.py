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
        self.service_ttl = 0.5
        self.service_heartbeat_interval = 0.1
        RPCManager.SERVICE_TTL = self.service_ttl
        RPCManager.SERVICE_HEARTBEAT_INTERVAL = self.service_heartbeat_interval

        self.rpc_manager = RPCManager()

        self.service_name0 = "test0"
        self.service_data0 = {
            "service_name": self.service_name0,
            "method_list": sorted([
                "test_method0",
                "test_method1",
                "test_method2",
                "test_method3",
            ])
        }

        self.service_data0_1 = {
            "service_name": self.service_name0,
            "method_list": sorted([
                "test_method0",
                "test_method1",
                "test_method2",
            ])
        }

        self.service_name1 = "test1"
        self.service_data1 = {
            "service_name": self.service_name1,
            "method_list": sorted([
                "test_method4",
                "test_method5",
            ])
        }

    def test_register_service(self):
        service_uuid = self.rpc_manager.register_service(
            **self.service_data0
        )

        self.assertTrue(service_uuid in self.rpc_manager.get_service_uuid_set(self.service_name0))

        self.assertEqual(
            service_uuid,
            self.rpc_manager.get_alive_service_uuid_low_loss(self.service_name0)
        )
        self.assertEqual(
            service_uuid,
            self.rpc_manager.get_alive_service_uuid_random(self.service_name0)
        )

        self.assertSequenceEqual(
            self.service_data0["method_list"],
            self.rpc_manager.get_method_list(self.service_name0)
        )

        with self.assertRaises(TypeError) as context:
            self.rpc_manager.register_service(
                **self.service_data0_1
            )
        self.assertTrue(isinstance(context.exception, TypeError))

        self.assertSequenceEqual([self.service_name0], self.rpc_manager.get_service_list())

        self.rpc_manager.unregister_service(self.service_name0, service_uuid)
        self.assertFalse(self.rpc_manager.get_alive_service_uuid_set(self.service_name0))

        self.assertEqual(None, self.rpc_manager.get_alive_service_uuid_random(self.service_name0))
        self.assertEqual(None, self.rpc_manager.get_alive_service_uuid_low_loss(self.service_name0))

        self.assertSequenceEqual([], self.rpc_manager.get_service_list())

        service_uuid = self.rpc_manager.register_service(
            **self.service_data0
        )
        service_uuid1 = self.rpc_manager.register_service(
            **self.service_data0
        )
        self.assertEqual(len(self.rpc_manager.get_service_uuid_set(self.service_name0)), 2)
        self.rpc_manager.unregister_service(self.service_name0, service_uuid1)
        self.assertEqual(len(self.rpc_manager.get_service_uuid_set(self.service_name0)), 1)

        time.sleep(self.service_ttl * 2)

        self.assertEqual(len(self.rpc_manager.get_alive_service_uuid_set(self.service_name0)), 0)
        self.rpc_manager.unregister_service(self.service_name0, service_uuid)

        service_uuid = self.rpc_manager.register_service(
            enable_multi_instance=False,
            **self.service_data0
        )

        with self.assertRaises(TypeError) as context:
            self.rpc_manager.register_service(
                **self.service_data0
            )

        self.assertTrue(isinstance(context.exception, TypeError))
        # clean up
        self.rpc_manager.unregister_service(self.service_name0, service_uuid)

    def test_heartbeat(self):
        service_uuid = self.rpc_manager.register_service(
            **self.service_data0
        )

        self.assertTrue(self.rpc_manager.check_service_instance_alive(self.service_name0, service_uuid))

        time.sleep(self.service_ttl / 3)
        self.assertTrue(self.rpc_manager.service_heartbeat(self.service_name0, service_uuid))
        time.sleep(self.service_ttl / 3)
        self.assertTrue(self.rpc_manager.service_heartbeat(self.service_name0, service_uuid))
        time.sleep(self.service_ttl / 3)
        self.assertTrue(self.rpc_manager.service_heartbeat(self.service_name0, service_uuid))
        time.sleep(self.service_ttl / 3)

        self.assertTrue(self.rpc_manager.check_service_instance_alive(self.service_name0, service_uuid))

        time.sleep(self.service_ttl)
        self.assertFalse(self.rpc_manager.check_service_instance_alive(self.service_name0, service_uuid))

        # force delete service instance
        service_uuid = self.rpc_manager.register_service(
            **self.service_data0
        )
        self.assertTrue(self.rpc_manager.check_service_instance_alive(self.service_name0, service_uuid))

        self.rpc_manager.get_service_instance(self.service_name0, service_uuid).clear()
        self.assertFalse(self.rpc_manager.service_heartbeat(self.service_name0, service_uuid))

        # force delete service instance
        service_uuid = self.rpc_manager.register_service(
            **self.service_data0
        )
        self.assertTrue(self.rpc_manager.check_service_instance_alive(self.service_name0, service_uuid))

        self.rpc_manager.get_service_uuid_set(self.service_name0).discard(service_uuid)
        self.assertFalse(self.rpc_manager.service_heartbeat(self.service_name0, service_uuid))
