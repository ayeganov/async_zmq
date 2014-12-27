import asyncio
import functools

import zmq
import time
import sys

import async_zmq

port = "loop_reqrep"

if len(sys.argv) > 1:
    port =  sys.argv[1]

def on_recv(socket, msg):
    print("Received request:", msg)
    socket.send("Back at ya!".encode())

#context = zmq.Context()
#socket = context.socket(zmq.REP)
#socket.bind("ipc:///tmp/%s" % port)

loop = asyncio.get_event_loop()
zmq_sock = async_zmq.SocketFactory.rep_socket("blabla",
                           loop=loop)
zmq_sock.on_recv(functools.partial(on_recv, zmq_sock))

try:
    loop.run_forever()
except (SystemExit, KeyboardInterrupt):
    print("Exiting due to system interrup")
