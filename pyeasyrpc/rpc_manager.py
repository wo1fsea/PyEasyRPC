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
import shortuuid
from .singleton import Singleton
from . import redis_connection

from .redis_collections.dict import Dict
from .redis_collections.set import Set
from .redis_collections.list import List
from .redis_collections.queue import Queue
from .redis_collections.mailbox import Mailbox

from .rpc_data import DEFAULT_SERVICE_DATA


def generate_uuid():
    """
    generate a uuid
    :return: uuid
    """
    return str(shortuuid.uuid())


class RPCManager(object):
    """
    RPCManager
    """

    GROUP_KEY_PATTERN = "rpc_group[{group_name}]"
    SERVICE_TTL = 1.000  # s
    SERVICE_HEARTBEAT_INTERVAL = 0.100  # s
    RPC_EXPIRE = 1.000  # s

    @staticmethod
    def gen_service_uuid():
        return generate_uuid()

    @staticmethod
    def gen_client_uuid():
        return generate_uuid()

    @staticmethod
    def gen_rpc_uuid():
        return generate_uuid()

    def __init__(self, rpc_group_name="default_group", data_packer=None, redis_url=None):
        self._group_name = rpc_group_name
        self._data_packer = data_packer
        self._redis_url = redis_url

        self._service_dict = Dict(
            self.service_dict_key,
            packer=self._data_packer,
            url=redis_url
        )

    @property
    def data_packer(self):
        return self._data_packer

    @property
    def redis_url(self):
        return self._redis_url

    @property
    def time(self):
        return redis_connection.get_time(self._redis_url)

    @property
    def group_key(self):
        return self.GROUP_KEY_PATTERN.format(group_name=self._group_name)

    @property
    def service_dict_key(self):
        return ".".join([self.group_key, "service_dict"])

    def get_service_uuid_set_key(self, service_name):
        return ".".join(
            [
                self.group_key,
                "service[{service_name}]".format(service_name=service_name),
                "instance_list"
            ]
        )

    def get_service_uuid_set(self, service_name):
        service_uuid_set_key = self.get_service_uuid_set_key(service_name)
        service_uuid_set = Set(service_uuid_set_key, packer=self._data_packer, url=self._redis_url)
        return service_uuid_set

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

    def get_service_instance_mailbox_channel(self, service_name, service_uuid):
        return ".".join(
            [
                self._group_name,
                service_name,
                service_uuid
            ]
        )

    def get_client_mailbox_channel(self, service_name, service_uuid, client_uuid):
        return ".".join(
            [
                self._group_name,
                service_name,
                service_uuid,
                client_uuid
            ]
        )

    def register_service(self, service_name, method_list, enable_multi_instance=True):
        service_uuid = self.gen_service_uuid()

        service_data = self._service_dict.get(service_name)
        service_uuid_set = self.get_service_uuid_set(service_name)

        if service_data and self.get_alive_service_uuid_set(service_name):
            if not enable_multi_instance or not service_data["enable_multi_instance"]:
                raise TypeError("service instance already exist.")
            if method_list != service_data["method_list"]:
                raise TypeError("can not register same service with different methods.")

            service_data["last_register_time"] = self.time
        else:
            service_uuid_set_key = self.get_service_uuid_set_key(service_name)
            self._service_dict[service_name] = {
                "service_name": service_name,
                "method_list": sorted(method_list),
                "enable_multi_instance": enable_multi_instance,

                "service_uuid_set_key": service_uuid_set_key,

                "register_time": self.time,
                "last_register_time": self.time
            }

            service_uuid_set.clear()

        service_uuid_set.add(service_uuid)

        # init service data
        service_instance = self.get_service_instance(service_name, service_uuid)
        service_instance.clear()
        service_instance.update(
            {
                "service_name": service_name,
                "service_uuid": service_uuid,
                "last_heartbeat_time": self.time,

                "last_call_require_time": 0.,
                "last_call_return_time": 0.,
            }
        )

        service_instance.set_raw("total_require", 0)
        service_instance.set_raw("total_return", 0)

        return service_uuid

    def unregister_service(self, service_name, service_uuid):
        service_instance = self.get_service_instance(service_name, service_uuid)
        service_instance.clear()

        service_uuid_set = self.get_service_uuid_set(service_name)
        service_uuid_set.discard(service_uuid)

        if not self.get_alive_service_uuid_set(service_name):
            self._service_dict.pop(service_name, None)

    def service_heartbeat(self, service_name, service_uuid):
        if service_uuid not in self.get_service_uuid_set(service_name):
            self.get_service_instance(service_name, service_uuid).clear()
            return False

        service_instance = self.get_service_instance(service_name, service_uuid)
        if not service_instance.exists:
            self.get_service_uuid_set(service_name).discard(service_uuid)
            return False

        service_instance["last_heartbeat_time"] = self.time
        return True

    def get_alive_service_uuid_set(self, service_name):
        service_uuid_set = self.get_service_uuid_set(service_name)
        deads = list(
            filter(
                lambda x: not self.check_service_instance_alive(service_name, x),
                service_uuid_set
            )
        )
        if deads:
            service_uuid_set.difference_update(deads)
            for service_uuid in deads:
                service_instance = self.get_service_instance(service_name, service_uuid)
                service_instance.clear()

        return service_uuid_set

    def check_service_instance_alive(self, service_name, service_uuid):
        service_instance = self.get_service_instance(service_name, service_uuid)
        if not service_instance.exists:
            return False

        return self.time - service_instance.get("last_heartbeat_time", 0) < self.SERVICE_TTL

    def check_service_instance_loss_rate(self, service_name, service_uuid):
        service_instance = self.get_service_instance(service_name, service_uuid)
        if not service_instance.exists or \
                self.time - service_instance.get("last_heartbeat_time", 0) > self.SERVICE_TTL:
            return 1.1

        total_return = max(1., float(service_instance.get_raw("total_return")))
        total_require = max(1., float(service_instance.get_raw("total_require")))

        return 1 - total_return / total_require

    def get_service_list(self):
        return list(filter(self.get_alive_service_uuid_set, self._service_dict.keys()))

    def get_alive_service_uuid_low_loss(self, service_name):
        service_uuid_set = self.get_alive_service_uuid_set(service_name)
        service_uuid_set = sorted(
            service_uuid_set,
            key=lambda x: self.check_service_instance_loss_rate(service_name, x)
        )
        if service_uuid_set:
            return service_uuid_set[0]
        else:
            return None

    def get_alive_service_uuid_random(self, service_name):
        uuids = self.get_alive_service_uuid_set(service_name)
        if not uuids:
            return None
        else:
            return random.choice(list(uuids))

    def get_method_list(self, service_name):
        if self.get_alive_service_uuid_set(service_name):
            return self._service_dict.get(service_name, {}).get("method_list", [])
        else:
            return []

    def increase_total_request(self, service_name, service_uuid):
        service_instance = self.get_service_instance(service_name, service_uuid)
        if service_instance.exists:
            service_instance.increase_by("total_require", 1)

    def increase_total_return(self, service_name, service_uuid):
        service_instance = self.get_service_instance(service_name, service_uuid)
        if service_instance.exists:
            service_instance.increase_by("total_return", 1)


class DefaultRPCManager(RPCManager, Singleton):
    """
    DefaultRPCManager
    """


assert DefaultRPCManager() is DefaultRPCManager()
