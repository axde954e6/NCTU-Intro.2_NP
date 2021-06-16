#!/usr/bin/python3
from socket import *
import json
import threading
import sys
import os



ip_user={}
user_ip={}


class ServerService(object):
    def __init__(self):
        self.next_serial_number = 1
        
    
            

    def HandleTCP(self, sockfd, saddr):
        try:
            sermsg="Hello, please assign your username:"
            sockfd.send(sermsg.encode())
            while 1:
                msg = sockfd.recv(1024).decode()
                username=msg
                if username in user_ip:
                    sermsg="The username is already used!"
                    sockfd.send(sermsg.encode())
                else:
                    break
            ip_user[saddr]=username
            user_ip[username]=saddr
            sermsg="Welcome, "+username
            sockfd.send(sermsg.encode())
            
            while True:
                msg = sockfd.recv(1024).decode()
                
                if msg.find('\n')!=-1:
                    pos=msg.find('\n')
                    #print("pos:",pos)
                    msg=msg[:pos-1]
                #content = json.loads(msg)
                #print(msg)
                cmd = msg.split(" ")[0]
                
                

                servmsg = self.HandleClientMsg(msg, saddr)
                sockfd.send(servmsg.encode())
                if cmd == "exit":
                    username=ip_user[saddr]
                    del ip_user[saddr]
                    del user_ip[username]
                    sockfd.close()
                    print(username,"\t",saddr[0],":",saddr[1],"\tdisconnected")
                    return
        except KeyboardInterrupt:
            return

    def HandleClientMsg(self, msg, addr):
        cmd = msg.split(" ")[0]
        Arg=msg.split(" ")
        servmsg=""
        if cmd=="list-users":
            for it in user_ip:
                ad=user_ip[it]
                servmsg=servmsg+it+'\t'+str(ad[0])+":"+str(ad[1])+'\n'
                
        if cmd=="sort-users":
            mmm=[]
            for it in user_ip:
                mmm.append(it)
            mmm.sort()
            for it in mmm :
                ad=user_ip[it]
                servmsg=servmsg+it+'\t'+str(ad[0])+":"+str(ad[1])+'\n'
                
            

        if cmd=="exit":
            name=ip_user[addr]
            servmsg="Bye, "+name+".\n"
        
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
            
            
            print("New connection from ",now_addr[0],":",now_addr[1])
            
            
            
            
            server.next_serial_number+=1
            TCP_thread.append(
                threading.Thread(
                    target=server.HandleTCP,
                    args=(
                        now_TCPfd,
                        now_addr,
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