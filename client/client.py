# Nicholas Kawwas (40124338)
# COEN 366 Section WJ-X
# Purpose: Simulate FTP Service (Clientside code)
# Statement: Nicholas Kawwas is the Sole Author

from os.path import exists, getsize
from sys import stdout, argv
from socket import socket, AF_INET6, SOCK_STREAM

# TODO: Make Functions to Clean Up Code, Write Report 
# -> Fix Images and PDF by adding b to rb and wb to read and write the contents of the file in binary (no decoding necessary) 

# Specify IP Address and Port as First and Second Command Line Arguments
# Note - argv[1]: IP Address, argv[2]: Port
HOSTNAME = "127.0.0.1" if len(argv) < 2 else argv[1]
PORT = 65432 if len(argv) < 3 else int(argv[2])

# Specify Debug Mode as Third/Last Command Line Argument 
# Debug Mode: Off (0) - No Printing, On (1) - Printing Msgs Sent and Received
# Note - argv[3]: Debug Mode (Default 0)
DEBUG_MODE = 0 if len(argv) < 4 else int(argv[3])

# Print Warning Message with Different Colors
RESET = '\033[0;0m'
WARNING = '\033[1;31m'
def write_err_msg(msg):
    stdout.write(WARNING)
    print(f'Error - {msg}')
    stdout.write(RESET)

# Print Debug Request
def debug_req(req):
    if DEBUG_MODE:
        print("Request:", req)

# Print Debug Request
def debug_res(res):
    if DEBUG_MODE:
        print("Response:", res)

