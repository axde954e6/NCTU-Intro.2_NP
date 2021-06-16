#!/usr/bin/python3
from socket import *
import json
import threading
import sys

mutex = threading.Lock()

cli_fd={}
fd_cli={}
fd_black={}


accounts={"ACCOUNT1":0,"ACCOUNT2":0}


class ServerService(object):
    def __init__(self):
        self.next_serial_number = 0
        

            

    def HandleTCP(self, sockfd, saddr,username):
        try:
            inimsg="*" * 32 + "\n** Welcome to the TCP server. **\n" + "*" * 32+"\n"
            sockfd.send(inimsg.encode())
            while True:
                msg = sockfd.recv(1024).decode().rstrip("\n")
                
                
                cmd = msg.split(" ")[0]
                
                if cmd == "exit":
                    
                    print(username+" "+str(saddr[0])+":"+str(saddr[1])+" disconnected.")
                    del cli_fd[username]
                    del fd_cli[sockfd]
                    del fd_black[sockfd]
                    sockfd.close()
                    return

                servmsg = self.HandleClientMsg(msg, sockfd,username)
                
                sockfd.send(servmsg.encode())
        except KeyboardInterrupt:
            return

    def HandleClientMsg(self, msg, sockfd,username):
        cmd = msg.split(" ")[0]
        
        Arg=msg.split(" ")
        servmsg=""
        if cmd=="show-accounts":
            mutex.acquire()
            for it in accounts:
                servmsg=servmsg+it+": "+str(accounts[it])+"\n"
            mutex.release()

        if cmd=="deposit":
            mutex.acquire()
            if len(Arg)!=3:
                servmsg="Usage deposit <account> <money>\n"
            elif int(Arg[2])<=0:
                servmsg="Deposit a non-positive number into accounts.\n"
            elif Arg[1] not in accounts:
                servmsg="Account "+Arg[1]+" does not exist.\n"
            else:
                servmsg="Successfully deposits "+Arg[2]+" into "+Arg[1]+".\n"
                now_money=accounts[Arg[1]]+int(Arg[2])
                accounts[Arg[1]]=now_money
            mutex.release()

        

        if cmd=="withdraw":
            mutex.acquire()
            if len(Arg)!=3:
                servmsg="Usage deposit <account> <money>\n"
            elif int(Arg[2])<=0:
                servmsg="Withdraw a non-positive number into accounts.\n"
            elif Arg[1] not in accounts:
                servmsg="Account "+Arg[1]+" does not exist.\n"
            else:
                if  int(Arg[2]) >  accounts[Arg[1]]:
                    servmsg="Withdraw excess money from accounts.\n"
                else:
                    servmsg="Successfully withdraws "+Arg[2]+" into "+Arg[1]+".\n"
                    now_money=accounts[Arg[1]]-int(Arg[2])
                    accounts[Arg[1]]=now_money
            mutex.release()

        
        
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
  
    TCP_thread = []
    try:
        while True:
            now_TCPfd, now_addr = TCPsockfd.accept()
            
            username=chr(ord('A')+server.next_serial_number)
            print("New connection from ",now_addr[0],":",now_addr[1]," ",username)
            cli_fd[username]=now_TCPfd
            fd_cli[now_TCPfd]=username
            
            
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