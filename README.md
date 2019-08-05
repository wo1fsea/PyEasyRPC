# PyEasyRPC
[![Build Status](https://travis-ci.com/wo1fsea/PyEasyRPC.svg?branch=master)](https://travis-ci.com/wo1fsea/PyEasyRPC)
[![codecov](https://codecov.io/gh/wo1fsea/PyEasyRPC/branch/master/graph/badge.svg)](https://codecov.io/gh/wo1fsea/PyEasyRPC)

PyEaseRPC is a Python RPC framework easy to use, which using Redis as backend.

## Example
### Server

```
# example_server.py
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
    instance0 = ServiceInstance(process_request_in_thread=True)
    instance0.start_background_running()

    input("press any key to stop")

    instance0.stop_background_running()


if __name__ == '__main__':
    main()

```

## Client

```
# example_client.py
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
```

### Async Client

```
# example_client_async.py

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
```