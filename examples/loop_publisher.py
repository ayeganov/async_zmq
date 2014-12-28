import asyncio
import functools
import time

import async_zmq

NUM_MSG = 100

loop = asyncio.get_event_loop()

counter = 0
def do_publish(sock, loop):
    global counter
    sock.send(("%s" % counter).encode())
    if counter < NUM_MSG:
        loop.call_soon(do_publish, sock, loop)
        counter += 1

def on_send(msgs):
    msg = msgs[-1].decode()
    if int(msg) >= NUM_MSG:
        loop.stop()


def publisher():
    try:
        zmq_sock = async_zmq.SocketFactory.pub_socket("blabla",
                                                      on_send=on_send,
                                                      loop=loop)
        # Sleep a litle to let `bind` take proper effect.
        # In production environment most likely the socket will have more than
        # enough time to bind, so this should not be an issue
        time.sleep(0.5)
        start = time.time()
        do_publish(zmq_sock, loop)
        loop.run_forever()
        print("Sending took %s seconds" % (time.time() - start))
    except (SystemExit, KeyboardInterrupt):
        print("Exiting...")


if __name__ == "__main__":
    main_pub()
