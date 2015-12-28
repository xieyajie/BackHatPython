import socket

address = ('127.0.0.1', 50007)

# SOCK_DGRAM 使用UDP, 不保持长连接
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    data = input("输入发送内容:")
    client.sendto(data.encode(), address)

    data, addr = client.recvfrom(4096)
    print(data.decode())