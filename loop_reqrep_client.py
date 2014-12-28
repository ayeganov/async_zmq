import asyncio
import functools

import zmq
import sys

import async_zmq

if len(sys.argv) > 1:
    port =  sys.argv[1]

counter = 0
loop = asyncio.get_event_loop()
def on_recv(socket, msg):
    global counter
    print("Received msg:", msg)
#    if counter < 10:
#        socket.send(b"more requests")
#        counter += 1
#    else:
#        loop.stop()


zmq_sock = async_zmq.SocketFactory.sub_socket("blabla",
                           loop=loop)
zmq_sock.on_recv(functools.partial(on_recv, zmq_sock))

#zmq_sock.send ("Hello".encode())

try:
    loop.run_forever()
except (KeyboardInterrupt, SystemExit):
    print("Exiting...")
