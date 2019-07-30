# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
    Huang Quanyong (wo1fSea)
    quanyongh@foxmail.com
Date:
    2018/1/14
Description:
    list.py
----------------------------------------------------------------------------"""

from .redis_object import RedisObject, DEFAULT_PACKER
from collections import UserList


class List(RedisObject, UserList):
    Redis_Type = "list"

    def __init__(self, key, packer=DEFAULT_PACKER):
        super(List, self).__init__(key, packer)

    def __get_data(self):
        return map(self.unpack, self.redis.lrange(self.key, 0, -1))

    def __cast(self, other):
        return tuple(other)

    @property
    def data(self):
        return tuple(self.__get_data())

    def __contains__(self, item):
        return item in self.data

    def __len__(self):
        return self.redis.llen(self.key)

    def __getitem__(self, i):
        if isinstance(i, slice):
            return self.data[i]

        item = self.redis.lindex(self.key, i)
        if item:
            item = self.unpack(item)
        return item

    def __setitem__(self, i, item):
        packed = self.pack(item)
        self.redis.lset(self.key, i, packed)

    def __delitem__(self, i):
        raise NotImplementedError()

    def __add__(self, other):
        raise NotImplementedError()

    def __radd__(self, other):
        raise NotImplementedError()

    def __iadd__(self, other):
        self.extend(other)
        return self

    def __mul__(self, n):
        raise NotImplementedError()

    __rmul__ = __mul__

    def __imul__(self, n):
        self.extend(self.data * (n - 1))
        return self

    def append(self, item):
        item = self.pack(item)
        self.redis.rpush(self._key, item)

    def insert(self, i, item):
        data = list(self.__get_data())
        data.insert(i, item)
        self.clear()
        self.redis.rpush(self._key, *data)

    def pop(self, i=-1):
        data = list(self.__get_data())
        item = data.pop(i)
        self.clear()
        self.redis.rpush(self._key, *data)

        return item

    def remove(self, item):
        data = list(self.__get_data())
        data.remove(item)
        self.clear()
        self.redis.rpush(self._key, *data)

    def copy(self):
        raise NotImplementedError()

    def count(self, item):
        return self.data.count(item)

    def index(self, item, *args):
        return self.data.index(item, *args)

    def reverse(self):
        data = list(self.__get_data())
        data.reverse()
        self.clear()
        self.redis.rpush(self._key, *data)

    def sort(self, *args, **kwds):
        data = list(self.__get_data())
        data.sort(*args, **kwds)
        self.clear()
        self.redis.rpush(self._key, *data)

    def extend(self, other):
        self.redis.rpush(self._key, *other)
