# Nicholas Kawwas (40124338)
# COEN 366 Section WJ-X
# Purpose: Simulate FTP Service (Serverside Code)
# Statement: Nicholas Kawwas is the Sole Author

from sys import argv
from os import rename
from os.path import exists, getsize
from socket import socket, AF_INET6, SOCK_STREAM 

# Specify IP Address and Port as First and Second Command Line Arguments
# Note - argv[1]: IP Address, argv[2]: Port
HOSTNAME = "127.0.0.1" if len(argv) < 2 else argv[1]
PORT = 65432 if len(argv) < 3 else int(argv[2])

# Specify Debug Mode as Third/Last Command Line Argument 
# Debug Mode: Off (0) - No Printing, On (1) - Printing Msgs Sent and Received
# Note - argv[3]: Debug Mode (Default 0)
DEBUG_MODE = 1 if len(argv) < 4 else int(argv[3])

# Print Debug Request
def debug_req(req):
    if DEBUG_MODE:
        print("Request:", req)

# Print Debug Response
def debug_res(res):
    if DEBUG_MODE:
        print("Response:", res)

# Accept Client Connection
# Returns Connection and Connection Number
def accept_conn(socket, connection_no):
    connection, _ = socket.accept()
    connection_no += 1
    print(f"Client Connection #{connection_no} Accepted!\n")
    return connection, connection_no

# Close Client Connection
def close_conn(connection, connection_no):
    connection.close()
    print(f"Client Connection #{connection_no} Closed!\n")

# Get Opcode from Request Bits 0:3 in Binary
def get_opcode_bits(req):
    return req[0:3]

# Get Filename Length (FL) from Req Bits 3:8 in Binary
def get_fl_bits(req):
    return req[3:8]

# Get File Name from Request
def get_file_name(req, fl):
    # Calculate End Index to Extract File Name
    # Convert Binary to Decimal Then Add Byte Offset
    # -> File Name Starts After First Byte
    fn_end_ind = int(fl, 2) + 8              
    file_name = req[8:fn_end_ind]
    return file_name, fn_end_ind

# Get File Size from Request
def get_fs_bits(req, fl):
    # Calculate End Index to Extract File Name
    # Convert Binary to Decimal Then Add Byte Offset
    # -> File Name Starts After First Byte
    fn_end_ind = int(fl, 2) + 8              
    file_name = req[8:fn_end_ind]
    return file_name, fn_end_ind


# TODO...
# Get File Data from Put Request
def get_file_data(conn, current_file_data, fs):
    # Attempt to Access File Data from Received Msg
    file_data = current_file_data

    # Calculate Amount of File Missing
    # Loop Until All File Data is Received
    missing_file_size = fs - len(file_data)
    while missing_file_size > 0:
        # Wait for Data and Update Amount of File Missing
        data = conn.recv(1024)

        if not data:
            break

        file_data = file_data + data.decode()
        missing_file_size = fs - len(file_data)
    
    return file_data

# Format Decimal to Binary String
def format_bin(num):
    return f'{num:05b}'

# Generate 1 Byte Long Response with Res Code and Unused Bits
def gen_byte_res(res_code):
    # Response: res_code unused
    res = res_code + "00000"
    return res.encode()

# Generate Help Response
def gen_help_res():
    # Response Code (0b110) Specifies Help Response
    res_code =  "110"
    
    help_data = "Cmds: get put change help bye"
    help_data_len = len(help_data)

    # Request: opcode help_data_len help_data
    res = res_code +  f'{help_data_len:05b}' + help_data
    return res.encode()

