import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("", 50002))
server.listen(1)

connection, addr = server.accept()
if connection:
    recv_data = connection.recv(4096).decode()
    print("Server RECV: " + recv_data)

    send_data = "Server ACK -> " + recv_data
    connection.send(send_data.encode())
