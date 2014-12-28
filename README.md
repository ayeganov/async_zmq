asyncio integration with ZeroMQ
===============================
This is a lightweight library that allows one to use zmq sockets with asyncio
loop that doesn't impose coroutine use in any way. Simply create a socket,
specify a callback on reception of data and you are good to go.

Requirements
------------

* Python_ 3.3+
* pyzmq_ 13.1+
* asyncio_ or Python 3.4+

