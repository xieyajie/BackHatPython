import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 50002))

send_data = "haha, text 01"
client.send(send_data.encode())
print("Client SEND: " + send_data)

recv_data = client.recv(4096).decode()
print("Client RECV: " + recv_data)

client.close()
