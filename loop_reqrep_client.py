import asyncio
import functools

import zmq
import sys

import async_zmq

port = "loop_reqrep"
if len(sys.argv) > 1:
    port =  sys.argv[1]

counter = 0
loop = asyncio.get_event_loop()
def on_recv(socket, msg):
    global counter
    print("Received reply:", msg)
    if counter < 10:
        socket.send("more requests".encode())
        counter += 1
    else:
        loop.stop()


#context = zmq.Context()
#print("Connecting to server...")
#socket = context.socket(zmq.REQ)
#socket.connect ("ipc:///tmp/%s" % port)

zmq_sock = async_zmq.SocketFactory.req_socket("blabla",
                           loop=loop)
zmq_sock.on_recv(functools.partial(on_recv, zmq_sock))

zmq_sock.send ("Hello".encode())

try:
    loop.run_forever()
except (KeyboardInterrupt, SystemExit):
    print("Exiting...")
