#!/usr/bin/python3
import socket
import select
import json
import sys
#from socket import *


def main():

    if len(sys.argv) != 3:

        print(f"\tUsage {sys.argv[0]} <IP> <Port>")
        exit(-1)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((sys.argv[1], int(sys.argv[2])))

    while True:
        sendmsg = ""
        sockets_list = [sys.stdin, server]
        read_sockets, write_socket, error_socket = select.select(
            sockets_list, [], [])
        for socks in read_sockets:
            if socks == server:
                message = socks.recv(2048).decode()
                if message:
                    print(message,end='')
            else:
                message = sys.stdin.readline()
                if message.find("\n") != 0:
                    message = message[:message.find("\n")]

                sendmsg = message
                server.send(sendmsg.encode())
                if  message == "exit":
                    server.close()
                    read_sockets.clear()
                    return


if __name__ == "__main__":
    main()
