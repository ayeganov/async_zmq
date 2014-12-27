import asyncio
import logging
import collections


import zmq

log = logging.getLogger(__name__)

class AIOZMQSocket:
    '''
    This class provides the asynchronous functionality to ZMQ sockets.
    '''

    def __init__(self, socket, loop=None):
        '''
        Initializes the AsyncZMQ instance.

        @param socket - ZMQ socket to use with AsyncIO loop.
        @param loop - asyncio loop
        '''
        self._socket = socket
        self._loop = asyncio.get_event_loop() if loop is None else loop

        # Start paying attention to recv events
        self._poller = zmq.Poller()
        self._poller.register(self._socket, zmq.POLLIN)

        # As soon as loop starts we need to poll for data
        self._poll_handle = self._loop.call_soon(self._poll_socket)
        self._on_send_callback = None
        self._on_recv_callback = None
        self._send_queue = collections.deque()

    @property
    def is_closed(self):
        '''
        Returns true if this socket is closed, false otherwise.
        '''
        return (self._socket is not None)

    def on_recv(self, on_recv):
        '''
        Register a callback for handling incoming data on this socket.

        @param on_recv - function to be invoked to handle received data
        '''
        self._on_recv_callback = on_recv

    def on_send(self, on_send):
        '''
        Register a callback for handling incoming data on this socket.

        @param on_send - function to be invoked when data is being sent on this
                         socket.
        '''
        self._on_send_callback = on_send

    def _poll_socket(self):
        '''
        Polls the zmq socket for incoming data. If new data is available
        triggers the callbacks.
        '''
        events = self._poller.poll(0)
        while events:
            socket, event = events.pop(0)

            # Data available for reception
            if event & zmq.POLLIN:
                self._handle_on_recv()
                if self._socket is None:
                    # Socket was closed after this call, get out of here
                    break

            # Can send and have data to send
            if (event & zmq.POLLOUT) and self.sending:
                self._handle_on_send()
                if self._socket is None:
                    # Socket was closed after this call, get out of here
                    break

        # Restart polling
        self._poll_handle = self._loop.call_soon(self._poll_socket)

    def _handle_on_send(self):
        '''
        Hadles the pending message to be sent across this socket.
        '''
        msg = self._send_queue.popleft()
        try:
            status = self._socket.send_multipart(msg)
        except zmq.ZMQError as e:
            log.exception("Send error: %s" % zmq.strerror(e.errno))
        if self._on_send_callback is not None:
            self._on_send_callback(msg, status)

    def _handle_on_recv(self):
        '''
        Hanldes the pending received messages on this socket.
        '''
        try:
            msgs = self._socket.recv_multipart(zmq.NOBLOCK)
        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                # state changed since poll event
                pass
            else:
                log.exception("Recv error: %s" % zmq.strerror(e.errno))

        if self._on_recv_callback is not None:
            self._on_recv_callback(msgs)

    @property
    def sending(self):
        '''
        Flag indicating whether there are messages to be sent on this socket.
        '''
        return not self._send_queue.empty()

    def send(self, msg):
        '''
        Send data on this socket.
        '''
        try:
            self._send_queue.append([msg])
            status = self._socket.send_multipart([msg])
        except zmq.ZMQError as e:
            log.exception("Send error: %s" % zmq.strerror(e.errno))

    def close(self):
        '''
        Closes this socket, and makes it unusable thereafter.
        '''
        if self._socket is not None:
            self._poll_handle.cancel()
            self._socket.close()
            self._socket = None

