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


def get_redis(url=None):
    if not url:
        url = DEFAULT_URL
    _redis = redis.Redis.from_url(url)
    return _redis
