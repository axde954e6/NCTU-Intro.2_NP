#!/usr/bin/python3

from socket import *
import threading
import sys
import os


def HandelUDP(UDPsockfd):
    msg, addr = UDPsockfd.recvfrom(1024)
    msg = msg.decode()
    cmd=msg.split()[0]
    servmsg=""
    if cmd=="send-file":
        Arg= msg.split(" ")
        for it in Arg[1:]:
            msg, addr = UDPsockfd.recvfrom(1024)
            file_write=open(it,'w')
            file_write.write(msg.decode())
            file_write.close()
    

def main():
    if len(sys.argv) != 2:
        print(f"\tUsage {sys.argv[0]} <Port>")
        exit(-1)
    HOSTNAME, ListenPort = "", int(sys.argv[1])
    UDPsockfd = socket(AF_INET, SOCK_DGRAM)
    UDPsockfd.bind((HOSTNAME, ListenPort))

    while True:
        HandelUDP(UDPsockfd)

if __name__ == "__main__":
    main()