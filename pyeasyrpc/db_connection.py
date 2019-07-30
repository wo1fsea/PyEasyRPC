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

from ..config_reader import ConfigReader

_redis = None


def get_redis():
    global _redis

    if not _redis:
        config_reader = ConfigReader()
        redis_config = config_reader.get_config("redis")
        assert redis_config, "redis config not exists."
        _redis = redis.StrictRedis(**redis_config)

    return _redis
