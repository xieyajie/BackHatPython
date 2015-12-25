import socket
import json

target_host = "127.0.0.1"
target_port = 50007

# AF_INET将使用标准的IPv4地址或者主机名
# SOCK_STREAM 使用TCP
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((target_host, target_port))

send_data = "GET / HTTP/1.1\r\nHost: baidu.com\r\n\r\n"
client.send(send_data.encode())

response = client.recv(4096).decode()
print(response)
