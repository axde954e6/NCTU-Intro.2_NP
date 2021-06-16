# -*- coding: UTF-8 -*-
import json
import datetime
import threading
from socket import *

mutex = threading.Lock()
have_space = ["create-post", "update-post", "comment"]

##### global class #####
chat_info = {}


class info(object):
    Session = {}
    user_password = {}
    user_email = {}
    board = {}
    post = {}

    def _init_(self):
        self.Session = {}
        self.user_password = {}
        self.user_email = {}
        self.board = {}
        self.post = {}


class chat(object):
    def __init__(self, port, status, IP):
        self.IP = str(IP)
        self.port = int(port)
        self.status = status


user_info = info()
"""
Session = {}   session id -> user_name
user_password = {}  user_name -> password
user_email = {}   user_name -> email
board = {}   board_name -> {"Moderator","have_post_SN":[]}
post =  {}  post_serial_number -> {"title",content","Author","Date","comment":{username:comment},"board_name"}
"""


def split_arg(cmd, content):
    if cmd not in have_space:
        Arg = content["msg"].split()
    else:
        t_pos = content["msg"].find("--title")
        c_pos = content["msg"].find("--content")
        Arg = []
        Arg.append(cmd)
        temp = content["msg"].split()
        if cmd == "create-post":
            if len(temp) < 6 or c_pos == -1 or t_pos == -1:
                return []
            b_name = content["msg"].split()[1]
            Arg.append(b_name)
            t_name = content["msg"][t_pos + len("--title"):c_pos].strip()
            Arg.append(t_name)
            c_msg = content["msg"][c_pos + len("--content"):].lstrip()
            c_msg = c_msg.replace("<br>", "\n")
            Arg.append(c_msg)
        if cmd == "update-post":
            if len(temp) < 4 or (c_pos == -1 and t_pos == -1):
                return []
            if c_pos != -1:
                s_num = content["msg"].split()[1]
                Arg.append(s_num)
                Arg.append("--content")
                c_msg = content["msg"][c_pos + len("--content"):].lstrip()
                c_msg = c_msg.replace("<br>", "\n")
                Arg.append(c_msg)
            elif t_pos != -1:
                s_num = content["msg"].split()[1]
                Arg.append(s_num)
                Arg.append("--title")
                t_name = content["msg"][t_pos + len("--title"):].lstrip()
                Arg.append(t_name)
        if cmd == "comment":
            if len(temp) < 3:
                return []
            s_num = content["msg"].split()[1]
            Arg.append(s_num)
            pos = content["msg"].find(s_num)
            comment_msg = content["msg"][pos + len(s_num):].lstrip()
            Arg.append(comment_msg)

    return Arg


