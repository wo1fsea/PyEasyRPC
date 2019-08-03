# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
    Huang Quanyong (wo1fSea)
    quanyongh@foxmail.com
Date:
    2017/10/5
Description:
    mailbox.py
----------------------------------------------------------------------------"""

from .redis_object import DEFAULT_PACKER
from .. import redis_connection


class Mailbox(object):

    def __init__(self, channel, msg_handler=None, packer=None, url=None):
        super(Mailbox, self).__init__()
        if not packer:
            packer = DEFAULT_PACKER

        self._msg_handler = msg_handler
        self._channel = channel
        self._packer = packer
        self._redis = redis_connection.get_redis(url)
        self._pubsub = None
        self._thread = None

    def _raw_handler(self, raw_data):
        if raw_data["type"] in ("psubscribe", "subscribe"):
            return

        data = self._packer.unpack(raw_data["data"])
        self._msg_handler(data)

    def subscribe(self):
        if self._pubsub:
            return

        self._pubsub = self._redis.pubsub()
        if self._msg_handler:
            self._pubsub.subscribe(**{self._channel: self._raw_handler})
        else:
            self._pubsub.subscribe(self._channel)

        data = self.get_message()
        assert data is None

    def set_message(self, data):
        self._redis.publish(self._channel, self._packer.pack(data))

    def get_message(self, timeout=0):
        assert self._pubsub, "need subscribe before get_message"

        data = self._pubsub.get_message(timeout)
        while data and data["type"] in ("psubscribe", "subscribe"):
            data = self._pubsub.get_message(timeout)

        if data:
            return self._packer.unpack(data["data"])
        else:
            return data

    def run_in_background(self):
        assert self._msg_handler, "msg_handler must be set before run_in_background"
        self._thread = self._pubsub.run_in_thread()

    def stop_background_thread(self):
        if not self._thread:
            return
        self._thread.stop()
        self._thread = None