# Main Function Called in Script
def main():
    # Initialize Socket using AF_INET6 and SOCK_STREAM to Specify IPv6 and TCP Respectively 
    s = socket(AF_INET6, SOCK_STREAM)

    try:
        # Connect to Server Socket with Hostname and Port Number of 127.0.0.1:65432
        s.connect((HOSTNAME, PORT))
        print("Welcome to FTP Client!\n")

        while True:
            # Read User Commands
            user_cmd = input("")

            # Determine Request
            parsed_cmd = user_cmd.strip().split(" ")
            cmd = parsed_cmd[0]
            
            # Send Put Request to Transfer File from Client to Server
            if cmd == "put":
                # Opcode Specifies Request Operation Code (3 bits)
                # File Name Length (FL) Specifies Length of File Name (5 bits)
                # File Name Specifies Name of Transferred File
                # File Size (FS) Specifies Size of Transferred File
                # File Data Specifies Data in File Sent as Chunks of Data
                opcode = "000"

                # Check if File Name is Specified
                if len(parsed_cmd) < 2:
                    write_err_msg("No File Name Provided!")
                    print("usage: put fileName\n")
                    continue

                file_name = parsed_cmd[1]

                # Check if File Exists
                if not exists(file_name):
                    write_err_msg("No File with Provided Name on Client!\n")
                    continue
                
                file_len = len(file_name) + 1
                file_size = getsize(file_name)

                # Create Request Msg
                req_str = opcode + f'{file_len:05b}' + file_name + f'{file_size:032b}'
                req = req_str.encode()
                
                # Request: opcode file_len file_name file_size
                s.send(req)

                if DEBUG_MODE:
                    print("Request:", req_str)
                
                # Send file_data
                # - Read and Send Segmented File Line by Line
                with open(file_name, "r") as file:
                    lines = file.readlines()
                    for line in lines:
                        file_data = line.encode()
                        s.send(file_data)
        
                # Receive Response from Server
                # 1024 Represents Buffer Size in Bytes
                data = s.recv(1024)
                res = data.decode()

                # Get Status Code
                res_code = res[0:3]

                if DEBUG_MODE:
                    print("Response:", res)
                    print()
                
                res_status = "was successfully" if res_code == "000" else "failed to be"
                print(f"{file_name} {res_status} uploaded!\n")

            # Send Get Request to Transfer File from Server to Client
            elif cmd == "get":
                opcode =  "001"

                # Check if File Name is Specified
                if len(parsed_cmd) < 2:
                    write_err_msg("No File Name Provided!")
                    print("usage: get fileName\n")
                    continue

                file_name = parsed_cmd[1]
                file_len = len(file_name) + 1

                # Request: opcode file_len file_name
                # Create Request Msg
                req_str = opcode + f'{file_len:05b}' + file_name
                req = req_str.encode()
                
                # Request: opcode file_len file_name file_size
                s.send(req)

                if DEBUG_MODE:
                    print("Request:", req_str)

                # Receive Response from Server
                # 1024 Represents Buffer Size in Bytes
                data = s.recv(1024)
                res = data.decode()

                if DEBUG_MODE:
                    print("Response:", res)
                    print()

                # Get Status Code
                res_code = res[0:3]
                file_name_len = int(res[3:8], 2)

                if res_code == "001":
                    fn_end_ind = file_name_len + 7
                    fs_end_ind = fn_end_ind + 32
                    file_name = res[8:fn_end_ind]
                    file_size = int(res[fn_end_ind:fs_end_ind], 2)

                    # Get File Data
                    file_data = res[fs_end_ind:]

                    # Calculate Amount of File Missing
                    # Loop Until All File Data is Received
                    missing_file_size = file_size - len(file_data)
                    while missing_file_size > 0:
                        # Wait for Data and Update Amount of File Missing
                        data = s.recv(1024)

                        if not data:
                            break

                        file_data = file_data + data.decode()
                        missing_file_size = file_size - len(file_data)
    
                    # Send file_data
                    # - Read and Send Segmented File Line by Line
                    with open(file_name, "w") as file:
                        file.write(file_data)
                
                res_status = "was successfully" if res_code == "001" else "failed to be"
                print(f"{file_name} {res_status} downloaded!\n")

            # Send Change Request to Rename File on Server
            elif cmd == "change":
                # Old File Name Specifies Name of File to Change
                # New File Name Specifies New Name of File
                # Old File Name Length (OFL) Specifies Length of Old File Name (5 bits)
                # New File Name Length (NFL) Specifies Length of New File Name (1 Byte)
                opcode = "010"

                # Check if File Name is Specified
                if len(parsed_cmd) < 3:
                    write_err_msg("New or Old File Name Not Provided!")
                    print("usage: change oldFileName newFileName\n")
                    continue

                old_file_name = parsed_cmd[1]
                new_file_name = parsed_cmd[2]
                old_file_len = len(old_file_name) + 1
                new_file_len = len(new_file_name) + 1

                # Request: opcode old_file_len old_file_name new_file_len new_file_name
                # Create Request Msg
                req_str = opcode + f'{old_file_len:05b}' + old_file_name + f'{new_file_len:08b}' + new_file_name
                req = req_str.encode()
                
                # Request: opcode file_len file_name file_size
                s.send(req)

                # Receive Response from Server
                # 1024 Represents Buffer Size in Bytes
                data = s.recv(1024)
                res = data.decode()

                # Get Status Code
                res_code = res[0:3]

                if DEBUG_MODE:
                    print("Response:", res)
                    print()

                res_status = "was successfully" if res_code == "000" else "failed to be"
                print(f"{old_file_name} {res_status} changed to {new_file_name}!\n")

            # Send Help Request to Get List of Commands from Server 
            elif cmd == "help":
                opcode = "011"

                # Request: opcode unused (1 Byte)
                req_str = opcode + "00000"
                req = req_str.encode()
                s.send(req)

                if DEBUG_MODE:
                    print("Request:", req_str)

                # Receive Response from Server
                # 1024 Represents Buffer Size in Bytes
                data = s.recv(1024)
                res = data.decode()

                # Get Status Code
                res_code = res[0:3]
                msg_len = res[3:8]

                if DEBUG_MODE:
                    print("Response:", res)
                    print()

                msg_data = res[8:]
                print(msg_data)
                print()
            # Break Connection with Server and Exit
            elif cmd == "bye":
                # Close Socket and Break
                s.close()
                print("Client Socket Closed!\n")
                break
            else:
                write_err_msg("Invalid Command.")
                print("Suggestion: Enter help command to view list of commands\n")

    except KeyboardInterrupt:
        # Close Socket on Keyboard Interrupt
        print("\nClosing Socket on Keyboard Interrupt!")
    
    except Exception as e:
        # Catch Other Exceptions
        print("Error: ", e)

# Script Starting Point
if __name__ == '__main__':
    main()
