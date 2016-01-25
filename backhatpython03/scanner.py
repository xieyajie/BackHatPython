# coding=utf-8

import socket
import os
import struct
import threading
import time

from ctypes import *
from netaddr import IPNetwork, IPAddress

host = "127.0.0.1"

# 扫描的目标子网
subnet = "192.168.0.0/24"

magic_message = "PYTHONRULES!"


# 批量发送UDP包
def udp_sender(subnet, magic_message):
    time.sleep(5)
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("udp_sender")

    for ip in IPNetwork(subnet):
        try:
            sender.sendto(magic_message.encode(), ("%s" % ip, 65212))
            print("did send to ip: %s" % ip)
        except:
            pass


class IP(Structure):

    _fields_ = [
        ("ihl", c_ubyte, 4),
        ("version", c_ubyte, 4),
        ("tos", c_ubyte),
        ("len", c_ushort),
        ("id", c_ushort),
        ("offset", c_ushort),
        ("ttl", c_ubyte),
        ("protocol_num", c_ubyte),
        ("sum", c_ushort),
        ("src", c_uint32),
        ("dst", c_uint32)
    ]

    def __new__(cls, socket_buffer=None):
        return cls.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):
        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}

        self.src_address = socket.inet_ntoa(struct.pack("@I", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("@I", self.dst))

        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)


class ICMP(Structure):

    _fields_ = [
        ("type", c_ubyte),
        ("code", c_ubyte),
        ("checksum", c_ushort),
        ("unused", c_ushort),
        ("next_hop_mtu", c_ushort)
    ]

    def __new__(cls, socket_buffer):
        return cls.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer):
        pass


if os.name == "nt":
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
sniffer.bind(("", 65212))
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

if os.name == "nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

# 开始发送数据包
t = threading.Thread(target=udp_sender, args=(subnet, magic_message))
t.start()

try:
    print(IPNetwork(subnet))

    while True:
        print("begin recv")

        raw_buffer = sniffer.recvfrom(65212)[0]
        print("end recv")
        ip_header = IP(raw_buffer)
        print("Protocol: %s %s -> %s" % (ip_header.protocol, ip_header.src_address, ip_header.dst_address))

        if ip_header.protocol == "ICMP":
            # IP头长度的计算基于IP头中得ihl字段,它代表IP头中32位(4字节)长的分片的个数
            offset = ip_header.ihl * 4
            buf = raw_buffer[offset:]

            icmp_header = ICMP(buf)
            print("ICMP -> Type: %d Code: %d" % (icmp_header.type, icmp_header.code))

            # 检测代码值和类型都是3的ICMP
            if icmp_header.code == 3 and icmp_header.type == 3:

                print("In 3")

                # 判断ICMP响应是否来自目标子网
                if IPAddress(ip_header.src_address) in IPNetwork(subnet):

                    print("In subnet")

                    # 判断ICMP信息中是否包含自定义的字符串签名
                    if raw_buffer[len(raw_buffer) - len(magic_message):] == magic_message:
                        print("Host Up: %s" % ip_header.src_address)


# handle CTRL-C
except KeyboardInterrupt:
    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
