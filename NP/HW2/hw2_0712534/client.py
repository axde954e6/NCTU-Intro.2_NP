#!/usr/bin/python3

from socket import *
import sys
import json

UDP_CMD = ["register", "whoami"]


class ClientService(object):
    def __init__(self, IP, Port):
        self.IP = IP
        self.Port = Port
        self.sessionID = -1

    def UDPsender(self, msg, UDP_sockfd):
        msg2serv = json.dumps({'msg': msg, 'sid': self.sessionID})
        UDP_sockfd.sendto(msg2serv.encode(), (self.IP, self.Port))
        servmsg, servaddr = UDP_sockfd.recvfrom(1024)
        content = json.loads(servmsg.decode())
        self.sessionID = content["sid"]
        # UDP_sockfd.close()
        return content["msg"]

    def TCPsender(self, msg, TCP_sockfd, cmd):
        msg2serv = json.dumps({'msg': msg, 'sid': self.sessionID})
        TCP_sockfd.send(msg2serv.encode())
        if cmd == "exit":
            return
        servmsg = TCP_sockfd.recv(1024).decode()
        content = json.loads(servmsg)
        self.sessionID = content["sid"]
        return content["msg"]

    def Create_socket(self):
        Tsockfd = socket(AF_INET, SOCK_STREAM)
        Tsockfd.connect((self.IP, self.Port))  # tuple
        Usockfd = socket(AF_INET, SOCK_DGRAM)
        return Tsockfd, Usockfd


def main():
    if len(sys.argv) != 3:

        print(f"\tUsage {sys.argv[0]} <IP> <Port>")
        exit(-1)

    Client = ClientService(sys.argv[1], int(sys.argv[2]))

    TCP_sockfd, UDP_sockfd = Client.Create_socket()
    msg = Client.UDPsender("INITIAL", UDP_sockfd)
    if msg:
        print(msg)
    else:
        print("Failed to connect to {IP}:{Port}")
        exit(-1)

    while True:
        msg = input("% ")
        cmd = msg.split(" ")[0]
        if cmd in UDP_CMD:
            servmsg = Client.UDPsender(msg, UDP_sockfd)
        else:
            servmsg = Client.TCPsender(msg, TCP_sockfd, cmd)
        if cmd == "exit":
            TCP_sockfd.close()
            UDP_sockfd.close()
            break
        print(servmsg)


if __name__ == "__main__":
    main()
