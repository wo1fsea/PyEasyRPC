# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
    Huang Quanyong (wo1fSea)
    quanyongh@foxmail.com
Date:
    2019/7/29
Description:
    rpc_manager.py
----------------------------------------------------------------------------"""

import random
import uuid
from .singleton import Singleton
from .redis_collections.dict import Dict
from .redis_collections.set import Set
from .redis_collections.list import List
from .redis_collections.queue import Queue

from .rpc_data import DEFAULT_SERVICE_DATA


def generate_uuid():
    """
    generate a uuid
    :return: uuid
    """
    return str(uuid.uuid4())


class RPCManager(Singleton):
    """
    RPCManager
    """

    GROUP_KEY_PATTERN = "rpc_group[{group_name}]"
    SERVICE_TTL = 1.500  # s
    SERVICE_HEARTBEAT_INTERVAL = 0.500  # s

    @staticmethod
    def gen_service_uuid():
        return generate_uuid()

    @staticmethod
    def gen_rpc_uuid():
        return generate_uuid()

    @property
    def group_key(self):
        return self.GROUP_KEY_PATTERN.format(group_name=self._group_name)

    @property
    def service_list_key(self):
        return ".".join([self.group_key, "service_list"])

    def get_service_instance_list_key(self, service_name):
        return ".".join(
            [
                self.group_key,
                "service[{service_name}]".format(service_name=service_name),
                "instance_list"
            ]
        )

    def get_service_instance_list(self, service_name):
        service_instance_list_key = self.get_service_instance_list_key(service_name)
        service_instance_list = Set(service_instance_list_key, packer=self._data_packer, url=self._redis_url)
        return service_instance_list

    def get_service_instance_key(self, service_name, service_uuid):
        return ".".join(
            [
                self.group_key,
                "service[{service_name}]".format(service_name=service_name),
                "instance[{service_uuid}]".format(service_uuid=service_uuid)
            ]
        )

    def get_service_instance(self, service_name, service_uuid):
        service_instance_key = self.get_service_instance_key(service_name, service_uuid)
        return Dict(service_instance_key)

    def __init__(self, rpc_group_name="default_group", data_packer=None, redis_url=None):
        self._group_name = rpc_group_name
        self._data_packer = data_packer
        self._redis_url = redis_url

        self._service_list = Dict(
            self.service_list_key,
            packer=self._data_packer,
            url=redis_url
        )

    def register_service(self, service_name, method_list, enable_multi_instance=True):
        service_uuid = self.gen_service_uuid()

        service_data = self._service_list.get(service_name)
        service_instance_list = self.get_service_instance_list(service_name)

        if service_data and self.get_alive_service_instance(service_name):
            if not enable_multi_instance:
                raise TypeError("service instance already exist.")
            if method_list != service_data["method_list"]:
                raise TypeError("can not register same service with different methods.")
        else:
            service_instance_list_key = self.get_service_instance_list_key(service_name)
            self._service_list[service_name] = {
                "service_name": service_name,
                "method_list": method_list,

                "service_instance_list_id": service_instance_list_key,

                "register_time": self._service_list.time,
                "last_register_time": self._service_list.time
            }

            service_instance_list.clear()

        service_instance_list.add(service_uuid)

        service_instance_data = self.get_service_instance(service_name, service_uuid)
        service_instance_data.clear()
        service_instance_data.update(
            {
                "service_instance_id": service_uuid,
                "last_heartbeat_time": service_instance_data.time,

                "last_call_require_time": 0.,
                "last_call_return_time": 0.,

                "total_require": 0,
                "total_return": 0,
            }
        )

        return service_uuid

    def unregister_service(self, service_name, service_uuid):
        service_instance_list = self.get_service_instance_list(service_name)
        service_instance_list.discard(service_uuid)
        if not self.get_alive_service_instance(service_name):
            self._service_list.pop(service_name, None)

    def service_heartbeat(self, service_name, service_uuid):
        raise NotImplementedError()

    def get_alive_service_instance(self, service_name):
        service_instance_list = self.get_service_instance_list(service_name)
        deads = list(
            filter(
                lambda x: not self.check_service_instance_alive(service_name, x),
                service_instance_list
            )
        )
        if deads:
            service_instance_list.difference_update(deads)
        return service_instance_list

    def check_service_instance_alive(self, service_name, service_uuid):
        service_data = self.get_service_instance(service_name, service_uuid)
        if not service_data.exists:
            return False

        return service_data.time - service_data["last_heartbeat_time"] < self.SERVICE_TTL

    def check_service_instance_loss_rate(self, service_name, service_uuid):
        service_data = self.get_service_instance(service_name, service_uuid)
        if not service_data.exists or \
                service_data.time - service_data["last_heartbeat_time"] > self.SERVICE_TTL:
            return 1.1

        total_return = max(1., service_data["total_return"])
        total_require = max(1., service_data["total_require"])

        return 1 - 1. * total_return / total_require

    def get_services(self):
        return filter(self.get_alive_service_instance, self._service_list.keys())

    def get_service_instances(self, service_name):
        return self.get_alive_service_instance(service_name)

    def get_service_instance_low_loss(self, service_name):
        service_instance_list = self.get_service_instance_list(service_name)
        service_instances = sorted(
            service_instance_list,
            key=lambda x: self.check_service_instance_loss_rate(service_name, x)
        )
        if service_instances:
            return service_instances[0]
        else:
            return None

    def get_service_instance_random(self, service_name):
        instances = self.get_alive_service_instance(service_name)
        if not instances:
            return None
        else:
            return random.choice(list(instances))

    def get_method_list(self, service_name):
        if self.get_alive_service_instance(service_name):
            return self._service_list.get(service_name, {}).get("method_list", [])
        else:
            return []

    def call_method_by_service_name(self, service_name, method_name, args, kwargs):
        raise NotImplementedError()

    def call_method_by_service_uuid(self, service_uuid, method_name, args, kwargs):
        raise NotImplementedError()

    def get_call_method_result(self, rpc_uuid):
        raise NotImplementedError()

    def block_call_method_by_service_name(self, service_name, method_name, args, kwargs):
        raise NotImplementedError()

    def block_call_method_by_service_uuid(self, service_uuid, method_name, args, kwargs):
        raise NotImplementedError()

    async def async_call_method_by_service_name(self, service_name, method_name, args, kwargs):
        raise NotImplementedError()

    async def async_call_method_by_service_uuid(self, service_name, method_name, args, kwargs):
        raise NotImplementedError()

    def get_call_method_request(self, service_uuid, method_name):
        raise NotImplementedError()

    def set_call_method_result(self, rpc_uuid, result):
        raise NotImplementedError()
