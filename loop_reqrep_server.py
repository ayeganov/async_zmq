import asyncio
import functools

import zmq
import time
import sys

import async_zmq

def publisher(sock, loop):
    sock.send(b"I am alive!")
    loop.call_later(1, publisher, sock, loop)

if len(sys.argv) > 1:
    port =  sys.argv[1]

loop = asyncio.get_event_loop()
def on_recv(socket, msg):
    print("Received request:", msg)
    loop.call_later(1, socket.send, ("Back at ya!".encode()))

zmq_sock = async_zmq.SocketFactory.pub_socket("blabla",
                           loop=loop)
#zmq_sock.on_recv(functools.partial(on_recv, zmq_sock))

try:
    publisher(zmq_sock, loop)
    loop.run_forever()
except (SystemExit, KeyboardInterrupt):
    print("Exiting...")
