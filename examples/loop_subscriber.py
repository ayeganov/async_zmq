'''
An example of usage of the subscriber socket.
'''

import asyncio
import pickle

import async_zmq

@asyncio.coroutine
def on_recv(msgs):
    '''
    Receiver function.
    '''
    msg_dict = pickle.loads(msgs[-1])
    print("Received msg:", msg_dict)

def subscriber():
    '''
    This is the main function of this program.
    '''
    try:
        loop = asyncio.get_event_loop()
        zmq_sock = async_zmq.SocketFactory.sub_socket(host="localhost",
                                                      port=55555,
                                                      transport="tcp",
                                                      loop=loop)
        zmq_sock.on_recv(on_recv)

        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        print("Exiting...")
