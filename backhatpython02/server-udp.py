import socket

address = ('192.168.1.8', 0)
socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket.bind(address)

while True:
    data, addr = socket.recvfrom(4096)
    if not data:
        print("client has exist")
        break

    print("[*] Received from: %s:%d" % (addr[0], addr[1]))
    print("[*] Received data: %s" % data.decode())

    socket.sendto("Server ACK!".encode(), addr)