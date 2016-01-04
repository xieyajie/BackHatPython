import socket

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

send_data = "client udp data 01"
client.sendto(send_data.encode(), ("127.0.0.1", 60001))
print("Client SEND: " + send_data)

recv_data, addr = client.recvfrom(4096)
print("Client RECV: " + recv_data.decode())
