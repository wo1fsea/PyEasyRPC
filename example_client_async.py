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

import asyncio
from pyeasyrpc.rpc import AsyncRPCClient


def main():
    client = AsyncRPCClient("ServiceInstance")
    print("method_list", client.get_methods())

    async def add():
        print("add", await client.add(1, 2))

    async def sub():
        print("sub", await client.sub(100, 1.1))

    async def make_dict():
        print("make_dict", await client.make_dict(a=1, b=2, c=3))

    async def make_list():
        print("make_list", await client.make_list(1, [2], {3}))

    async def catch_exception():
        try:
            await client.add()
        except Exception as ex:
            print(type(ex), ex)

    async def func():
        task = [add(), sub(), make_list(), make_dict(), catch_exception()]
        # task.extend([add() for i in range(100)])
        # task.extend([sub() for i in range(100)])
        # task.extend([make_list() for i in range(100)])
        # task.extend([make_dict() for i in range(100)])
        # task.extend([catch_exception() for i in range(100)])
        await asyncio.wait(task)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(func())


if __name__ == '__main__':
    main()
