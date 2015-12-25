#!/opt/local/bin/python2.7

import sys
import socket
import getopt
import threading
import subprocess

listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0


def run_command(cmd):

    # rstrip() 删除 string 字符串末尾的指定字符（默认为空格）
    cmd = cmd.rstrip()

    try:
        # subprocess.check_output() 父进程等待子进程完成, 返回子进程向标准输出的输出结果
        # 函数中多个参数都有默认值,如果想中间几个用默认值,后边的自赋值,需要"参数名=自定义值"
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command.\r\n"

    return output


def client_handler(client_socket):

    # 函数里如果只使用到了全局变量的值，而没有对其赋值（指a = XXX这种写法）的话，就不需要声明global。
    global upload
    global execute
    global command

    if len(upload_destination):
        file_buffer = ""

        while True:
            data = client_socket.recv(1024)

            if not data:
                break
            else:
                file_buffer += data

        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            client_socket.send("Successfully saved file to %s\r\n" % upload_destination)
        except:
            client_socket.send("Failed to save file to %s\r\n" % upload_destination)

    if len(execute):
        output = run_command(execute)
        client_socket.send(output)

    if command:

        while True:
            client_socket.send("<BHP:#>")
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)

            response = run_command(cmd_buffer)
            client_socket.send(response)


def server_loop():
    global target
    global port

    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()


def client_sender(buffer):

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((target, port))

        if len(buffer):
            client.send(buffer)

        while True:

            recv_len = 1
            response = ""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break

            print(response, end=' ')

            buffer = input("")
            buffer += "\n"

            client.send(buffer)
    except:
        print("[*] Exceptions! Exiting.")

        client.close()


def usage():
    print("Netcat Replacement")
    print()
    print("Usage: bhpnet.py -t target_host -p port")
    print("-l --listen                 - listen on [host]:[port] for incoming connections")
    print("-e --execute=file_to_run    - execute the given file upon receiving a connection")
    print("-c --command                - initialize a command shell")
    print("-u --upload=destonation     - upon receiving connection upload a file and write to [destination]")
    print()
    print()
    print("Examples:")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -c")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.ext")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"")
    print("echo 'ABCDEFGHI' | ./bhpnet.py -t 192.168.0.01 -p 135")
    sys.exit(0)


def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    # python test.py --t help --v
    # 那么sys.argv就是['test.py', '--t', 'help', '--v']
    # 那么sys.argv[1:]就是['--t', 'help', '--v']
    # if not len(sys.argv[1:]):
    #     usage()

    argvs = input()

    try:
        # getopt.getopt()返回两个值，
        # 一个为optlist，参数选项和参数值组成的一个列表
        # 一个为args，单独的参数值组成一个列表对应参数选项
        # "hle:..." 为短选项处理格式，h,l,都表示是为无参数，e:表示必有参数,必须要有参数的则在字符后面加“:”表示.
        # ['help', 'listen', ...] 为长选项处理格式
        opts, args = getopt.getopt(argvs.split(), "hle:t:p:cu:",
                                   ["help", "listen", "execute", "target", "port", "command", "upload"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    for o, a in opts:
        if o in("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"

    if not listen and len(target) and port > 0:
        buffer = sys.stdin.read()
        client_sender(buffer)

    if listen:
        server_loop()

if __name__ == '__main__':
    main()
