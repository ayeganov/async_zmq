import zmq
import time
import sys

port = "5556"
if len(sys.argv) > 1:
    port =  sys.argv[1]
    int(port)
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("ipc:///tmp/reqrep")

print("My package is", __package__)
while True:
    #  Wait for next request from client
    message = socket.recv()
    print("Received request: ", message)
    socket.send("World from %s" % port)
#    time.sleep (1)

