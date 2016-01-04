import socket

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("", 60001))

recv_data, addr = server.recvfrom(4096)
print("Server RECV: " + recv_data.decode())

if recv_data:
    send_data = "Server ACK -> " + recv_data.decode()
    server.sendto(send_data.encode(), addr)
    print("Server SEND: " + send_data)
