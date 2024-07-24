import socket
from socket import getfqdn
import threading

def handle_client_request(client_socket):
    request = b''

    client_socket.setblocking(False)

    while True:
        try:
            data = client_socket.recv(1024)
            request = request + data
        except:
            break

    host, port = extract_host_port_from_request(request)

    destination_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    destination_socket.connect((host, port))
    destination_socket.sendall(request)

    while True:
        data = destination_socket.recv(1024)

        if len(data) > 0:
            client_socket.sendall(data)
        else:
            break

    destination_socket.close()
    client_socket.close()

def extract_host_port_from_request(request):
    host_string_start = request.find(b'Host: ') + len(b'Host: ')
    host_string_end = request.find(b'\r\n', host_string_start)
    host_string = request[host_string_start:host_string_end].decode('utf-8')

    webserver_pos = host_string.find("/")

    if webserver_pos == -1:
        webserver_pos = len(host_string)

    port_pos = host_string.find(":")

    if port_pos == -1 or webserver_pos < port_pos:
        port = 80
        host = host_string[:webserver_pos]
    else:
        port = int((host_string[(port_pos + 1):])[:webserver_pos - port_pos - 1])
        host = host_string[:port_pos]

    return host, port

def start_proxy_server():
    port = 8888

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((socket.gethostbyname(socket.getfqdn()), port))
    server.listen()

    print(f"Proxy server listening on {server.getsockname()} and port {port}")

    while True:
        client_socket, addr = server.accept()
        client_handler = threading.Thread(target=handle_client_request, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":

    start_proxy_server()