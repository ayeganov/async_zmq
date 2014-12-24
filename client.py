#!/usr/bin/env python3

import asyncio


@asyncio.coroutine
def tcp_echo_client(message, loop):
    reader, writer = yield from asyncio.open_unix_connection('/tmp/test_con',
                                                        loop=loop)

    print('Send: %r' % message)
    writer.write(message.encode())

    data = yield from reader.read(100)
    print('Received: %r' % data.decode())

    print('Close the socket')
    writer.close()

def echo_wrapper(loop, message):
    asyncio.async(tcp_echo_client(message, loop))
    loop.call_later(1.0, echo_wrapper, loop, message)

def main():
    message = 'Hello World!'
    loop = asyncio.get_event_loop()
    print("Loop", loop)
    try:
        loop.call_soon(echo_wrapper, loop, message)
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    loop.close()


if __name__ == "__main__":
    main()
