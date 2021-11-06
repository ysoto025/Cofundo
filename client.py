#!/usr/bin/env python3

import argparse
import os
import socket
import sys

import confundo
from confundo.header import Header
from confundo.packet import Packet

parser = argparse.ArgumentParser("Parser")
parser.add_argument("host", help="Set Hostname")
parser.add_argument("port", help="Set Port Number", type=int)
parser.add_argument("file", help="Set File Directory")
args = parser.parse_args()

def start():
    try:
        with confundo.Socket() as sock:
            sock.settimeout(10)
            sock.connect((args.host, int(args.port)))

            header = Header(77, 0, 0, True)
            packet = Packet(header)
            print(packet)
            sock.send("pack", packet)
            packet_from_server = Packet(sock.recv(424)).decode()

            if packet_from_server.isSyn and packet_from_server.isAck:
                packet.connId = packet_from_server.connId
                packet.isAck = True
                sock.send(packet.encode())
            else:
                sys.stderr.write("ERROR:  FLAGS were not active")
                sys.exit(0)

            with open(args.file, "rb") as f:
                data = f.read(50000)
                while data:
                    total_sent = 0
                    while total_sent < len(data):
                        sent = sock.send(data[total_sent:])
                        total_sent += sent
                        data = f.read(50000)
    except RuntimeError as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)


if __name__ == '__main__':
    start()
