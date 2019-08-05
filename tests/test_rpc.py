# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
    Huang Quanyong (wo1fSea)
    quanyongh@foxmail.com
Date:
    2019/8/4
Description:
    test_rpc.py
----------------------------------------------------------------------------"""

import unittest
import asyncio

from pyeasyrpc.rpc import remote_method
from pyeasyrpc.rpc import RPCService
from pyeasyrpc.rpc import RPCClient
from pyeasyrpc.rpc import AsyncRPCClient


class TestInstance(RPCService):
    @remote_method
    def add(self, a, b):
        return a + b


class RPCTestCase(unittest.TestCase):

    def test_call_method(self):

        instance0 = TestInstance()
        instance1 = TestInstance()

        client0 = RPCClient("TestInstance", instance0.service_uuid)
        rpc_uuid0, expire_time0 = client0.set_call_method_request("add", (1, 2), {})

        client1 = RPCClient("TestInstance", instance1.service_uuid)
        rpc_uuid1, expire_time1 = client1.set_call_method_request("add", (1, 2), {})

        self.assertEqual(client0.get_methods(), instance0.rpc_methods)

        while instance0.process():
            pass

        while instance1.process():
            pass

        self.assertEqual(
            client0.get_call_method_result_with_uuid(rpc_uuid0, expire_time0).get("return_value"),
            3
        )
        self.assertEqual(
            client1.get_call_method_result_with_uuid(rpc_uuid1, expire_time1).get("return_value"),
            3
        )

        instance0.unregister()
        instance1.unregister()

    def test_run_service_in_thread(self):
        instance0 = TestInstance()

        client0 = RPCClient("TestInstance")

        instance0.start_background_running()

        self.assertEqual(client0.add(1, 2), 3)

        instance0.stop_background_running()

        with self.assertRaises(TimeoutError) as context:
            client0.add(1, 2)

        instance0.start_background_running()

        self.assertEqual(client0.add(1, 2), 3)
        self.assertEqual(client0.add(1, 2), 3)
        self.assertEqual(client0.add(1, 2), 3)

        instance0.stop_background_running()
        instance0.unregister()

    def test_return_out_of_order(self):
        instance0 = TestInstance()

        client0 = RPCClient("TestInstance")
        rpc_uuid0, expire_time0 = client0.set_call_method_request("add", (1, 2), {})
        rpc_uuid1, expire_time1 = client0.set_call_method_request("add", (1, 2), {})

        while instance0.process():
            pass

        self.assertEqual(
            client0.get_call_method_result_with_uuid(rpc_uuid1, expire_time1).get("return_value"),
            3
        )
        self.assertEqual(
            client0.get_call_method_result_with_uuid(rpc_uuid0, expire_time0).get("return_value"),
            3
        )

        instance0.unregister()

    def test_service_process_request_in_thread(self):
        instance0 = TestInstance(process_request_in_thread=True)

        client0 = RPCClient("TestInstance")

        instance0.start_background_running()

        self.assertEqual(client0.add(1, 2), 3)
        self.assertEqual(client0.add(1, 2), 3)
        self.assertEqual(client0.add(1, 2), 3)

        instance0.stop_background_running()

        with self.assertRaises(TimeoutError) as context:
            client0.add(1, 2)

        instance0.start_background_running()

        self.assertEqual(client0.add(1, 2), 3)
        self.assertEqual(client0.add(1, 2), 3)
        self.assertEqual(client0.add(1, 2), 3)

        instance0.stop_background_running()
        instance0.unregister()

    def test_client_call_an(self):
        instance0 = TestInstance(process_request_in_thread=True)
        client = AsyncRPCClient("TestInstance")

        async def add():
            self.assertEqual(await client.add(1, 2), 3)

        async def catch_exception():
            with self.assertRaises(Exception) as context:
                await client.add()

        task = [add(), catch_exception()]

        async def func():
            await asyncio.wait(task)

        instance0.start_background_running()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(func())

        instance0.stop_background_running()
        instance0.unregister()

if __name__ == '__main__':
    RPCTestCase().test_run_service_in_thread()
