'''
An example of usage of the subscriber socket.
'''

import asyncio

import async_zmq

@asyncio.coroutine
def on_recv(msgs):
    '''
    Receiver function.
    '''
    print("Received msg:", msgs[0].decode())

def subscriber():
    '''
    This is the main function of this program.
    '''
    try:
        loop = asyncio.get_event_loop()
        zmq_sock = async_zmq.SocketFactory.sub_socket("blabla", loop=loop)
        zmq_sock.on_recv(on_recv)

        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        print("Exiting...")
