# Nicholas Kawwas (40124338)
# COEN 366 Section WJ-X
# Purpose: Simulate FTP Service (Serverside Code)
# Statement: Nicholas Kawwas is the Sole Author

from os import rename
from sys import stdout, argv
from os.path import exists, getsize
from socket import socket, AF_INET6, SOCK_STREAM 

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
    file_name = req[8:fn_end_ind].decode()
    return file_name, fn_end_ind

# Get File Size from Request
def get_file_size(req, fn_end_ind):
    # Calculate End Index to Extract File Name
    # Convert Binary to Decimal Then Add Byte Offset
    # -> File Name Starts After End of File Name
    fs_end_ind = fn_end_ind + 32             
    file_size = int(req[fn_end_ind:fs_end_ind], 2)
    return file_size, fs_end_ind

# Get New File Name from Change Request
def get_new_file_name(req, ofn_end_ind):
    # Calculate End Index to Extract New File Name
    # Convert Binary to Decimal Then Add Byte Offset
    # -> File Name Starts After End of Old File Name
    nfl_start_ind = ofn_end_ind + 8
    new_file_len = int(req[ofn_end_ind:nfl_start_ind], 2)

    nfn_end_ind = nfl_start_ind + new_file_len    
    new_file_name = req[nfl_start_ind:nfn_end_ind].decode()
    return new_file_name

# Validation - Check if File Name Matches with Critical Files
def is_critical_file(new_name, old_name):
    return "server.py" in [new_name, old_name]

# Format Decimal to Binary String
def format_bin(val, bits):
    return f'{val:0{bits}b}'

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

# Send Response and Print Debug Msg
def send_res(conn, res):
    conn.send(res)
    debug_res(res)

# TODO: Fix Read and Write Binary
# Get Missing File Data to Receive Whole File
def get_missing_file_data(conn, file_size, file_data):
    # Calculate Amount of File Missing
    missing_file_size = file_size - len(file_data)

    # Loop until Whole File Received (Missing = 0)
    while missing_file_size > 0:
        # Wait for Data and Update Amount of File Missing
        data = conn.recv(1024)
        if not data:
            break

        # Add Incoming Data to File
        file_data += data

        # Reevalute Amount of Data Missing
        missing_file_size = file_size - len(file_data)

    return file_data

# Read Binary from File, Send Line By Line
def read_bin_send(conn, file_name):
    with open(file_name, "rb") as file:
        lines = file.readlines()
        for line in lines:
            send_res(conn, line)

# Write Binary to File, Received Line By Line
def write_bin_receive(conn, file_name, file_data):
    with open(file_name, "wb") as file:
            file.write(file_data)

# Main Function
def main():
    # Initialize Socket using AF_INET6 and SOCK_STREAM to Specify IPv6 and TCP Respectively 
    s = socket(AF_INET6, SOCK_STREAM)

    try:
        # Bind Hostname and Port Number to Socket as 127.0.0.1:65432
        s.bind((HOSTNAME, PORT))
        print("Server Running on Specified Hostname and Port Number! \n")

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
            
            # Extract Opcode Bits
            opcode = get_opcode_bits(data)

            debug_req(data)

            # Respond to Put Request with Transfer File from Client to Server
            if opcode == b'000':
                fl_bits = get_fl_bits(data)

                # Get File Name from Bits 8:FL + 8
                # File Name End Index: File Name Length Plus First Byte
                file_name, fn_end_ind = get_file_name(data, fl_bits)
                
                # Get File Size from Bits FL + 8: FL + 8 + 32
                # File Size End Index: Four Bytes Reserved for File Size Plus File Name End Index
                file_size, fs_end_ind = get_file_size(data, fn_end_ind)

                #Attempt to Access File Data from Received Msg
                file_data = data[fs_end_ind:]

                # Calculate Amount of File Missing
                missing_file_size = file_size - len(file_data)

                # Loop Until All File Data is Received
                while missing_file_size > 0:
                    # Wait for Data and Update Amount of File Missing
                    data = conn.recv(1024)
                    if not data:
                        break
                    
                    # Add Incoming Data to File, Line by Line
                    file_data = file_data + data
                    missing_file_size = file_size - len(file_data)

                # Write to File in Binary to Avoid Encoding Issues (Especially for PDF and PNG)
                with open(file_name, "wb") as file:
                    file.write(file_data)
                
                # Response Code (0b000) Specifies Correct Put and Change Requests
                res = gen_byte_res("000")
                send_res(conn, res)
            # Respond to Get Request with Transfer File from Server to Client
            elif opcode == b'001':
                # Get File Length (FL) from Bits 3:8 in Binary (Convert to Decimal)
                fl_bits = get_fl_bits(data)

                # Get File Name from Bits 8:FL + 8
                # File Name End Index: File Name Length Plus First Byte
                file_name, fn_end_ind = get_file_name(data, fl_bits)
    
                # Check if File Exists
                if not exists(file_name):
                    # Response Code (0b010) Specifies File Not Found Error 
                    res = gen_byte_res("010")
                    send_res(conn, res)
                    continue

                file_size = getsize(file_name)

                # Response: opcode file_len file_name file_size
                # Response Code (0b001) Specifies Correct Get Request
                res_code = "001"
                res_str = res_code + fl_bits.decode() + file_name + format_bin(file_size, 32)
                res = res_str.encode()
                send_res(conn, res)

                # Response File: file_data
                with open(file_name, "rb") as file:
                    lines = file.readlines()
                    for line in lines:
                        conn.send(line)
                
            # Respond to Change Request with Rename File on Server
            elif opcode == b'010':
                # Get Old File Name using Old File Length from Request 
                old_fl_bits = get_fl_bits(data)

                # Get File Name from Bits 8:FL + 8
                # File Name End Index: File Name Length Plus First Byte
                old_file_name, ofn_end_ind = get_file_name(data, old_fl_bits)

                # Error Validation: File with Old Name Doesn't Exist
                if not exists(old_file_name):
                    # Response Code (0b010) Specifies File Not Found Error 
                    res = gen_byte_res("010")
                    send_res(conn, res)
                    continue

                # Get New File Name using New File Length from Request
                new_file_name = get_new_file_name(data, ofn_end_ind)
                
                # Error Validation: File with New Name Already Exists
                # Or New/Old File Name Represent a Critical File (Avoid Overwritting)
                if exists(new_file_name) or is_critical_file(new_file_name, old_file_name):
                    # Response Code (0b101) Specifies Unsuccessful Change
                    res = gen_byte_res("101")
                    send_res(conn, res)
                    continue

                # Rename File
                rename(old_file_name, new_file_name)

                # Response Code (0b000) Specifies Correct Change Request
                res = gen_byte_res("000")
                send_res(conn, res)
            # Respond to Help Request with Get List of Commands from Server 
            elif opcode == b'011':
                res = gen_help_res()
                send_res(conn, res)
            # Respond to Unknown Request
            else:
                # Response Code (0b011) Specifies Unknown Request
                res = gen_byte_res("011")
                send_res(conn, res)

    except KeyboardInterrupt:
        # Close Socket on Keyboard Interrupt
        print("\nClosed Server Socket on Keyboard Interrupt!")
    
    except Exception as e:
        # Catch Other Exceptions
        write_err_msg(e)


# Script Starting Point
if __name__ == '__main__':
    main()
