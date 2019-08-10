# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
    Huang Quanyong (wo1fSea)
    quanyongh@foxmail.com
Date:
    2019/8/4
Description:
    rpc.py
----------------------------------------------------------------------------"""

import inspect
import time
import threading
# import asyncio

from .rpc_manager import DefaultRPCManager
from .redis_collections.mailbox import Mailbox


def remote_method(method):
    frame = inspect.currentframe()
    # class_name = frame.f_back.f_code.co_names
    method_name = method.__code__.co_name
    rpc_methods = frame.f_back.f_locals.setdefault("rpc_methods", [])
    rpc_methods.append(method_name)

    return method


class RPCService(object):
    rpc_methods = []
    CHECK_REQUEST_INTERVAL = 0.01  # s

    def __init__(self,
                 service_name="",
                 enable_multi_instance=True,
                 process_request_in_thread=False,
                 rpc_manager=None
                 ):
        self._rpc_manager = DefaultRPCManager() if not rpc_manager else rpc_manager
        self._service_name = service_name
        self._service_uuid = None
        self._request_mailbox = None
        self._remote_methods = {}
        self._enable_multi_instance = enable_multi_instance
        self._process_request_in_thread = process_request_in_thread

        for name in self.rpc_methods:
            method = getattr(self, name)
            self._remote_methods[name] = method

        self._register()

        self._is_heartbeat_thread_running = False
        self._is_process_thread_running = False

        self._heartbeat_thread = None
        self._process_thread = None

    def _register(self):
        self._service_uuid = self._rpc_manager.register_service(
            self.service_name,
            self.rpc_methods,
            self.enable_multi_instance
        )
        self._request_mailbox = Mailbox(
            self._rpc_manager.get_service_instance_mailbox_channel(
                self.service_name,
                self.service_uuid
            ),
            packer=self._rpc_manager.data_packer,
            url=self._rpc_manager.redis_url
        )
        self._request_mailbox.subscribe()

    def unregister(self):
        self._rpc_manager.unregister_service(self.service_name, self.service_uuid)

    @property
    def service_name(self):
        return self.__class__.__name__ if not self._service_name else self._service_name

    @property
    def service_uuid(self):
        return self._service_uuid

    @property
    def enable_multi_instance(self):
        return self._enable_multi_instance

    def heartbeat(self):
        if not self._rpc_manager.service_heartbeat(self.service_name, self.service_uuid):
            # TODO: log dead
            self._register()

    def start_background_running(self):
        self.start_heartbeat()
        self.start_process()

    def stop_background_running(self):
        self.stop_heartbeat()
        self.stop_process()

    def _process_request(self, rpc_data):
        method_name = rpc_data["method_name"]
        args = rpc_data["args"]
        kwargs = rpc_data["kwargs"]

        return_value = None
        exception = None

        try:

            # TODO: not found method_name?
            method = self._remote_methods[method_name]
            return_value = method(*args, **kwargs)

        except Exception as ex:
            exception = ex

        rpc_data["return_value"] = return_value
        rpc_data["exception"] = exception
        rpc_data["return_time"] = self._rpc_manager.time

        return_mailbox = Mailbox(
            rpc_data["return_mailbox"],
            url=self._rpc_manager.redis_url,
            packer=self._rpc_manager.data_packer
        )

        return_mailbox.set_message(rpc_data)

        self._rpc_manager.increase_total_return(
            rpc_data["service_name"],
            rpc_data["service_uuid"]
        )

    def process(self):
        rpc_data = self._request_mailbox.get_message()
        if rpc_data and rpc_data.get("rpc_uuid"):
            if self._process_request_in_thread:
                t = threading.Thread(target=self._process_request, args=(rpc_data,))
                t.start()
            else:
                self._process_request(rpc_data)
            return True

        return False

    def _process_in_thread(self):
        while self._is_process_thread_running:
            while self.process():
                pass
            time.sleep(self.CHECK_REQUEST_INTERVAL)

    def start_process(self):
        assert self._process_thread is None, "process thread is already running."
        self._is_process_thread_running = True
        self._process_thread = threading.Thread(target=self._process_in_thread)
        self._process_thread.start()

    def stop_process(self):
        assert self._process_thread is not None, "process thread is not running."
        self._is_process_thread_running = False
        self._process_thread.join()
        self._process_thread = None

    def _heartbeat_in_thread(self):
        while self._is_heartbeat_thread_running:
            self.heartbeat()
            time.sleep(self._rpc_manager.SERVICE_HEARTBEAT_INTERVAL)

    def start_heartbeat(self):
        assert self._heartbeat_thread is None, "heartbeat thread is already running."
        self._is_heartbeat_thread_running = True
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_in_thread)
        self._heartbeat_thread.start()

    def stop_heartbeat(self):
        assert self._heartbeat_thread is not None, "heartbeat thread is not running."
        self._is_heartbeat_thread_running = False
        self._heartbeat_thread.join()
        self._heartbeat_thread = None


class RPCClientMethod(object):
    def __init__(self, client, method_name):
        super(RPCClientMethod, self).__init__()
        self._client = client
        self._method_name = method_name

    def __call__(self, *args, **kwargs):
        return self._client.call_method(self._method_name, args, kwargs)


class RPCClient(object):
    def __init__(self, service_name, service_uuid=None, rpc_manager=None):
        super(RPCClient, self).__init__()
        self._rpc_manager = DefaultRPCManager() if not rpc_manager else rpc_manager

        assert service_name in self._rpc_manager.get_service_list(), "service not found."

        self._service_name = service_name
        self._method_list = self._rpc_manager.get_method_list(service_name)

        if service_uuid and service_uuid not in self._rpc_manager.get_alive_service_uuid_set(self._service_name):
            service_uuid = None
        if service_uuid:
            self._service_uuid = service_uuid
        else:
            self._service_uuid = self._rpc_manager.get_alive_service_uuid_low_loss(self.service_name)

        self._client_uuid = self._rpc_manager.gen_client_uuid()

        assert self.service_uuid, "not available service instance."

        self._request_mailbox = Mailbox(
            self._rpc_manager.get_service_instance_mailbox_channel(
                self.service_name,
                self.service_uuid
            ),
            packer=self._rpc_manager.data_packer,
            url=self._rpc_manager.redis_url
        )

        self._return_mailbox = Mailbox(
            self._rpc_manager.get_client_mailbox_channel(
                self.service_name,
                self.service_uuid,
                self.client_uuid
            ),
            packer=self._rpc_manager.data_packer,
            url=self._rpc_manager.redis_url
        )
        self._return_mailbox.subscribe()

        self._return_rpc_data_cache = {}

    @property
    def service_name(self):
        return self._service_name

    @property
    def service_uuid(self):
        return self._service_uuid

    @property
    def client_uuid(self):
        return self._client_uuid

    def get_methods(self):
        return self._method_list

    def call_method(self, method_name, args, kwargs):
        rpc_uuid, expire_time = self.set_call_method_request(method_name, args, kwargs)
        rpc_data = self.get_call_method_result_with_uuid(rpc_uuid, expire_time)
        if rpc_data:

            return_value = rpc_data.get("return_value")
            exception = rpc_data.get("exception")

            if exception:
                raise exception

            return return_value

        else:
            raise TimeoutError(
                "call {mailbox_channel} method {method_name} failed".format(
                    mailbox_channel=self._request_mailbox.channel,
                    method_name=method_name
                )
            )

    def set_call_method_request(self, method_name, args, kwargs):
        rpc_uuid = self._rpc_manager.gen_rpc_uuid()
        request_time = self._rpc_manager.time
        expire_time = request_time + self._rpc_manager.RPC_EXPIRE
        rpc_data = {
            "rpc_uuid": rpc_uuid,

            "request_mailbox": self._request_mailbox.channel,
            "return_mailbox": self._return_mailbox.channel,

            "service_name": self.service_name,
            "service_uuid": self.service_uuid,

            "method_name": method_name,
            "args": args,
            "kwargs": kwargs,
            "return_value": None,
            "exception": None,

            "request_time": request_time,
            "expire_time": expire_time,
            "return_time": None,
        }

        self._request_mailbox.set_message(rpc_data)

        self._rpc_manager.increase_total_request(self.service_name, self.service_uuid)

        return rpc_uuid, expire_time

    def get_call_method_result_with_uuid(self, rpc_uuid, expire_time):

        while True:
            timeout = expire_time - self._rpc_manager.time

            # try cache
            rpc_data = self._return_rpc_data_cache.pop(rpc_uuid, None)

            if not rpc_data:
                if timeout > 0:
                    rpc_data = self._return_mailbox.get_message(timeout)
                else:
                    return None

            if rpc_data:
                return_rpc_data_uuid = rpc_data.get("rpc_uuid")
                if return_rpc_data_uuid == rpc_uuid:
                    return rpc_data
                elif return_rpc_data_uuid:
                    self._return_rpc_data_cache[return_rpc_data_uuid] = rpc_data

    def get_call_method_result_with_uuid_noblock(self, rpc_uuid):
        while True:
            # try cache
            rpc_data = self._return_rpc_data_cache.pop(rpc_uuid, None)

            if not rpc_data:
                rpc_data = self._return_mailbox.get_message()

            if rpc_data:
                return_rpc_data_uuid = rpc_data.get("rpc_uuid")
                if return_rpc_data_uuid == rpc_uuid:
                    return rpc_data
                elif return_rpc_data_uuid:
                    self._return_rpc_data_cache[return_rpc_data_uuid] = rpc_data
            else:
                return None

    def __getattr__(self, method_name):
        if self._method_list and method_name in self._method_list:
            return RPCClientMethod(self, method_name)
        raise AttributeError("type object '%s' has no attribute '%s'" % (self.__class__.__name__, method_name))

#
# class AsyncRPCClientMethod(object):
#     def __init__(self, client, method_name):
#         super(AsyncRPCClientMethod, self).__init__()
#         self._client = client
#         self._method_name = method_name
#
#     async def __call__(self, *args, **kwargs):
#         return await self._client.async_call_method(self._method_name, args, kwargs)
#
#
# class AsyncRPCClient(RPCClient):
#     ASYNC_GET_POLL_INTERVAL = 0.01
#
#     def __init__(self, service_name, service_uuid=None, rpc_manager=None):
#         super(AsyncRPCClient, self).__init__(service_name, service_uuid, rpc_manager)
#
#     async def async_call_method(self, method_name, args, kwargs):
#         rpc_uuid, expire_time = self.set_call_method_request(method_name, args, kwargs)
#
#         while True:
#
#             rpc_data = self.get_call_method_result_with_uuid_noblock(rpc_uuid)
#             if not rpc_data:
#                 if expire_time - self._rpc_manager.time < 0:
#                     raise TimeoutError(
#                         "call {mailbox_channel} method {method_name} failed".format(
#                             mailbox_channel=self._request_mailbox.channel,
#                             method_name=method_name
#                         )
#                     )
#                 await asyncio.sleep(self.ASYNC_GET_POLL_INTERVAL)
#                 continue
#
#             return_value = rpc_data.get("return_value")
#             exception = rpc_data.get("exception")
#
#             if exception:
#                 raise exception
#
#             return return_value
#
#     def __getattr__(self, method_name):
#         if self._method_list and method_name in self._method_list:
#             return AsyncRPCClientMethod(self, method_name)
#         raise AttributeError("type object '%s' has no attribute '%s'" % (self.__class__.__name__, method_name))
