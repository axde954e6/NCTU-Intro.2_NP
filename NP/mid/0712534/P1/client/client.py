#!/usr/bin/python3

from os import read
from socket import *
import threading
import sys

class server_INFO(object):
    def __init__(self,IP,port) -> None:
        self.IP=str(IP)
        self.port=int(port)

def main():
    if len(sys.argv) < 3:
        print(f"\tUsage {sys.argv[0]} <IP> <Port> <file1> <flie2>.....")
        exit(-1)
    UDP_sockfd= socket(AF_INET, SOCK_DGRAM)
    server=server_INFO(sys.argv[1],sys.argv[2])
    msg=""
    while(1):
        msg = input("% ")
        cmd = msg.split(" ")[0]
        UDP_sockfd.sendto(msg.encode(),(server.IP, server.port))
        
        
        if cmd=="send-file":
            Arg= msg.split(" ")
            for it in Arg[1:]:
                get_file=open(it,mode='r')
                all_word=get_file.read()
                get_file.close()
                UDP_sockfd.sendto(all_word.encode(),(server.IP, server.port))
           
        elif cmd=="exit":
            
            UDP_sockfd.close()
            break

    


if __name__ == "__main__":
    main()
