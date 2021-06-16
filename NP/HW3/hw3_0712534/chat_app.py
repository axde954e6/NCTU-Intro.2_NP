import socket
import select
import json
import sys


class chat_info(object):
    def __init__(self, username, IP, port):
        self.username = username
        self.IP = str(IP)
        self.port = int(port)

server_username=""

def chatroom_APP(username, IP, port):
    chat_INFO = chat_info(username, IP, port)
    #print(chat_INFO.username + "|" + chat_INFO.IP)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((chat_INFO.IP, chat_INFO.port))
    sendmsg = json.dumps({'msg': "INITIAL", 'username': chat_INFO.username})
    server.send(sendmsg.encode())
    #message = server.recv(2048).decode()
    #print(message)
    #print("client " + username + " " + IP + " " + str(port))
    while True:
        sendmsg = ""
        sockets_list = [sys.stdin, server]
        read_sockets, write_socket, error_socket = select.select(
            sockets_list, [], [])
        for socks in read_sockets:
            if socks == server:
                message = socks.recv(2048).decode()
                if message:
                    print(message)
                    if message.find("the chatroom is close") != -1:
                        server.close()
                        return
            else:
                message = sys.stdin.readline()
                if message.find("\n") != 0:
                    message = message[:message.find("\n")]

                sendmsg = json.dumps({
                    'msg': message,
                    'username': chat_INFO.username
                })
                server.send(sendmsg.encode())
                if (message == "detach" and username==server_username) or message == "leave-chatroom":
                    server.close()
                    read_sockets.clear()
                    return

        #read_sockets.clear()


def main():
    if len(sys.argv) != 4:
        print("Correct usage: script, IP address, port number")
        exit()
    #chat_INFO.username = sys.argv[3]
    chatroom_APP(sys.argv[3], sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
