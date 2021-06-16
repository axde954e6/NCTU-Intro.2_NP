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

using namespace std;
struct sockaddr_in server_addr;
int id = 0;
const int MAX_LEN = 2048;
char buf[MAX_LEN];
int Tsockfd, Usockfd;
int login, logout, whoami, regis;
socklen_t addr_len = sizeof(struct sockaddr_in);

int Tcreate_socket(string, int);
int Ucreate_socket(string, int);
int send_to_server(string);
void read_from_server(int);
string split(string &str, string delim);

int main(int argc, char *argv[])
{
    if (argc != 3)
    {
        printf("Usage: ./client [ip] [port]\n");
        exit(EXIT_FAILURE);
    }

    Tsockfd = Tcreate_socket(string(argv[1]), atoi(argv[2])); //TCP socket
    Usockfd = Ucreate_socket(string(argv[1]), atoi(argv[2])); //UDP socket

    read_from_server(1);

    while (true)
    {
        string input;
        getline(cin, input);
        string temp = input;
        string getcmd = split(temp, " ");

        if (getcmd == "login")
            login = 1;
        else
            login = 0;
        if (getcmd == "logout")
            logout = 1;
        else
            logout = 0;
        if (getcmd == "whoami")
            whoami = 1;
        else
            whoami = 0;
        if (getcmd == "register")
            regis = 1;
        else
            regis = 0;

        int TorU = send_to_server(input);

        if (input[0] == 'e')
        {
            close(Usockfd);
            close(Tsockfd);
            break;
        }

        read_from_server(TorU);
    }

    return 0;
}

int Tcreate_socket(string ip, int port)
{
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    bzero(&server_addr, sizeof(server_addr));

    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = inet_addr(ip.c_str());
    server_addr.sin_port = htons(port);

    int optval = 1;
    if (setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, (const void *)&optval, sizeof(int)) == -1)
    {
        printf("Error: setsockopt() failed\n");
        exit(EXIT_FAILURE);
    }

    if (connect(fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
    {
        printf("Error: connect() failed\n");
        exit(EXIT_FAILURE);
    }
    return fd;
}

int Ucreate_socket(string ip, int port)
{

    int fd = socket(AF_INET, SOCK_DGRAM, 0);
    bzero(&server_addr, sizeof(server_addr));

    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = inet_addr(ip.c_str());
    server_addr.sin_port = htons(port);

    return fd;
}

int send_to_server(string message)
{

    if (whoami)
    {
        message += " ";
        message += to_string(id); //send message with client port
    }
    int tmp = 1; //TCP
    if (whoami || regis)
    {

        char msg[message.length() + 5];
        sprintf(msg, "%s", message.c_str());
        sendto(Usockfd, msg, strlen(msg), 0, (struct sockaddr *)&server_addr, addr_len);
        tmp = 0; //UDP
    }
    else
    {

        char msg[message.length()];
        sprintf(msg, "%s", message.c_str());
        write(Tsockfd, msg, strlen(msg));
    }
    return tmp;
}

void read_from_server(int TU)
{
    memset(buf, 0, sizeof(buf));
    if (TU == 1) //TCP
        read(Tsockfd, buf, MAX_LEN);
    else if (TU == 0) //UDP
        recvfrom(Usockfd, buf, MAX_LEN, 0, (struct sockaddr *)&server_addr, &addr_len);

    string response = string(buf);
    if (login && response[0] <= '9' && response[0] >= '0')
    {
        string temp = split(response, " ");
        for (int i = 0; i < temp.length(); i++) //set current port
        {
            if (temp[i] > '9' || temp[i] < '0')
                break;
            id *= 10;
            id += temp[i] - '0';
        }
    }
    if (logout)
        id = 0;

    cout << response << flush;
}

string split(string &str, string delim)
{
    int pos = str.find(delim);
    string res = str.substr(0, pos);
    str.erase(0, pos);
    str.erase(0, str.find_first_not_of(" "));
    return res;
}