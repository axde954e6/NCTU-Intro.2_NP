import socket
import select
import json
import threading
import sys
import datetime

chatroomstate = "NOT_EXIST"
event = threading.Semaphore(0)


class server_info(object):
    def __init__(self, username, IP, port):
        self.username = username
        self.IP = str(IP)
        self.port = int(port)


def create_socket(IP, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  #reset socket
    #server.setblocking(0)
    IP_address = str(IP)
    Port = int(port)

    server.bind((IP_address, Port))
    #binds the server to an entered IP address and at the specified port number. The client must be aware of these parameters
    server.listen(10)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return server


list_of_clients = []
his_msg = []
inputs = []
Handle_CMD = ['INITIAL', "leave-chatroom"]


def GetClientMsg(conn, content, server_INFO):

    try:
        global his_msg

        message = content["msg"]
        username = content["username"]
        now_date = datetime.datetime.now()
        nowtime = "[" + str(now_date.hour) + ":" + str(now_date.minute) + "]"
        #print("receive msg")
        if message:

            if message in Handle_CMD or ( message=="detach" and username==server_INFO.username) :
                #print("INIT")
                Handle_msg(content, conn, server_INFO)
            else:

                sendmsg = username + nowtime + " : " + message
                #print(sendmsg)
                his_msg.append(sendmsg)
                if len(his_msg) > 3:
                    his_msg = his_msg[-3:]
                broadcast(sendmsg, conn)
                #prints the message and address of the user who just sent the message on the server terminal
        else:
            remove(conn)
    except:
        return


def broadcast(message, connection):
    for clients in list_of_clients:
        #print(clients)
        if clients != connection:
            try:
                clients.send(message.encode())
            except:
                clients.close()
                remove(clients)


def remove(connection):
    if connection in list_of_clients:
        list_of_clients.remove(connection)


def Handle_msg(content, conn, server_INFO):

    message = content["msg"]
    username = content["username"]
    now_date = datetime.datetime.now()
    nowtime = "[" + str(now_date.hour) + ":" + str(now_date.minute) + "]"
    if message == "INITIAL":
        msg = "*" * 29 + "\n** Welcome to the chatroom **\n" + "*" * 29
        global his_msg
        for it in his_msg:
            msg = msg + "\n" + it
        conn.send(msg.encode())
        #sends a message to the client whose user object is conn
        if username != server_INFO.username:
            sysmsg = "sys " + nowtime + " : " + username + " join us."
            broadcast(sysmsg, conn)
    elif message == "detach":
        if username != server_INFO.username:
            sysmsg = "sys " + nowtime + " : " + username + " leave us."
            broadcast(sysmsg, conn)
        inputs.remove(conn)
        list_of_clients.remove(conn)
        remove(conn)
        conn.close()
        event.release()
        return

    elif message == "leave-chatroom":
        if username == server_INFO.username:
            sysmsg = "sys " + nowtime + " : the chatroom is close."
            broadcast(sysmsg, conn)
            global chatroomstate
            chatroomstate = "close"
            event.release()
        else:
            sysmsg = "sys " + nowtime + " : " + username + " leave us."
            broadcast(sysmsg, conn)
            inputs.remove(conn)
            remove(conn)
            conn.close()

        return


def ChatServer(username, IP, port):
    #server = create_socket(IP, port)
    server_INFO = server_info(username, IP, port)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  #reset socket
    server.setblocking(0)

    server.bind((server_INFO.IP, server_INFO.port))
    #binds the server to an entered IP address and at the specified port number. The client must be aware of these parameters
    server.listen(10)
    event.release()
    #print("server" + IP + " " + str(port) + " " + username)
    global inputs
    inputs = [server]
    while True:
        readable, write_socket, error_socket = select.select(inputs, [], [])
        for sck in readable:
            if sck is server:

                conn, addr = server.accept()
                list_of_clients.append(conn)
                conn.setblocking(0)
                inputs.append(conn)
                #print("NEW CLIENT " + str(conn))
            else:
                #print("OLD CLIENT")
                msg = sck.recv(2048).decode()
                content = json.loads(msg)
                message = content["msg"]
                username = content["username"]
                GetClientMsg(sck, content, server_INFO)
                if message == "leave-chatroom" and username == server_INFO.username:
                    for it in list_of_clients:
                        remove(it)
                    server.close()
                    return


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Correct usage: script, IP address, port number")
        exit()
    ChatServer(str(sys.argv[3]), str(sys.argv[1]), int(sys.argv[2]))
