# coding=utf-8

import socket
import os
import struct
from ctypes import *

host = "127.0.0.1"

# Structures和Unions必须继承Structure和Union基础类，它们都在ctypes模块中定义，
# 每一个子类必须定义个_fields_属性，_fields_是一个二维的tuples列表，包含着每个field的name及type，
# 这field类型必须是一个ctypes类型，如c_int，或者任何其他的继承ctypes的类型，如Structure, Union, Array, 指针等
class IP(Structure):
    _fields_ = [
        # 头长度, 4位
        ("ih1", c_ubyte, 4),
        # 版本号, 4位. 目前采用的IP协议的版本号,一般的值为0100（IPv4），0110（IPv6）
        ("version", c_ubyte, 4),
        # 服务类型, 8位
        ("tos", c_ubyte, 8),
        # 包总长, 16位
        ("len", c_ushort, 16),
        # 标识符, 16位
        ("id", c_ushort, 16),
        # 标志, 3位
        # ("tag", c_ubyte, 3),
        # 片偏移, 13位
        ("offset", c_ushort, 16),
        # 生存时间, 8位. 当IP包经过每一个沿途的路由器的时候，每个沿途的路由器会将IP包的TTL值减少1。如果TTL减少为0，则该IP包会被丢弃
        ("ttl", c_ubyte, 8),
        # 协议, 8位. 1:ICMP 2:IGMP 6:TCP 17:UDP 88:IGRP 89:OSPF
        ("protocol_num", c_ubyte, 8),
        # 头部校验, 16位
        ("sum", c_ushort, 8),
        # c_ulong is 4 bytes in i386 and 8 in amd64
        ## 发送地址, 32位
        #("src", c_ulong, 32),
        ## 目标地址, 32位
        #("dst", c_ulong, 32)
        # 发送地址, 32位
        ("src", c_uint32, 32),
        # 目标地址, 32位
        ("dst", c_uint32, 32)
    ]

    # __new__() 静态方法. 实例化开始后,在__init__()之前调用. 没有重写,会自动调用父类
    # __new__()会返回cls的实例，然后该类的__init__()方法作为构造方法会接收这个实例（即self）作为自己的第一个参数，然后依次传入__new__()方法中接收的位置参数和命名参数
    # 如果__new__()没有返回cls（即当前类）的实例，那么当前类的__init__()方法是不会被调用的。
    # 如果__new__()返回其他类（新式类或经典类均可）的实例，那么只会调用被返回的那个类的构造方法.
    def __new__(cls, socket_buffer=None):
        # 将原始缓冲区中的数据填充到结构中
        return cls.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):
        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}

        # struct
        # pack(fmt, v1, v2, ...)
        # 按照给定的格式(fmt)，把数据封装成字符串(实际上是类似于c结构体的字节流)
        # unpack(fmt, string)
        # 按照给定的格式(fmt)解析字节流string，返回解析出来的tuple
        # calcsize(fmt)
        #  计算给定的格式(fmt)占用多少字节的内存

        # socket.inet_ntoa: 将32位形式的IP地址转换成字符串形式的IP地址,非线程安全
        self.src_address = socket.inet_ntoa(struct.pack("@I", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("@I", self.dst))
        # self.src_address = self.src
        # self.dst_address = self.dst

        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)

    def decode_buffer(self, buffer=None):
        if buffer:
            self.version = (int(ord(buffer[0])) & 0xF0) >> 4
            self.ih1 = (int(ord(buffer[0])) & 0x0F) << 2
            # self.tos = hex(int(ord(socket_buffer[1])))
            self.len = (int(ord(buffer[2]) << 8))+(int(ord(buffer[3])))
            self.id = (int(ord(buffer[4]) >> 8)) + (int(ord(buffer[5])))
            self.tag = int(ord(buffer[6]) & 0xE0) >> 5
            self.offset = int(ord(buffer[6]) & 0x1F) << 8 + int(ord(buffer[7]))
            self.ttl = int(ord(buffer[8]))
            self.protocol_num = int(ord(buffer[9]))
            self.sum = int(ord(buffer[10]) << 8)+int(ord(buffer[11]))
            self.src_address = "%d.%d.%d.%d" % (int(ord(buffer[12])), int(ord(buffer[13])), int(ord(buffer[14])), int(ord(buffer[15])))
            self.dst_address = "%d.%d.%d.%d" % (int(ord(buffer[16])), int(ord(buffer[17])), int(ord(buffer[18])), int(ord(buffer[19])))


if os.name == "nt":
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
sniffer.bind((host, 0))
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

# 如果在Windows上,发送IOCTL信号到网卡驱动上以启用混杂模式
if os.name == "nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

try:
    while True:
        raw_buffer = sniffer.recvfrom(65565)[0]
        # ip_header = IP(raw_buffer[:20]) works on x86 Ubuntu.
        # ip_header = IP(raw_buffer[:32]) works on amd64 CentOS 6.6 Python 2.6.6
        # ip_header = IP(raw_buffer) works in both.
        ip_header = IP(raw_buffer)

        # ip_header = IP(raw_buffer)
        # ip_header.decodeBuffer(raw_buffer)
        print("Protocol: %s %s -> %s" % (ip_header.protocol, ip_header.src_address, ip_header.dst_address))

except KeyboardInterrupt:
    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)