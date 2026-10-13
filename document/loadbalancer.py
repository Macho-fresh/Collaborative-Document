import socket

servers = [('127.0.0.1', 8001), ('127.0.0.1', 8002)]

def get_server():
    current_server = 0
    if current_server > 2:
        current_server = 0
    current_server +=1
    server = 1 % current_server

    return server

# build the load balancer function