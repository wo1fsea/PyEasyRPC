# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
    Huang Quanyong (wo1fSea)
    quanyongh@foxmail.com
Date:
    2017/10/5
Description:
    db_connection.py
----------------------------------------------------------------------------"""

import time
import redis

DEFAULT_URL = "redis://localhost:6379/0"
DELTA_TIME = {}
REDIS_POOLS = {}


def get_redis(url=None):
    if not url:
        url = DEFAULT_URL
    redis_ = REDIS_POOLS.get(url)
    if not redis_:
        redis_ = redis.Redis.from_url(url)
        REDIS_POOLS[url] = redis_
    return redis_


def get_time(url=None):
    if not url:
        url = DEFAULT_URL

    delta_time = DELTA_TIME.get(url, None)

    if delta_time is None:
        redis_time = float("%d.%d" % get_redis(url).time())
        delta_time = redis_time - time.time()
        DELTA_TIME[url] = delta_time
        return redis_time

    return delta_time + time.time()
