import asyncio
import collections
import logging
import os

import zmq

logging.basicConfig()
log = logging.getLogger(__name__)

class AIOZMQSocket:
    '''
    This class provides the asynchronous functionality to ZMQ sockets.
    '''

    def __init__(self, socket, loop=None):
        '''
        Initializes the AIOZMQSocket instance.

        @param socket - ZMQ socket to use with AsyncIO loop.
        @param loop - asyncio loop
        '''
        self._socket = socket
        self._loop = asyncio.get_event_loop() if loop is None else loop

        # Start paying attention to recv events
        self._poller = zmq.Poller()
        self._poller.register(self._socket, zmq.POLLIN | zmq.POLLOUT)

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
        self._poll_handle = self._loop.call_later(.0001, self._poll_socket)

    def _handle_on_send(self):
        '''
        Hadles the pending message to be sent across this socket.
        '''
        msg = self._send_queue.popleft()
        try:
            print("Sending message:", msg)
            status = self._socket.send_multipart(msg)
        except zmq.ZMQError as e:
            log.exception("Send error: %s" % zmq.strerror(e.errno))
        if self._on_send_callback is not None:
            self._on_send_callback(msg, status)

    def _handle_on_recv(self):
        '''
        Handles the pending received messages on this socket.
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
        return bool(len(self._send_queue))

    def send(self, msg):
        '''
        Send data on this socket.
        '''
        self._send_queue.append([msg])

    def close(self):
        '''
        Closes this socket, and makes it unusable thereafter.
        '''
        if self._socket is not None:
            self._poll_handle.cancel()
            self._socket.close()
            self._socket = None


class SocketFactory:
    '''
    Convenience class for creating different types of zmq sockets.
    '''

    @staticmethod
    def _topic_to_sock_name(transport, topic):
        '''
        Converts topic name to system acceptable socket name.

        @param transport - socket transport type
        @param topic - topic of the socket.
        @return fully qualified socket path
        '''
        name = topic.lstrip('/').replace('/', '_')
        return "{0}:///tmp/{1}".format(transport, name)

    @staticmethod
    def pub_socket(topic, on_send=None, transport="ipc", port=None, loop=None):
        '''
        Create a publish socket on the specified topic.

        @param topic - topic of this socket
        @param transport - what kind of transport to use for messaging(inproc, ipc, tcp etc)
        @param loop - loop this socket will belong to. Default is global async loop.
        @param on_send - callback when messages are sent on this socket.
                         It will be called as `on_send([msg1,...,msgN], status)`
                         Status is either a positive value indicating
                         number of bytes sent, or -1 indicating an error.
        @param port - port number to connect to
        @returns AIOZMQSocket
        '''
        if transport != "ipc" or port is not None:
            raise NotImplemented("Only IPC transport is currently supported.")

        # TODO: Once topics have a clear definition do a lookup of the URL
        # against definition table
        context = zmq.Context.instance()
        socket = context.socket(zmq.PUB)
        sock_path = SocketFactory._topic_to_sock_name(transport, topic)
        socket.bind(sock_path)

        async_sock = AIOZMQSocket(socket, loop=loop)
        async_sock.on_send(on_send)

        return async_sock

    @staticmethod
    def sub_socket(topic, on_recv=None, transport="ipc", port=None, loop=None):
        '''
        Create a subscriber socket on the specified topic.

        @param topic - topic of this socket
        @param transport - what kind of transport to use for messaging(inproc, ipc, tcp etc)
        @param loop - loop this socket will belong to. Default is global async loop.
        @param on_recv - callback when messages are received on this socket.
                         It will be called as `on_recv([msg1,...,msgN])`
                         If set to None - no data will be read from this socket.
        @param port - port number to connect to
        @returns AIOZMQSocket
        '''
        if transport != "ipc" or port is not None:
            raise NotImplemented("Only IPC transport is currently supported.")

        # TODO: Once topics have a clear definition do a lookup of the URL
        # against definition table
        context = zmq.Context.instance()
        socket = context.socket(zmq.SUB)
        socket.setsockopt(zmq.SUBSCRIBER, '')

        sock_path = SocketFactory._topic_to_sock_name(transport, topic)
        socket.connect(sock_path)

        async_sock = AIOZMQSocket(socket, loop=loop)
        async_sock.on_recv(on_recv)

        return async_sock

    @staticmethod
    def req_socket(topic, on_send=None, on_recv=None, transport="ipc", port=None, loop=None):
        '''
        Create a subscriber socket on the specified topic.

        @param topic - topic of this socket
        @param transport - what kind of transport to use for messaging(inproc, ipc, tcp etc)
        @param loop - loop this socket will belong to. Default is global async loop.
        @param on_send - callback when messages are sent on this socket.
                         It will be called as `on_send([msg1,...,msgN], status)`
                         Status is either a positive value indicating
                         number of bytes sent, or -1 indicating an error.
        @param on_recv - callback when messages are received on this socket.
                         It will be called as `on_recv([msg1,...,msgN])`
                         If set to None - no data will be read from this socket.
        @param port - port number to connect to
        @returns AIOZMQSocket
        '''
        if transport != "ipc" or port is not None:
            raise NotImplemented("Only IPC transport is currently supported.")

        # TODO: Once topics have a clear definition do a lookup of the URL
        # against definition table
        context = zmq.Context.instance()
        socket = context.socket(zmq.REQ)

        sock_path = SocketFactory._topic_to_sock_name(transport, topic)
        log.info("Connecting to socket: %s", sock_path)
        print("Connecting to socket:", sock_path)
        socket.connect(sock_path)

        async_sock = AIOZMQSocket(socket, loop=loop)
        async_sock.on_send(on_send)
        async_sock.on_recv(on_recv)

        return async_sock

    @staticmethod
    def rep_socket(topic, on_send=None, on_recv=None, transport="ipc", port=None, loop=None):
        '''
        Create a subscriber socket on the specified topic.

        @param topic - topic of this socket
        @param transport - what kind of transport to use for messaging(inproc, ipc, tcp etc)
        @param loop - loop this socket will belong to. Default is global async loop.
        @param on_send - callback when messages are sent on this socket.
                         It will be called as `on_send([msg1,...,msgN], status)`
                         Status is either a positive value indicating
                         number of bytes sent, or -1 indicating an error.
        @param on_recv - callback when messages are received on this socket.
                         It will be called as `on_recv([msg1,...,msgN])`
                         If set to None - no data will be read from this socket.
        @param port - port number to connect to
        @returns AIOZMQSocket
        '''
        if transport != "ipc" or port is not None:
            raise NotImplemented("Only IPC transport is currently supported.")

        # TODO: Once topics have a clear definition do a lookup of the URL
        # against definition table
        context = zmq.Context.instance()
        socket = context.socket(zmq.REP)

        sock_path = SocketFactory._topic_to_sock_name(transport, topic)
        log.info("Connecting to socket: %s", sock_path)
        print("Connecting to socket:", sock_path)
        socket.bind(sock_path)

        async_sock = AIOZMQSocket(socket, loop=loop)
        async_sock.on_send(on_send)
        async_sock.on_recv(on_recv)

        return async_sock

