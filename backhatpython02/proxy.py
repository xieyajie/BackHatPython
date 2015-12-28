import sys
import socket
import threading

def hexdump(src, length=16):
    result = []

    # Python 3 renamed the unicode type to str, the old str type has been replaced by bytes
    digits = 4 if isinstance(src, str) else 2

    for i in range(0, len(src), length):
        s = src[i: i+length]
        # b开头说明是byte
        # ord() 参数是一个ascii字符，返回值是对应的十进制整数
        hexa = b' '.join(["%0*X" % (digits, ord(x)) for x in s])
        text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.' for x in s])
        result.append(b"%04X    %-*s    %s" % (i, length * (digits + 1), hexa, text))

    print(b'\n'.join(result))


def receive_from(connection):

    buffer = ""

    connection.settimeout(2)

    try:
        while True:
            data = connection.recv(4096).decode()

            if not data:
                break

            buffer += data
    except:
        pass

    return buffer


def request_handler(buffer):
    return buffer.decode()


def response_handler(buffer):
    return buffer.decode()


def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

        remote_buffer = response_handler(remote_buffer)
        if len(remote_buffer):
            print("[<==] Sending %d bytes to localhost." % len(remote_buffer))
            client_socket.send(remote_buffer)

    while True:
        local_buffer = receive_from(client_socket)

        if len(local_buffer):
            print("[==>] Received %d bytes from localhost." % len(local_buffer))
            hexdump(local_buffer)

            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Send to remote")

        remote_buffer = receive_from(remote_socket)

        if len(remote_buffer):
            print("[<==] Received %d bytes from remote." % len(remote_buffer))
            hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)

            print("[<==] Sent to localhost.")

        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()

            print("[*] No more data. Closing connections.")

            break


def server_loop(local_host, local_port, remote_host, remote_ip, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((local_host, local_port))
    except:
        print("[!!] Failed to listen on %s:%d" % (local_host, local_port))
        print("[!!] Check for other listening sockets or correct permissions.")
        sys.exit(0)

    print("[*] Listening on %s:%d" % (local_host, local_port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        print("[==>] Received incoming connection from %s:%d" % (addr[0], addr[1]))

        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_ip, receive_first))
        proxy_thread.start()


def main():
    cmd_input = input("输入命令:")
    info_input = cmd_input.split()
    # info_input = sys.argv[1:]
    if len(info_input) != 5:
        print("Usage: ./proxy.py [localhost] [localport] [remotehost] [remoteport] [receive_first]")
        print("Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 90000 True")
        sys.exit(0)

    local_host = info_input[0]
    local_port = int(info_input[1])

    remote_host = info_input[2]
    remote_port = int(info_input[3])

    receive_first = info_input[4]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)

if __name__ == '__main__':
    main()
