import socket
import threading

bind_ip = ""
bind_port = 60007

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen(5)

print("[*] Listening on %s:%d" % (bind_ip, bind_port))


def handle_client(client_socket):

    request = client_socket.recv(1024).decode()
    print("[*] Received: %s" % request)

    send_data = "ACK!"
    client_socket.send(send_data.encode())
    print(client_socket.getpeername())
    client_socket.close()


while True:

    client, addr = server.accept()
    print("[*] Accepted connect from: %s:%d" % (addr[0], addr[1]))

    client_handler = threading.Thread(target=handle_client, args=(client,))
    client_handler.start()