#!/usr/bin/python3

from socket import *
import sys
import json
import chat_server
import chat_app
import threading

UDP_CMD = ["register", "whoami", "list-chatroom"]


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
        return content

    def TCPsender(self, msg, TCP_sockfd, cmd):
        msg2serv = json.dumps({'msg': msg, 'sid': self.sessionID})
        TCP_sockfd.send(msg2serv.encode())
        if cmd == "exit":
            return
        servmsg = TCP_sockfd.recv(1024).decode()
        content = json.loads(servmsg)
        self.sessionID = content["sid"]
        return content

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
    username = msg["username"]
    if msg:
        print(msg['msg'])
    else:
        print("Failed to connect to {IP}:{Port}")
        exit(-1)

    while True:
        msg = input("% ")
        cmd = msg.split(" ")[0]
        if cmd in UDP_CMD:
            content = Client.UDPsender(msg, UDP_sockfd)
        else:
            content = Client.TCPsender(msg, TCP_sockfd, cmd)

        if cmd == "exit":
            TCP_sockfd.close()
            UDP_sockfd.close()
            break
        username = content["username"]
        chat_port = content['get_port']
        servmsg = content['msg']
        if servmsg == "enter chat room":
            chat_app.server_username=""
            ChatAPPThread = threading.Thread(
                target=chat_app.chatroom_APP,
                args=(username, "", chat_port),
            )
            ChatAPPThread.start()
            ChatAPPThread.join()
            c = Client.TCPsender("EXITCHAT", TCP_sockfd, "EXITCHAT")
            servmsg = c['msg']
        elif servmsg == "ATTACH":
            chat_app.server_username=username
            ChatAPPThread = threading.Thread(
                target=chat_app.chatroom_APP,
                args=(username, "", chat_port),
            )
            ChatAPPThread.start()
            ChatAPPThread.join()
            chat_server.event.acquire()
            if chat_server.chatroomstate == "close":
                c = Client.TCPsender("ENDCHATROOM", TCP_sockfd, "ENDCHATROOM")
            else:
                c = Client.TCPsender("EXITCHAT", TCP_sockfd, "EXITCHAT")
            servmsg = c['msg']

        print(servmsg)
        if servmsg == "start to create chatroom...":
            ChatServerThread = threading.Thread(
                target=chat_server.ChatServer,
                args=(username, "", chat_port),
            )
            chat_server.chatroomstate = "run"
            ChatServerThread.start()
            chat_server.event.acquire()
            chat_app.server_username=username
            ChatAPPThread = threading.Thread(
                target=chat_app.chatroom_APP,
                args=(username, "", chat_port),
            )
            ChatAPPThread.start()
            ChatAPPThread.join()
            chat_server.event.acquire()
            if chat_server.chatroomstate == "close":
                c = Client.TCPsender("ENDCHATROOM", TCP_sockfd, "ENDCHATROOM")
            else:
                c = Client.TCPsender("EXITCHAT", TCP_sockfd, "EXITCHAT")
            print(c['msg'])


if __name__ == "__main__":
    main()
