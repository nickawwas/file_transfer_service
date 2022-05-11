# File Transfer Service

Simulated the file transfer protocol (FTP) over TCP sockets using a client-server architecture in Python \
Performed unit testing by mocking standard input and output for each command

## Usage

### Step 0: Move Test Files into Either Client or Server Directory

Setup client and server machines with initial files

server/ directory represents the server machine, containing all the files on the server machine

client/ directory represents the client machine, containing all the files on the client machine

### Step 1: Open Two Terminals Sessions - One for Client, Another for Server

### Step 2: Enter the Server Directory and Run the Server Program on the Dedicated Server Terminal

server/ directory represents the server machine, containing all the files on the server machine - including the serverside code

> Simplifies accessing and storing files within server/ directory when running server program (same path)

```
cd server/
```

> Running the serverside code can be done by specifying the ip address, port number and debug mode status flag

```
# Usage Format
p3 server.py ip_address port_number debug_mode

# Specifying None Defaults to 127.0.0.1:65432 with Debug Mode Disabled (0)
p3 server.py

# Specifying Some or All Fields Overrides Defaults
p3 server.py 127.0.0.1
p3 server.py 127.0.0.1 65432
p3 server.py 127.0.0.1 65432 1
```

Note: Must Start Serverside Code Before Clientside Code

> Server socket first initialized
> Attach IP address and port number to serverside socket
> Listen on specified hostname and port, waiting for client connection

### Step 3: Enter the Client Directory and Run the Client Program on the Dedicated Client Terminal

client/ directory represents the client machine, containing all the files on the client machine

> Simplifies accessing and storing files within client/ directory when running client program (same path)

```
cd client/
```

> Running the clientside code can be done by specifying the ip address, port number and debug mode status flag

```
# Usage Format
p3 client.py ip_address port_number debug_mode

# Specifying None Defaults to 127.0.0.1:65432 with Debug Mode Disabled (0)
p3 client.py

# Specifying All Fields Overrides Defaults
p3 client.py 127.0.0.1
p3 client.py 127.0.0.1 65432
p3 client.py 127.0.0.1 65432 1
```

Note: IP Address and Port Number Must Match the Ones Specified on the Server Socket

> Client socket then initialized \
> Connect to serverside socket using IP address and port number \
> Once Server Accepts Connection, Client Can Create, Serialize and Send Request to Server \
> Server Receives and Deserializes Data to then Create, Serialize, and Send a Response to Client \
> Client Receives and Deserializes Data, Receiving a Response for a Given Request \

### Step 4: Enter the Commands in Client Terminal

> Sample Commands

```
# Transfer File from Client to Server
put client_file.txt

# Transfer File from Server to Client
get server_file.txt

# Rename File on Server
change old_server_file.txt new_server_file.txt

# Provides List of Commands
help

# Closes Client Connection
bye
```

### [Optional] Step 5: End Client Session and Open New Session

> User may close/end the client session \
> Server will close old connection and listen for new connections\
