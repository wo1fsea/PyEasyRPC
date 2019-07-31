# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
    Huang Quanyong (wo1fSea)
    quanyongh@foxmail.com
Date:
    2017/10/29
Description:
    redis_object.py
----------------------------------------------------------------------------"""

import time
import msgpack
import _pickle as pickle

from .. import redis_connection

_delta_time = None


class Packer(object):
    @staticmethod
    def pack(obj):
        raise NotImplementedError()

    @staticmethod
    def unpack(packed):
        raise NotImplementedError()


class NoPacker(object):
    @staticmethod
    def pack(obj):
        return obj

    @staticmethod
    def unpack(packed):
        return packed


class MsgPacker(Packer):
    @staticmethod
    def pack(obj):
        return msgpack.packb(obj)

    @staticmethod
    def unpack(packed):
        return msgpack.unpackb(packed, raw=False)


class PicklePacker(Packer):
    @staticmethod
    def pack(obj):
        return pickle.dumps(obj)

    @staticmethod
    def unpack(packed):
        return pickle.loads(packed)


DEFAULT_PACKER = PicklePacker


class RedisObject(object):
    Redis_Type = "none"
    _delta_time = {}

    def __init__(self, key, packer=None, url=None):
        if not packer:
            packer = DEFAULT_PACKER

        self._key = key
        self._packer = packer
        self._redis = redis_connection.get_redis(url)

    def get_type(self):
        return self._redis.type(self._key).decode()

    def set_expire(self, milliseconds):
        self._redis.pexpire(self._key, milliseconds)

    @property
    def exists(self):
        return self._redis.exists(self._key)

    @property
    def time(self):
        delta_time = self._delta_time.get(self._redis, None)
        if delta_time is None:
            local_time = time.time()
            redis_time = float("%d.%d" % self._redis.time())
            delta_time = redis_time - local_time
            self._delta_time[self._redis] = delta_time
        return delta_time + time.time()

    @property
    def key(self):
        return self._key

    def clear(self):
        self._redis.delete(self.key)

    def pack(self, obj):
        return self._packer.pack(obj)

    def unpack(self, packed):
        return self._packer.unpack(packed)
