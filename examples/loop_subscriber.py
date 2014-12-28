import asyncio
import functools

import async_zmq

loop = asyncio.get_event_loop()
def on_recv(socket, msg):
    print("Received msg:", msg)

def subscriber():
    try:
        zmq_sock = async_zmq.SocketFactory.sub_socket("blabla", loop=loop)
        zmq_sock.on_recv(functools.partial(on_recv, zmq_sock))

        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        print("Exiting...")
