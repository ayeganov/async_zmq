'''
An example of usage of the publisher socket.
'''

import asyncio
import time

import pickle

import async_zmq

NUM_MSG = 1000

loop = asyncio.get_event_loop()

counter = 0
def do_publish(sock, loop):
    '''
    Continious publisher.
    '''
    global counter
    d = {"count":counter}
    ds = pickle.dumps(d)
    sock.send(ds)
    if counter < NUM_MSG:
        loop.call_soon(do_publish, sock, loop)
        counter += 1

@asyncio.coroutine
def on_send(msgs):
    '''
    Gets called when publisher sends a message.
    '''
    msgd = pickle.loads(msgs[-1])
    count = msgd['count']
    if count >= NUM_MSG:
        loop.stop()


def publisher():
    '''
    This is the main function of this program.
    '''
    try:
        zmq_sock = async_zmq.SocketFactory.pub_socket(host='*',
                                                      port=55555,
                                                      transport="tcp",
                                                      on_send=on_send,
                                                      loop=loop)
        # Sleep a litle to let `bind` take proper effect.  In production
        # environment most likely the socket will have more than enough time to
        # bind, so this should not be an issue
        time.sleep(0.5)
        start = time.time()
        do_publish(zmq_sock, loop)
        loop.run_forever()
        print("Sending took %s seconds" % (time.time() - start))
    except (SystemExit, KeyboardInterrupt):
        print("Exiting...")

