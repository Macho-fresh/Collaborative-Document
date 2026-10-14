import socket

servers = [('127.0.0.1', 8001), ('127.0.0.1', 8002)]

CURRENT_SERVER = -1

def get_server():
    global CURRENT_SERVER
    CURRENT_SERVER += 1
    if CURRENT_SERVER >= len(servers):
        CURRENT_SERVER = 0
    
    return servers[CURRENT_SERVER]

# build the load balancer function

def loadbalancer():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind('127.0.0.0', 8000)
    server.listen(10)
    print('load balancer running on port 8000')
    while True:
        client_socket, client_address = server.accept()
        print(f'client connected, client address: {client_address}')
        backend_host, backend_port = get_server()
        print(f'forwarding conection to: {backend_host}:{backend_port}')
        backend_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backend_socket.connect(backend_host, backend_port)
        data = client_socket.recv(4096)
        backend_socket.sendall(data)
        response = backend_socket.recv(4096)
        client_socket.sendall(response)
        client_socket.close()
        backend_socket.close()

if __name__ == '__main__':
    loadbalancer()