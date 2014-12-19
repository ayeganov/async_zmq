#!/usr/bin/env python3.4

import asyncio


def new_connection(*args):
    print("New connection")
    print(args)

@asyncio.coroutine
def create_server(loop):
    print(4)
    con = yield from asyncio.start_unix_server(new_connection, "/tmp/test_con")
    print(con)

def main():
    print(1)
    loop = asyncio.get_event_loop()
    print(2)
    result = loop.run_until_complete(create_server(loop))
    print(3)
    print(result)
    loop.run_forever()

if __name__ == "__main__":
    print("wtf")
    main()
