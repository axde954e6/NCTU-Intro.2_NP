CPP = g++
CFLAGS = -g -Wall
TARGET_server = server
TARGET_client = client


all: $(TARGET_server)

server: main.cpp
	$(CPP) $(CFLAGS) -o $(TARGET_server) main.cpp
	$(CPP) $(CFLAGS) -o $(TARGET_client) client.cpp

clean: 
	rm -f $(TARGET_server)
	rm -f $(TARGET_client)