#!/usr/bin/python3

from os import read
import  socket
import threading
import sys

class server_INFO(object):
    def __init__(self,IP,port) -> None:
        self.IP=str(IP)
        self.port=int(port)

def main():
    if len(sys.argv) < 3:
        print(f"\tUsage {sys.argv[0]} <IP> <Port> ")
        exit(-1)
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((sys.argv[1], int(sys.argv[2])))
    smsg = server.recv(1024).decode()
    print(smsg)
    msg = input("% ")
    server.send(msg.encode())
    smsg = server.recv(1024).decode()
    while smsg=="The username is already used!":
        print(smsg)
        msg = input("% ")
        server.send(msg.encode())
        smsg = server.recv(1024).decode()
    print(smsg)
    msg=""
    while(1):
        msg = input("% ")
        cmd = msg.split(" ")[0]
        server.send(msg.encode())
        smsg = server.recv(1024).decode()
        print(smsg,end="")
       
        if cmd=="exit":
            
            server.close()
            break

    


if __name__ == "__main__":
    main()