# Main Function
def main():
    # Initialize Socket using AF_INET6 and SOCK_STREAM to Specify IPv6 and TCP Respectively 
    s = socket(AF_INET6, SOCK_STREAM)

    try:
        # Bind Hostname and Port Number to Socket as 127.0.0.1:65432
        s.bind((HOSTNAME, PORT))

        # Open TCP Socket, Listening for Connections on 127.0.0.1:65432
        s.listen()
        print("Listening for FTP Client Connection ...\n")

        # Accept Initial Client Connection
        conn, conn_num = accept_conn(s, 0)

        while True:
            # Receive HTTP Get Request from Client Connection/Browser
            data = conn.recv(1024)

            # Close Old Connnection and Allow New Connection with Another Client
            if not data:
                close_conn(conn, conn_num)
                conn, conn_num = accept_conn(s, conn_num)
                continue
            
            # Decode Request and Extract Opcode Bits
            req = data #.decode()
            opcode = get_opcode_bits(req)
            print("Opcode", opcode)

            debug_req(req)

            # Respond to Put Request with Transfer File from Client to Server
            if opcode == b'000':
                fl_bits = get_fl_bits(req)
                file_name_len = int(fl_bits, 2)

                # File Name End Index: File Name Length Plus First Byte
                # File Size End Index: Four Bytes Reserved for File Size Plus File Name End Index
                fn_end_ind = file_name_len + 8
                fs_end_ind = fn_end_ind + 32

                
                # Get File Name from Bits 8:FL + 8
                file_name = req[8:fn_end_ind].decode()
                file_size = int(req[fn_end_ind:fs_end_ind], 2)

                print("File Name", file_name)
                print("File Size", file_size)

                #Attempt to Access File Data from Received Msg
                file_data = req[fs_end_ind:]

                # Calculate Amount of File Missing
                # Loop Until All File Data is Received
                missing_file_size = file_size - len(file_data)
                while missing_file_size > 0:
                    # Wait for Data and Update Amount of File Missing
                    data = conn.recv(1024)

                    if not data:
                        break

                    print(data)

                    file_data = file_data + data
                    missing_file_size = file_size - len(file_data)

                # Write to File
                with open(file_name, "wb") as file:
                    file.write(file_data)
                
                # Response Code (0b000) Specifies Correct Put and Change Requests
                res = gen_byte_res("000")
                conn.send(res)
            # Respond to Get Request with Transfer File from Server to Client
            elif opcode == b'001':
                # Get File Length (FL) from Bits 3:8 in Binary (Convert to Decimal)
                file_name_len = get_fl_bits(req)

                # File Name End Index: File Name Length Plus First Byte
                # File Size End Index: Four Bytes Reserved for File Size Plus File Name End Index
                fn_end_ind = int(file_name_len, 2) + 8
                
                # Get File Name from Bits 8:FL + 8
                file_name = req[8:fn_end_ind].decode()

                # Check if File Exists
                if not exists(file_name):
                    # Response Code (0b010) Specifies File Not Found Error 
                    res = gen_byte_res("010")
                    conn.send(res)
                    continue

                file_size = getsize(file_name)

                # Response: opcode file_len file_name file_size
                # Response Code (0b001) Specifies Correct Get Request
                res_code = "001"
                res_str = res_code + file_name_len.decode() + file_name + f'{file_size:032b}'
                res = res_str.encode()
                conn.send(res)

                # Response File: file_data
                with open(file_name, "rb") as file:
                    lines = file.readlines()
                    for line in lines:
                        conn.send(line)
                
            # Respond to Change Request with Rename File on Server
            elif opcode == b'010':
                # Get Old File Name using Old File Length from Request 
                old_file_len = get_fl_bits(req)

                ofn_end_ind = int(old_file_len, 2) + 8              
                old_file_name = req[8:ofn_end_ind]

                # Error Validation: File with Old Name Doesn't Exist
                if not exists(old_file_name):
                    # Response Code (0b010) Specifies File Not Found Error 
                    res = gen_byte_res("010")
                    conn.send(res)
                    continue

                # Get New File Name using New File Length from Request 
                nfl_end_ind = ofn_end_ind + 8         
                new_file_len = req[ofn_end_ind:nfl_end_ind] 

                nfn_end_ind = ofn_end_ind + int(new_file_len, 2) + 8            
                new_file_name = req[nfl_end_ind:nfn_end_ind]
                
                # Error Validation: File with New Name Already Exists
                # TODO: Or Old/New File Name is server.py 
                if exists(new_file_name) or old_file_name == "server.py":
                    # Response Code (0b101) Specifies Unsuccessful Change
                    res = gen_byte_res("101")
                    conn.send(res)
                    continue

                # Rename File
                rename(old_file_name, new_file_name)

                # Response Code (0b000) Specifies Correct Change Request
                res = gen_byte_res("000")
                conn.send(res)
            # Respond to Help Request with Get List of Commands from Server 
            elif opcode == b'011':
                res = gen_help_res()
                conn.send(res)
            # Respond to Unknown Request
            else:
                # Response Code (0b011) Specifies Unknown Request
                res = gen_byte_res("011")
                conn.send(res)

    except KeyboardInterrupt:
        # Close Socket on Keyboard Interrupt
        print("\nClosed Server Socket on Keyboard Interrupt!")
    
    except Exception as e:
        # Catch Other Exceptions
        print("\nError:", e)


# Script Starting Point
if __name__ == '__main__':
    main()
