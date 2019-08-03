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
import threading

from .rpc_manager import RPCManager
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

    def __init__(self, service_name="", enable_multi_instance=True):
        self._rpc_manager = RPCManager()
        self._service_name = service_name
        self._service_uuid = None
        self._request_mailbox = None
        self._remote_methods = {}
        self._enable_multi_instance = enable_multi_instance

        for name in self.rpc_methods:
            method = getattr(self, name)
            self._remote_methods[name] = method

        self._register()

        self._is_background_running = False

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
            )
        )

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
            self._register()

    def start_background_running(self):
        self._is_background_running = True
        self.start_heartbeat()
        self.start_process()

    def stop_background_running(self):
        self._is_background_running = False
        self.stop_heartbeat()
        self.stop_process()

    def process(self):
        rpc_data = self._rpc_manager.get_call_method_request(self._request_mailbox)
        if rpc_data and rpc_data.get("rpc_uuid"):

            method_name = rpc_data["method_name"]
            args = rpc_data["args"]
            kwargs = rpc_data["kwargs"]

            return_value = None
            exception = None

            # TODO: not found method_name?
            method = self._remote_methods[method_name]

            try:
                return_value = method(*args, **kwargs)

            except Exception as ex:
                exception = ex

            rpc_data["return_value"] = return_value
            rpc_data["exception"] = exception
            rpc_data["return_time"] = self._rpc_manager.time

            self._rpc_manager.set_call_method_result(rpc_data)

    def _process_in_thread(self):
        raise NotImplementedError()

    def start_process(self):
        assert self._process_thread is None, "process thread is already running."
        self._process_thread = threading.Thread(target=self._process_in_thread)
        self._process_thread.start()

    def stop_process(self):
        assert self._process_thread is not None, "process thread is not running."
        self._process_thread.join()
        self._process_thread = None

    def _heartbeat_in_thread(self):
        raise NotImplementedError()

    def start_heartbeat(self):
        assert self._process_thread is None, "heartbeat thread is already running."
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_in_thread)
        self._heartbeat_thread.start()

    def stop_heartbeat(self):
        assert self._heartbeat_thread is not None, "heartbeat thread is not running."
        self._heartbeat_thread.join()
        self._heartbeat_thread = None
