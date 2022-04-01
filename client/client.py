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

# Print Debug Response
def debug_res(res):
    if DEBUG_MODE:
        print("Response:", res)

# Format Decimal to Binary String
def format_bin(val, bits):
    return f'{val:0{bits}b}'

# Calculate and Format File Name Length to 5 or 8 Bits
def get_filename_len(file_name, num_bits=5):
    fl = len(file_name)
    fl_bstr = format_bin(fl, num_bits)

    # Determine If File Name Exceeds Number Bits Used to Represent File in Request
    has_overflow = fl >  2**(num_bits) - 1
    if has_overflow:
        write_err_msg(f"File Size Exceeds Max Value from {num_bits} Bits Allocated!")

    return fl_bstr, has_overflow

# Calculate and Format File Size to 32 Bits
def get_file_size(file_name):
    fs = getsize(file_name)
    fs_bstr = format_bin(fs, 32)

    # Determine If File Size Exceeds Number Bits Used to Represent File in Request
    has_overflow = fs > 2**32 - 1
    if has_overflow:
        write_err_msg(f"File Size Exceeds Max Value from 32 Bits Allocated!")

    return fs_bstr, has_overflow

# Get Response Code from Response in Binary
def get_rescode(res):
    return res[0:3]

# Get Length from Response in Binary
def get_res_len(res):
    return res[3:8]

# Generate 1 Byte Long Request with Opcode and Unused Bits
def gen_byte_req(opcode):
    # Request: opcode unused
    req = opcode + "00000"
    return req.encode()

