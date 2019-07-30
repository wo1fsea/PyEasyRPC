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

import redis

DEFAULT_URL = "redis://localhost:6379/0"

_redis = None


def get_redis():
    global _redis

    if not _redis:
        _redis = redis.StrictRedis.from_url(url=DEFAULT_URL)

    return _redis