class ServerService(object):
    def __init__(self):
        self.next_serial_number = 1

    def HandleTCP(self, sockfd, saddr):
        try:
            while True:
                msg = sockfd.recv(1024).decode()
                content = json.loads(msg)
                cmd = content["msg"].split(" ")[0]
                servmsg = self.HandleClientMsg(msg, saddr)
                if cmd == "exit":
                    sockfd.close()
                    return
                sockfd.send(servmsg.encode())
        except KeyboardInterrupt:
            return

    def HandleUDP(self, sockfd):
        try:
            while True:
                msg, addr = sockfd.recvfrom(1024)
                msg = msg.decode()
                servmsg = self.HandleClientMsg(msg, addr)
                sockfd.sendto(servmsg.encode(), (addr[0], addr[1]))
        except KeyboardInterrupt:
            return

    def HandleClientMsg(self, msg, addr):

        global user_info
        get_port = 0
        content = json.loads(msg)
        cmd = content["msg"].split()[0]
        sessionID = content["sid"]

        Arg = split_arg(cmd, content)
        servmsg = ""
        if cmd == "INITIAL" and sessionID == -1:
            print("New connection.")
            mutex.acquire()
            sessionID = len(user_info.Session)
            user_info.Session[sessionID] = ""
            mutex.release()
            servmsg = "*" * 32 + "\n** Welcome to the BBS server. **\n" + "*" * 32

        elif cmd == "register":
            if len(Arg) != 4:
                servmsg = "Usage: register <username> <email> <password>"
            else:
                mutex.acquire()
                if user_info.user_password.get(Arg[1]) != None:
                    servmsg = "Username is already used."
                else:
                    user_info.user_password[Arg[1]] = Arg[3]
                    user_info.user_email[Arg[1]] = Arg[2]
                    servmsg = "Register successfully."
                mutex.release()

        elif cmd == "login":
            if len(Arg) != 3:
                servmsg = "Usage: login <username> <password>"
            else:
                mutex.acquire()
                if (user_info.Session[sessionID] != ""
                        and Arg[1] == user_info.Session[sessionID]):
                    servmsg = "Please logout first."
                else:
                    if user_info.user_password.get(Arg[1]) != None:
                        if Arg[2] == user_info.user_password[Arg[1]]:
                            user_info.Session[sessionID] = Arg[1]
                            servmsg = f"Welcome, {Arg[1]}."
                        else:
                            servmsg = "Login failed."
                    else:
                        servmsg = "Login failed."
                mutex.release()

        elif cmd == "logout":
            if len(Arg) != 1:
                servmsg = "Usage: logout"
            else:
                mutex.acquire()
                if user_info.Session[sessionID] == "":
                    servmsg = "Please login first."
                elif user_info.Session[sessionID] in chat_info and chat_info[
                        user_info.Session[sessionID]].status == "open":
                    servmsg = "Please do “attach” and “leave-chatroom” first"
                else:
                    logout_name = user_info.Session[sessionID]
                    servmsg = f"Bye, {logout_name}."
                    user_info.Session[sessionID] = ""

                mutex.release()

        elif cmd == "list-user":
            servmsg = "Name\tEmail"
            mutex.acquire()
            for k, v in user_info.user_email.items():
                servmsg += "\n" + k + "\t" + v
            mutex.release()

        elif cmd == "whoami":
            if len(Arg) != 1:
                servmsg = "Usage: whoami"
            else:
                if user_info.Session[sessionID] == "":
                    servmsg = "Please login first."
                else:
                    servmsg = user_info.Session[sessionID]

        elif cmd == "create-board":
            if len(Arg) != 2:
                servmsg = "Usage: create-board <name>"
            else:
                mutex.acquire()
                if user_info.Session[sessionID] == "":
                    servmsg = "Please login first."
                elif user_info.board.get(Arg[1]) != None:
                    servmsg = "Board already exists."
                else:
                    servmsg = "Create board successfully."
                    user_info.board[Arg[1]] = {
                        "Moderator": user_info.Session[sessionID],
                        "have_post_SN": [],
                    }
                mutex.release()

        elif cmd == "create-post":
            if len(Arg) != 4:
                servmsg = (
                    "Usage create-post <board-name> --title <title> --content <content>"
                )
            else:
                mutex.acquire()
                if user_info.Session[sessionID] == "":
                    servmsg = "Please login first."
                elif user_info.board.get(Arg[1]) == None:
                    servmsg = "Board does not exist."
                else:
                    now_date = datetime.datetime.now()
                    date = str(now_date.month) + "/" + str(now_date.day)
                    servmsg = "Create post successfully."
                    new_post = {
                        "title": Arg[2],
                        "content": Arg[3],
                        "Author": user_info.Session[sessionID],
                        "Date": date,
                        "comment": [],
                        "board_name": Arg[1],
                    }
                    user_info.post[self.next_serial_number] = new_post
                    # add SN to board
                    user_info.board[Arg[1]]["have_post_SN"].append(
                        int(self.next_serial_number))
                    self.next_serial_number = self.next_serial_number + 1
                mutex.release()

        elif cmd == "list-board":
            servmsg = "Index\tName\tModerator"
            index = 1
            mutex.acquire()
            for it in user_info.board:
                servmsg = (servmsg + "\n" + str(index) + "\t" + str(it) +
                           "\t" + str(user_info.board[it]["Moderator"]))
                index = index + 1
            mutex.release()

        elif cmd == "list-post":
            if len(Arg) != 2:
                servmsg = "Usage list-post <board-name>"
            else:
                mutex.acquire()
                if Arg[1] not in user_info.board:
                    servmsg = "Board does not exist."
                else:
                    servmsg = "S/N\tTitle\tAuthor\tDate"
                    for it in user_info.board[Arg[1]]["have_post_SN"]:
                        if it not in user_info.post:
                            continue
                        servmsg = (servmsg + "\n" + str(it) + "\t" +
                                   user_info.post[int(it)]["title"] + "\t" +
                                   user_info.post[int(it)]["Author"] + "\t" +
                                   user_info.post[int(it)]["Date"])
                mutex.release()

        elif cmd == "read":
            if len(Arg) != 2:
                servmsg = "Usage read <post-S/N>"
            else:
                mutex.acquire()
                if int(Arg[1]) not in user_info.post:
                    servmsg = "Post does not exist."
                else:
                    get_post = user_info.post[int(Arg[1])]
                    servmsg = ("Author: " + get_post["Author"] + "\nTitle: " +
                               get_post["title"] + "\nDate: " +
                               get_post["Date"] + "\n--\n")
                    servmsg = servmsg + get_post["content"] + "\n--"
                    for it in get_post["comment"]:
                        servmsg = servmsg + "\n" + \
                            it["username"] + ": " + it["comment"]
                mutex.release()

        elif cmd == "delete-post":
            if len(Arg) != 2:
                servmsg = "Usage delete-post <post-S/N>"
            else:
                mutex.acquire()
                if user_info.Session[sessionID] == "":
                    servmsg = "Please login first."
                elif int(Arg[1]) not in user_info.post:
                    servmsg = "Post does not exist."
                elif (user_info.Session[sessionID] != user_info.post[int(
                        Arg[1])]["Author"]):
                    servmsg = "Not the post owner."
                else:
                    board_name = user_info.post[int(Arg[1])]["board_name"]
                    del user_info.post[int(Arg[1])]
                    user_info.board[board_name]["have_post_SN"].remove(
                        int(Arg[1]))
                    servmsg = "Delete successfully."
                mutex.release()

        elif cmd == "update-post":
            if len(Arg) != 4:
                servmsg = "Usage update-post <post-S/N> --title/content <new>"
            else:
                mutex.acquire()
                if user_info.Session[sessionID] == "":
                    servmsg = "Please login first."
                elif int(Arg[1]) not in user_info.post:
                    servmsg = "Post does not exist."
                elif (user_info.Session[sessionID] != user_info.post[int(
                        Arg[1])]["Author"]):
                    servmsg = "Not the post owner."
                else:
                    if Arg[2] == "--title":
                        user_info.post[int(Arg[1])]["title"] = Arg[3]
                    else:
                        user_info.post[int(Arg[1])]["content"] = Arg[3]
                    servmsg = "Update successfully."
                mutex.release()

        elif cmd == "comment":
            if len(Arg) != 3:
                servmsg = "Usage comment <post-S/N> <comment>"
            else:
                mutex.acquire()
                if user_info.Session[sessionID] == "":
                    servmsg = "Please login first."
                elif int(Arg[1]) not in user_info.post:
                    servmsg = "Post does not exist."
                else:
                    user_info.post[int(Arg[1])]["comment"].append({
                        "username":
                        user_info.Session[sessionID],
                        "comment":
                        Arg[2]
                    })
                    servmsg = "Comment successfully."
                mutex.release()

        elif cmd == "create-chatroom":
            if len(Arg) != 2:
                servmsg = "Usage create-chatroom <port>."
            elif user_info.Session[sessionID] == "":
                servmsg = "Please login first."
            elif user_info.Session[sessionID] in chat_info:
                servmsg = "User has already created the chatroom."
            else:
                servmsg = "start to create chatroom..."
                temp = chat(Arg[1], "open", "")
                chat_info[user_info.Session[sessionID]] = temp
                get_port = Arg[1]

        elif cmd == "list-chatroom":
            if user_info.Session[sessionID] == "":
                servmsg = "Please login first."
            else:
                servmsg = "Chatroom_name\tStatus"
                for it in chat_info:
                    servmsg = servmsg + "\n" + it + "\t" + chat_info[it].status

        elif cmd == "join-chatroom":
            if len(Arg) != 2:
                servmsg = "Usage join-chatroom <chatroom_name>"
            elif user_info.Session[sessionID] == "":
                servmsg = "Please login first."
            elif Arg[1] not in chat_info or chat_info[
                    Arg[1]].status == "close":
                servmsg = "The chatroom does not exist or the chatroomis close."
            else:
                servmsg = "enter chat room"
                get_port = chat_info[Arg[1]].port

        elif cmd == "restart-chatroom":
            if user_info.Session[sessionID] == "":
                servmsg = "Please login first."
            elif user_info.Session[sessionID] not in chat_info:
                servmsg = "Please create-chatroom first."
            elif chat_info[user_info.Session[sessionID]].status == "open":
                servmsg = "Your chatroom is still running."
            else:
                servmsg = "start to create chatroom..."
                chat_info[user_info.Session[sessionID]].status = "open"
                get_port = chat_info[user_info.Session[sessionID]].port

        elif cmd == "exit":
            mutex.acquire()
            user_info.Session[sessionID] = None
            mutex.release()
            sessionID = -1
            return
        elif cmd == "ENDCHATROOM":
            servmsg = "Welcome back to BBS."
            chat_info[user_info.Session[sessionID]].status = "close"

        elif cmd == "EXITCHAT":
            servmsg = "Welcome back to BBS."

        elif cmd == "attach":
            if user_info.Session[sessionID] == "":
                servmsg = "Please login first."
            elif user_info.Session[sessionID] not in chat_info:
                servmsg = "Please create-chatroom first."
            else:
                servmsg = "ATTACH"
                get_port = chat_info[user_info.Session[sessionID]].port
        else:
            servmsg = f"{cmd}: Command not found!"
        return json.dumps({
            "msg": servmsg,
            "sid": sessionID,
            "username": user_info.Session[sessionID],
            "get_port": get_port
        })
