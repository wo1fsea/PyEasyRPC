# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
    Huang Quanyong (wo1fSea)
    quanyongh@foxmail.com
Date:
    2017/10/6
Description:
    table.py
----------------------------------------------------------------------------"""

from collections import UserDict
from .redis_object import RedisObject


class Dict(RedisObject, UserDict):
    Redis_Type = "hash"

    def __init__(self, key, packer=None, url=None):
        super(Dict, self).__init__(key, packer, url)

        # assert self.get_type() in (self.Redis_Type, RedisObject.Redis_Type), "Wrong Redis Object Type"

    @property
    def data(self):
        return dict(self.items())

    def __len__(self):
        return self._redis.hlen(self.key)

    def __getitem__(self, key):
        b_key = self.pack(key)
        b_item = self._redis.hget(self.key, b_key)
        if not b_item:
            raise KeyError(key)
        return self.unpack(b_item)

    def __setitem__(self, key, value):
        b_key = self.pack(key)
        b_item = self.pack(value)
        self._redis.hset(self.key, b_key, b_item)

    def __delitem__(self, key):
        b_key = self.pack(key)
        if not self._redis.hdel(self.key, b_key):
            raise KeyError(key)

    def __iter__(self):
        return iter(self.keys())

    def __contains__(self, key):
        b_key = self.pack(key)
        return self._redis.hexists(self.key, b_key)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self):
        return map(self.unpack, self._redis.hkeys(self.key))

    def items(self):
        return map(lambda x: (self.unpack(x[0]), self.unpack(x[1])), self._redis.hgetall(self.key).items())

    def values(self):
        return map(self.unpack, self._redis.hvals(self.key))

    def setdefault(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            self[key] = default
        return default

    def copy(self):
        return self.data

    # 4 redis hash
    def get_raw(self, key):
        return self._redis.hget(self.key, self.pack(key))

    def set_raw(self, key, value):
        self._redis.hset(self.key, self.pack(key), value)

    def increase_by(self, key, value):
        if isinstance(value, int):
            self._redis.hincrby(self.key, self.pack(key), value)
        elif isinstance(value, float):
            self._redis.hincrbyfloat(self.key, self.pack(key), value)
        else:
            raise TypeError()
