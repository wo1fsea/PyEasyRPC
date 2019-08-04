# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
    Huang Quanyong (wo1fSea)
    quanyongh@foxmail.com
Date:
    2019/8/4
Description:
    example.py
----------------------------------------------------------------------------"""

from pyeasyrpc.rpc import remote_method
from pyeasyrpc.rpc import RPCService


class ServiceInstance(RPCService):
    @remote_method
    def add(self, a, b):
        return a + b

    @remote_method
    def sub(self, a, b):
        return a - b

    @remote_method
    def make_dict(self, **kwargs):
        return dict(kwargs)

    @remote_method
    def make_list(self, *args):
        return list(args)


def main():
    instance0 = ServiceInstance()
    instance0.start_background_running()

    input("press any key to stop")

    instance0.stop_background_running()


if __name__ == '__main__':
    main()
