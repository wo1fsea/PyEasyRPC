# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
    Huang Quanyong (wo1fSea)
    quanyongh@foxmail.com
Date:
    2019/7/31
Description:
    rpc_data.py
----------------------------------------------------------------------------"""

DEFAULT_RPC_DATA = {
    "rpc_uuid": None,

    "request_mailbox": None,
    "return_mailbox": None,

    "service_name": None,
    "service_uuid": None,

    "method_name": "",
    "args": [],
    "kwargs": {},
    "return_value": None,
    "exception": None,

    "request_time": None,
    "expire_time": None,
    "return_time": None,
}

DEFAULT_SERVICE_DATA = {
    "service_name": "",
    "method_list": [],
    "enable_multi_instance": True,

    "service_uuid_set_key": None,

    "register_time": None,
    "last_register_time": None
}

DEFAULT_SERVICE_INSTANCE_DATA = {
    "service_uuid": None,
    "last_heartbeat_time": None,

    "last_call_require_time": None,
    "last_call_return_time": None,

    "total_require": 0,
    "total_return": 0,
}
