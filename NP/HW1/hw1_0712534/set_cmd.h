#pragma once

#include <iostream>
#include <cstdlib>
#include <vector>
#include <map>
#include <unistd.h>
#include <cmath>
#include "set_client.h"

using namespace std;

extern map<int, string> clients;
extern map<int, int> clifd_to_ramd;
extern int current_sockfd;

//Function

struct User
{
    string email;
    string password;
    string username;
    User(string email = "", string password = "", string username = "") : email(email), password(password), username(username) {}
};

map<string, User> users; // username -> User

string execute_register(const vector<string> &args)
{
    string str;
    if (args.size() != 3)
    {
        str = "Usage: register <username> <email> <password>\n% ";
        return str;
    }

    string username = args.at(0);
    string email = args.at(1);
    string password = args.at(2);
    if (users.find(username) != users.end())
    {
        str = "Username is already used.\n% ";
        return str;
    }
    users[username] = User(email, password, username);
    str = "Register successfully.\n% ";
    return str;
}

void execute_login(const vector<string> &args, int fd)
{
    if (args.size() != 2)
    {
        send_message("Usage: login <username> <password>\n");
        return;
    }
    string username = args.at(0);
    string password = args.at(1);

    if (clifd_to_ramd[fd] != 0)
    {
        send_message("Please logout first.\n");
        return;
    }
    if (users.find(username) == users.end())
    {
        send_message("Login failed.\n");
        return;
    }

    if (users[username].password != password)
    {
        send_message("Login failed.\n");
        return;
    }

    int randid = rand() % 50000 + 1;
    clifd_to_ramd[current_sockfd] = randid;
    clients[randid] = username;
    send_message(to_string(randid) + " Welcome, " + username + ".\n");
}

void execute_logout()
{
    int id = clifd_to_ramd[current_sockfd];
    string current_username = clients[id];
    if (current_username == "")
    {
        send_message("Please login first.\n");
        return;
    }
    clients[id] = "";
    clifd_to_ramd[current_sockfd] = 0;
    send_message("Bye, " + current_username + ".\n");
}

string execute_whoami(const vector<string> &args)
{
    string str = args.at(0);
    int id = 0;
    for (int i = 0; i < str.length(); i++)
    {
        if (str[i] > '9' || str[i] < '0')
            break;
        id *= 10;
        id += str[i] - '0';
    }

    string tmp;
    if (id == 0)
    {
        tmp = "Please login first.\n% ";

        return tmp;
    }
    string current_username = clients[id];

    tmp = current_username;
    tmp = tmp + "\n" + "% ";
    return tmp;
}

void execute_list()
{

    string str = "Name\tEmail\n";
    map<string, User>::iterator iter;
    for (iter = users.begin(); iter != users.end(); iter++)
    {
        str = str + iter->first + "\t" + iter->second.email + "\n";
    }
    send_message(str);
}

//command
// remove space in the beginning of str
void remove_space(string &str)
{
    str.erase(0, str.find_first_not_of(" ")); //space before str
    str.erase(str.find_last_not_of(" ") + 1); //space after str
}

string split(string &str, string delim)
{
    int pos = str.find(delim);
    string res = str.substr(0, pos);
    str.erase(0, pos);
    return res;
}

vector<string> parse(string input)
{
    vector<string> args;
    args.clear();
    while (input.length() > 0)
    {
        remove_space(input);
        if (input.length() == 0)
            break;

        string arg = split(input, " ");
        while (arg[0] == ' ')
        {
            int i;
            for (i = 0; i < arg.length() - 1; i++)
            {
                arg[i] = arg[i + 1];
            }
            arg[i] = '\0';
        }
        args.push_back(arg);
    }
    return args;
}

string execute(string input)
{
    remove_space(input);

    string cmd_name = split(input, " "); //get cmd

    vector<string> args = parse(input); //get args

    if (cmd_name == "register")
    {

        return execute_register(args);
    }
    if (cmd_name == "login")
    {

        execute_login(args, current_sockfd);
        return "";
    }
    if (cmd_name == "logout")
    {
        execute_logout();
        return "";
    }
    if (cmd_name == "whoami")
    {

        return execute_whoami(args);
    }
    if (cmd_name == "exit")
    {
        remove_client();
        return "";
    }
    if (cmd_name == "list-user")
    {
        execute_list();
        return "";
    }
    return "F";
}
