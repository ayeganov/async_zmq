#!/usr/bin/env python3.4

import asyncio


@asyncio.coroutine
def open_connection():
    con = yield from asyncio.open_unix_connection("/tmp/test_con")
    return con

def main():
    loop = asyncio.get_event_loop()
    con = loop.run_until_complete(open_connection())

    print(con)
    loop.run_forever()

if __name__ == "__main__":
    main()
