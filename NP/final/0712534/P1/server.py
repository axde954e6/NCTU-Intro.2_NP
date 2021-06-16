#!/usr/bin/python3
from socket import *
import json
import threading
import sys


cli_fd={}
fd_cli={}
fd_black={}
mute={}


class ServerService(object):
    def __init__(self):
        self.next_serial_number = 1
        
    def boardcase(self,sockfd,msg):
        for it in fd_cli:
            if it != sockfd and (fd_cli[it] not in fd_black[sockfd]) and (fd_cli[it] not in mute):
                it.send(msg.encode())
            

    def HandleTCP(self, sockfd, saddr,username):
        try:
            inimsg="*" * 32 + "\n** Welcome to the BBS server. **\n" + "*" * 32+"\n"+"Welcome, "+username+".\n"
            sockfd.send(inimsg.encode())
            while True:
                msg = sockfd.recv(1024).decode().rstrip("\n")
                
                
                cmd = msg.split(" ")[0]
                
                if cmd == "exit":
                    username=fd_cli[sockfd]
                    print(username+" "+str(saddr[0])+":"+str(saddr[1])+" disconnected.")
                    del cli_fd[username]
                    del fd_cli[sockfd]
                    del fd_black[sockfd]
                    sockfd.close()
                    return

                servmsg = self.HandleClientMsg(msg, sockfd,username)
                if servmsg !="Broadcast":
                    sockfd.send(servmsg.encode())
        except KeyboardInterrupt:
            return

    def HandleClientMsg(self, msg, sockfd,username):
        cmd = msg.split(" ")[0]
        
        Arg=msg.split(" ")
        servmsg=""
        if cmd=="mute":
            if username not in mute:
                servmsg="Mute mode.\n"
                mute[username]=1
            else:
                servmsg="You are already in mute mode.\n"

        if cmd=="unmute":
            if username in mute:
                servmsg="Unmute mode.\n"
                del mute[username]
            else:
                servmsg="You are already in unmute mode.\n"

        

        if cmd=="yell":
            smsg=username+" : "
            smsg=smsg+msg[len("yell "):]+'\n'
            self.boardcase(sockfd,smsg)
            servmsg="Broadcast"
        if cmd=="tell":
            if Arg[1] not in cli_fd:
                servmsg=Arg[1]+" does not exist.\n"
            else:
                servmsg="Broadcast"
                pos=msg.find(Arg[1])
                smsg=username+" told you: "+msg[pos+len(Arg[1])+1:]+"\n"
                if Arg[1] not in mute:
                    cli_fd[Arg[1]].send(smsg.encode())
        
        return servmsg

            
    
def main():
    if len(sys.argv) != 2:
        print(f"\tUsage {sys.argv[0]} <Port>")
        exit(-1)
    HOSTNAME, ListenPort = "", int(sys.argv[1])

    TCPsockfd = socket(AF_INET, SOCK_STREAM)
    TCPsockfd.bind((HOSTNAME, ListenPort))
    TCPsockfd.listen(30)
    server=ServerService()
    # TCP_thread
    TCP_thread = []
    try:
        while True:
            now_TCPfd, now_addr = TCPsockfd.accept()
            
            username="user"+str(server.next_serial_number)
            print("New connection from ",now_addr[0],":",now_addr[1]," ",username)
            cli_fd[username]=now_TCPfd
            fd_cli[now_TCPfd]=username
            
            #print("username:",username)
            fd_black[now_TCPfd]=[]
            server.next_serial_number+=1
            TCP_thread.append(
                threading.Thread(
                    target=server.HandleTCP,
                    args=(
                        now_TCPfd,
                        now_addr,
                        username,
                    ),
                )
            )
            TCP_thread[-1].start()
    except KeyboardInterrupt:
        print("\nClose Server.")
    for sockfd in [TCPsockfd]:
        sockfd.close()
    return 0



    
if __name__ == "__main__":
    main()