# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import socket

def test2():
    target_host = "www.kendelweb.de"

    target_port = 21  # create a socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect the client
    client.connect((target_host,target_port))

    # send some data
    #request = "GET / HTTP/1.1\r\nHost:%s\r\n\r\n" % target_host
    request = "GET / HTTP/1.1\r\nHost:%s/%s\r\n\r\n" % (target_host, ".private/keypassxc/random" )
    client.send(request.encode())

    # receive some data
    response = client.recv(4096)
    http_response = repr(response)
    http_response_len = len(http_response)

    #display the response
    print("[RECV] - length: %d" % http_response_len)
    print(http_response)

def test1():
    TCP_IP = '127.0.0.1'
    TCP_PORT = 8000
    BUFFER_SIZE = 1024
    MESSAGE = b"Hello, World!"
    s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    s.connect( (TCP_IP, TCP_PORT) )
    s.send( MESSAGE )
    data = s.recv(BUFFER_SIZE)
    s.close()
    print( "received data:", data )

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    test1()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
