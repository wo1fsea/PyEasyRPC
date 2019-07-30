# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
    Huang Quanyong (wo1fSea)
    quanyongh@foxmail.com
Date:
    2017/10/5
Description:
    queue.py
----------------------------------------------------------------------------"""

from .redis_object import RedisObject, DEFAULT_PACKER

QUEUE_MAX_LENGTH = -1


class Queue(RedisObject):
    Redis_Type = "list"

    def __init__(self, key, max_len=QUEUE_MAX_LENGTH, packer=DEFAULT_PACKER, url=None):
        super(Queue, self).__init__(key, packer, url)
        self.max_len = max_len

    def put(self, item):
        item = self.pack(item)
        self._redis.lpush(self.key, item)
        if self.max_len > 0:
            self._redis.ltrim(self.key, 0, self.max_len)

    def get(self):
        item = self._redis.rpop(self.key)
        item = self.unpack(item) if item else item
        return item

    def bget(self, timeout=0):
        b_items = self._redis.brpop(self.key, timeout)
        if not b_items:
            return None

        b_item = b_items[1]
        item = self.unpack(b_item) if b_item else b_item
        return item

    def clear(self):
        self._redis.delete(self.key)
