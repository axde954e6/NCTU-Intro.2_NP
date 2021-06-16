#pragma once

#include <iostream>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <map>
#include <sys/types.h>
#include <unistd.h>

using namespace std;

map<int, string> clients; // randid -> username

map<int, int> clifd_to_ramd; //fd->randid

int current_sockfd;
int Tsockfd, Usockfd;
fd_set allset, rset;

void init_clients()
{
    clients.clear();
    clifd_to_ramd.clear();
}

void add_client(int fd)
{ // when a client connect to server

    clifd_to_ramd[fd] = 0;
}

void remove_client()
{ // when a client quit the connection
    int id = clifd_to_ramd[current_sockfd];
    clifd_to_ramd.erase(current_sockfd);
    clients.erase(id);
    FD_CLR(current_sockfd, &allset);
    close(current_sockfd);
}

void send_message(string message)
{
    message = message + "% ";
    char msg[message.length() + 5];
    sprintf(msg, "%s", message.c_str());
    write(current_sockfd, msg, strlen(msg));
}