# Print Server Response to Client from Command/Request
def print_server_res(res_code, file_name, action_type, optional_fname=""):
    # Determine Response - Success or Failed
    if res_code == "000":
        res_status = "was successfully" 
    else:
        res_status = "failed to be"

        if res_code == "010":
            err_type = "File Not Found."
        elif res_code == "101":
            err_type = "Unsuccessful Change."
        else:
            err_type = "Unknown Request."
        write_err_msg(err_type)
    
    print(f"{file_name} {res_status} {action_type} {optional_fname}!\n")

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
                # 0b000 Represents Put
                opcode = "000"

                # Check if File Name is Specified
                if len(parsed_cmd) < 2:
                    write_err_msg("No File Name Provided!")
                    print("usage: put fileName\n")
                    continue

                # File Name Specifies Name of Transferred File
                file_name = parsed_cmd[1]

                # Check if File Exists
                if not exists(file_name):
                    write_err_msg("No File with Provided Name on Client!\n")
                    continue
                
                # File Name Length (FL) Specifies Length of File Name (5 bits)
                # Get and Check if File Name Length Overflows/Exceeds Max Value Given 5 Bits Allocated
                fl_bits, has_overflow = get_filename_len(file_name)
                if has_overflow:
                    continue

                # File Size (FS) Specifies Size of Transferred File
                # Get and Check if File Size Overflows/Exceeds Max Value Given 5 Bits Allocated
                fs_bits, has_overflow = get_file_size(file_name)
                if has_overflow:
                    continue

                # Create Request Msg
                req_str = opcode + fl_bits + file_name + fs_bits
                req = req_str.encode()
                
                # Request: opcode file_len file_name file_size
                s.send(req)
                debug_req(req_str)

                # File Data Specifies Data in File Sent as Chunks of Data
                # Send file_data by reading and segmenting file line by line
                with open(file_name, "rb") as file:
                    lines = file.readlines()
                    for line in lines:
                        s.send(line)

                # Receive Response from Server
                # 1024 Represents Buffer Size in Bytes
                data = s.recv(1024)
                res = data.decode()
                debug_res(res)

                # Get Status Code
                res_code = get_rescode(res)

                # Print Server Response - Success or Failed
                print_server_res(res_code, file_name, "uploaded")
            # Send Get Request to Transfer File from Server to Client
            elif cmd == "get":
                # 0b001 Represents Get
                opcode =  "001"

                # Check if File Name is Specified
                if len(parsed_cmd) < 2:
                    write_err_msg("No File Name Provided!")
                    print("usage: get fileName\n")
                    continue

                file_name = parsed_cmd[1]

                # Check if File Name Length Exceeds Max Value Given 5 Bits Allocated
                fl_bits, has_overflow = get_filename_len(file_name)
                if has_overflow:
                    continue

                # Request: opcode file_len file_name
                req_str = opcode + fl_bits + file_name
                req = req_str.encode()
                
                # Request: opcode file_len file_name file_size
                s.send(req)
                debug_req(req_str)

                # Receive Response from Server
                # 1024 Represents Buffer Size in Bytes
                res = s.recv(1024)
                debug_res(res)

                # Get Status Code
                res_code = get_rescode(res)
                file_name_len = int(res[3:8], 2)# NOTE:

                if res_code == b"001":
                    fn_end_ind = file_name_len + 8# NOTE:
                    fs_end_ind = fn_end_ind + 32# NOTE:
                    file_name = res[8:fn_end_ind].decode()# NOTE:
                    file_size = int(res[fn_end_ind:fs_end_ind], 2)# NOTE:

                    # Get File Data
                    file_data = res[fs_end_ind:]# NOTE:

                    # Calculate Amount of File Missing
                    # Loop Until All File Data is Received
                    while file_size - len(file_data) > 0:
                        # Wait for Data and Update Amount of File Missing
                        data = s.recv(1024)
                        if not data:
                            break

                        # Add Segmented File Data Until Whole File Received
                        file_data = file_data + data
    
                    # Write file_data to Specified File
                    with open(file_name, "wb") as file:
                        file.write(file_data)
                
                # Print Server Response - Success or Failed
                print_server_res(res_code.decode(), file_name, "downloaded") # NOTE: Change res to binary for all of them

            # Send Change Request to Rename File on Server
            elif cmd == "change":
                # 0b010 Represents Change Command
                opcode = "010"

                # Check if File Name is Specified
                if len(parsed_cmd) < 3:
                    write_err_msg("New or Old File Name Not Provided!")
                    print("usage: change oldFileName newFileName\n")
                    continue

                # Old File Name Specifies Name of File to Change
                # New File Name Specifies New Name of File
                old_file_name = parsed_cmd[1]
                new_file_name = parsed_cmd[2]

                # Old File Name Length (OFL) Specifies Length of Old File Name (5 bits)
                old_fl_bits, has_overflow = get_filename_len(old_file_name)
                if has_overflow:
                    continue

                # New File Name Length (NFL) Specifies Length of New File Name (1 Byte)
                new_fl_bits, has_overflow = get_filename_len(new_file_name, 8)
                if has_overflow:
                    continue

                # Request: opcode old_file_len old_file_name new_file_len new_file_name
                req_str = opcode + old_fl_bits + old_file_name + new_fl_bits + new_file_name
                req = req_str.encode()
                s.send(req)
                debug_req(req_str)

                # Receive Response from Server
                # 1024 Represents Buffer Size in Bytes
                data = s.recv(1024)
                res = data.decode()
                debug_res(res)

                # Get Status Code
                res_code = get_rescode(res)

                # Print Server Response - Success or Failed
                print_server_res(res_code, old_file_name, "changed", new_file_name)
            # Send Help Request to Get List of Commands from Server 
            elif cmd == "help":
                # 0b011 Represent Help Command
                req = gen_byte_req("011")

                # Request: opcode unused (1 Byte)
                s.send(req)
                debug_req(req_str)

                # Receive Response from Server
                # 1024 Represents Buffer Size in Bytes
                data = s.recv(1024)
                res = data.decode()
                debug_res(res)

                # Get Status Code
                res_code = get_rescode(res)
                msg_len = res[3:8] # NOTE:

                # Print Response
                msg_data = res[8:] # NOTE:
                print(msg_data + "\n")
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
        write_err_msg(e)

# Script Starting Point
if __name__ == '__main__':
    main()
