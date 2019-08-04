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

from pyeasyrpc.rpc import RPCClient


def main():
    client = RPCClient("ServiceInstance")
    print("method_list", client.get_methods())

    print("add", client.add(1, 2))
    print("sub", client.sub(100, 1.1))
    print("make_dict", client.make_dict(a=1, b=2, c=3))
    print("make_list", client.make_list(1, [2], {3}))

    try:
        client.add()
    except Exception as ex:
        print(type(ex), ex)


if __name__ == '__main__':
    main()
