# File Transfer Service

Simulated the file transfer protocol (FTP) over TCP sockets using a client-server architecture in Python

## Usage

### Step 0: Set Up and Activate Virtual Environment

#### For Mac/Linux

```
pip3 install virtualenv
virtualenv env
source env/bin/activate
```

#### For Windows

```
pip install virtualenv
virtualenv env
~\env\Scripts\activate
```

### Step 1: Open Two Terminals Sessions - One for Client, Another for Server

### Step 2: Enter the Server Directory and Run the Server Program on the Dedicated Server Terminal

server/ directory contains all the files on the server machine, including the serverside code

> Simplifies accessing and storing files within server/ directory when running server program (same path)

```
cd server/
python3 server.py
```

TODO: Write instructions with ip port debug mode

Note: Must Start Serverside Code Before Clientside Code

> Server must be listening and waiting for client connection
>
> Server Socket First Initialized \
> Server Binds Hostname Address and Port Number to Server Side Socket \
> -> Start Listening for Client Side to Connect with Same Hostname and Port

> Server Socket Listens for Client

### Step 3: Enter the Client Directory and Run the Client Program on the Dedicated Client Terminal

client/ directory contains all the files on the client machine

> Simplifies accessing and storing files within client/ directory when running client program (same path)

```
cd client/
python3 client.py
```

> Client Socket Then Initialized \
> Client Socket Connects to Server Side Socket using Same Hostname and Port

> Once Server Accepts Connection, Client Can Create, Serialize and Send Request to Server \
> Server Receives and Deserializes Data to then Create, Serialize, and Send a Response to Client

> Client Receives and Deserializes Data, Receiving a Response for a Given Request

TODO: Write instructions with ip port debug mode

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
