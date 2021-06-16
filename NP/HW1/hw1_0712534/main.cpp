#include <iostream>
#include <fstream>
#include <sstream>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <fcntl.h>
#include <unistd.h>
#include <cmath>
#include <vector>
#include "set_client.h"
#include "set_cmd.h"

using namespace std;

extern map<int, string> clients;
//extern int current_port;
extern int current_sockfd;
extern int Tsockfd, Usockfd;
extern fd_set allset, rset;
timeval timeout = {3, 0};
const int MAX_LEN = 2048;

struct sockaddr_in serv_addr;
struct sockaddr_in cli_addr;    //UDP
struct sockaddr_in client_addr; //TCP
socklen_t addr_len = sizeof(struct sockaddr_in);

void handle_new_connection(int);
void handle_TCP(int);
void handle_UDP(int sockfd);

void error(const char *msg)
{
    perror(msg);
    exit(1);
}

int main(int argc, char *argv[])
{
    if (argc < 2)
    {
        printf("Usage: ./server [port]\n");
        exit(EXIT_FAILURE);
    }

    // socket(int domain, int type, int protocol)
    Tsockfd = socket(AF_INET, SOCK_STREAM, 0); //TCP socket
    Usockfd = socket(AF_INET, SOCK_DGRAM, 0);  //UDP socket
    int max_fd = Tsockfd + Usockfd;
    if (Tsockfd < 0 || Usockfd < 0)
        error("ERROR opening socket");

    // clear address structure
    bzero((char *)&serv_addr, sizeof(serv_addr));

    // setup the host_addr structure
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = htonl(INADDR_ANY); //every connected cliend
    serv_addr.sin_port = htons(atoi(argv[1]));

    // TCP/UDP bind
    if (bind(Tsockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0)
        error("ERROR on Tbinding");

    if (bind(Usockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0)
        error("ERROR on Ubinding");

    //TCP listen
    listen(Tsockfd, 30);

    //clear
    FD_ZERO(&allset);
    //add Tsockfd/Usockfd
    FD_SET(Tsockfd, &allset);
    FD_SET(Usockfd, &allset);

    init_clients();

    while (true)
    {
        rset = allset;
        while (select(max_fd + 1, &rset, NULL, NULL, NULL) < 0)
            ;

        // new client
        if (FD_ISSET(Tsockfd, &rset))
        {

            socklen_t client_addr_len = sizeof(client_addr);
            int client_sockfd;
            while ((client_sockfd = accept(Tsockfd, (struct sockaddr *)&client_addr, &client_addr_len)) < 0)
                ;
            current_sockfd = client_sockfd;
            FD_SET(client_sockfd, &allset);
            //int port = client_sockfd.sin_port;
            max_fd = max(max_fd, client_sockfd + Usockfd);
            handle_new_connection(client_sockfd);
        }

        // old TCP client
        map<int, int>::iterator it;
        for (it = clifd_to_ramd.begin(); it != clifd_to_ramd.end(); it++)
        {
            int sockfd = it->first;
            if (!FD_ISSET(sockfd, &rset))
                continue;
            handle_TCP(sockfd);
        }
        //udp message
        if (FD_ISSET(Usockfd, &rset))
        {
            handle_UDP(Usockfd);
        }
    }
    return 0;
}

void handle_new_connection(int sockfd)
{
    printf("New connection.\n");

    char msg[] = "********************************\n"
                 "** Welcome to the BBS server. **\n"
                 "********************************\n"
                 "% ";
    write(sockfd, msg, strlen(msg));

    add_client(current_sockfd);
}

void handle_TCP(int sockfd)
{
    char buf[MAX_LEN];
    memset(buf, 0, sizeof(buf));
    int n = read(sockfd, buf, MAX_LEN);

    string input = buf;
    input = input + " ";
    input[n + 1] = '\0';

    current_sockfd = sockfd;

    string tmp = execute(input);
    if (tmp == "F")
        write(sockfd, "% ", strlen("% "));
}
void handle_UDP(int sockfd)
{

    char buf[2048];
    memset(buf, 0, sizeof(buf));
    int n = recvfrom(sockfd, buf, MAX_LEN, 0, (struct sockaddr *)&cli_addr, &addr_len);

    string input = buf;
    input[n + 1] = '\0';

    string output = execute(input);
    char msg[output.length() + 5];
    sprintf(msg, "%s", output.c_str());

    sendto(sockfd, msg, strlen(msg), 0, (struct sockaddr *)&cli_addr, addr_len);
}