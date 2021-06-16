#!/usr/bin/python3

from socket import *
import threading
import sys
from handle_function import *


server = ServerService()


def main():
    if len(sys.argv) != 2:
        print(f"\tUsage {sys.argv[0]} <Port>")
        exit(-1)
    HOSTNAME, ListenPort = "", int(sys.argv[1])

    TCPsockfd = socket(AF_INET, SOCK_STREAM)
    TCPsockfd.bind((HOSTNAME, ListenPort))
    TCPsockfd.listen(30)
    UDPsockfd = socket(AF_INET, SOCK_DGRAM)
    UDPsockfd.bind((HOSTNAME, ListenPort))

    global server

    # UDP_thread
    UDP_thread = threading.Thread(target=server.HandleUDP, args=(UDPsockfd,))
    UDP_thread.start()

    # TCP_thread
    TCP_thread = []
    try:
        while True:
            now_TCPfd, now_addr = TCPsockfd.accept()
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
    for sockfd in [TCPsockfd, UDPsockfd]:
        sockfd.close()
    return 0


if __name__ == "__main__":
    main()
