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

from collections import UserList
from .redis_object import RedisObject


class List(RedisObject, UserList):
    Redis_Type = "list"

    def __init__(self, key, packer=None, url=None):
        super(List, self).__init__(key, packer, url)

    def __get_data(self):
        return map(self.unpack, self._redis.lrange(self.key, 0, -1))

    def __cast(self, other):
        return tuple(other)

    @property
    def data(self):
        return list(self.__get_data())

    def __contains__(self, item):
        return item in self.data

    def __len__(self):
        return self._redis.llen(self.key)

    def __getitem__(self, i):
        if isinstance(i, slice):
            return self.data[i]

        item = self._redis.lindex(self.key, i)
        if item:
            item = self.unpack(item)
        return item

    def __setitem__(self, i, item):
        packed = self.pack(item)
        self._redis.lset(self.key, i, packed)

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
        self._redis.rpush(self._key, item)

    def insert(self, i, item):
        data = list(self.__get_data())
        data.insert(i, item)
        self.clear()
        if data:
            self._redis.rpush(self._key, *map(self.pack, data))

    def pop(self, i=-1):
        data = list(self.__get_data())
        item = data.pop(i)
        self.clear()
        if data:
            self._redis.rpush(self._key, *map(self.pack, data))

        return item

    def remove(self, item):
        data = list(self.__get_data())
        data.remove(item)
        self.clear()
        if data:
            self._redis.rpush(self._key, *map(self.pack, data))

    def copy(self):
        return self.data

    def count(self, item):
        return self.data.count(self.pack(item))

    def index(self, item, *args):
        return self.data.index(item, *args)

    def reverse(self):
        data = list(self.__get_data())
        data.reverse()
        self.clear()
        if data:
            self._redis.rpush(self._key, *map(self.pack, data))

    def sort(self, *args, **kwds):
        data = list(self.__get_data())
        data.sort(*args, **kwds)
        self.clear()
        if data:
            self._redis.rpush(self._key, *map(self.pack, data))

    def extend(self, other):
        if other:
            self._redis.rpush(self._key, *map(self.pack, other))
