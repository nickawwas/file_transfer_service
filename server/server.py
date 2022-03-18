# Nicholas Kawwas (40124338)
# COEN 366 Section WJ-X
# Purpose: Simulate FTP Service (Serverside Code)
# Statement: Nicholas Kawwas is the Sole Author

from os.path import exists, getsize
from os import rename
from socket import socket, AF_INET6, SOCK_STREAM 

# Main Function Called in Script
def main():
    # TODO: Specify Server Port in Command Line Argument for Server
    # Set Hostname and Port Variables
    HOSTNAME, PORT = "127.0.0.1", 65432

    # Initialize Socket using AF_INET6 and SOCK_STREAM to Specify IPv6 and TCP Respectively 
    s = socket(AF_INET6, SOCK_STREAM)

    try:
        # Bind Hostname and Port Number to Socket as 127.0.0.1:65432
        s.bind((HOSTNAME, PORT))

        # Open TCP Socket, Listening for Connections on 127.0.0.1:65432
        s.listen()
        print("Listening for FTP Client Connection ...\n")

        # Accept Client Connection
        conn, addr = s.accept()
        print("Client Connection Accepted!\n")

        # with connection as c: 
        while True:
            # Receive HTTP Get Request from Client Connection/Browser
            data = conn.recv(1024)

            # Close Old Connnection and Allow New Connection with Another Client
            if not data:
                conn.close()
                print("Client Connection Closed!")

                conn, addr = s.accept()
                print("New Client Connection Accepted!")
                continue
            
            # Opcode Represented by First 3 Bits
            req = data.decode()
            opcode = req[0:3]

            # Respond to Put Request with Transfer File from Client to Server
            if opcode == "000":
                # Get File Length (FL) from Bits 3:8 in Binary (Convert to Decimal)
                file_name_len = int(req[3:8], 2)

                # File Name End Index: File Name Length Plus First Byte
                # File Size End Index: Four Bytes Reserved for File Size Plus File Name End Index
                fn_end_ind = file_name_len + 7
                fs_end_ind = fn_end_ind + 32
                
                # Get File Name from Bits 8:FL + 8
                file_name = req[8:fn_end_ind]
                file_size = int(req[fn_end_ind:fs_end_ind], 2)

                # Attempt to Access File Data from Received Msg
                file_data = req[fs_end_ind:]

                # Calculate Amount of File Missing
                # Loop Until All File Data is Received
                missing_file_size = file_size - len(file_data)
                while missing_file_size > 0:
                    # Wait for Data and Update Amount of File Missing
                    data = conn.recv(1024)

                    if not data:
                        break

                    file_data = file_data + data.decode()
                    missing_file_size = file_size - len(file_data)

                # Write to File
                with open(file_name, "w") as file:
                    file.write(file_data)
                
                # Generate Response (1 Byte)
                # Response Code (0b000) Specifies Correct Put and Change Requests
                res_code = "000"
                res_str = "000" + "00000"
                res = res_str.encode()

                # Response: res_code unused
                conn.send(res)
            # Respond to Get Request with Transfer File from Server to Client
            elif opcode == "001":
                # Get File Length (FL) from Bits 3:8 in Binary (Convert to Decimal)
                file_name_len = req[3:8]

                # File Name End Index: File Name Length Plus First Byte
                # File Size End Index: Four Bytes Reserved for File Size Plus File Name End Index
                fn_end_ind = int(file_name_len, 2) + 7
                
                # Get File Name from Bits 8:FL + 8
                file_name = req[8:fn_end_ind]

                # Check if File Exists
                if not exists(file_name):
                    # Response Code (0b010) Specifies File Not Found Error 
                    res_code  = "010"
                    res_str = res_code + "00000"
                    res = res_str.encode()
                    conn.send(res)
                    continue

                file_size = getsize(file_name)

                # Response: opcode file_len file_name file_size
                # Response Code (0b001) Specifies Correct Get Request
                res_code = "001"
                res_str = res_code + file_name_len + file_name + f'{file_size:032b}'
                res = res_str.encode()
                conn.send(res)

                # Response File: file_data
                with open(file_name, "r") as file:
                    lines = file.readlines()
                    for line in lines:
                        file_data = line.encode()
                        conn.send(file_data)
                
            # Respond to Change Request with Rename File on Server
            elif opcode == "010":
                # Get Old File Name using Old File Length from Request 
                old_file_len = req[3:8] 

                ofn_end_ind = int(old_file_len, 2) + 7              
                old_file_name = req[8:ofn_end_ind]

                # Error Validation: File with Old Name Doesn't Exist
                if not exists(old_file_name):
                    # Response Code (0b010) Specifies File Not Found Error 
                    res_code  = "010"
                    res_str = res_code + "00000"
                    res = res_str.encode()
                    conn.send(res)
                    continue

                # Get New File Name using New File Length from Request 
                nfl_end_ind = ofn_end_ind + 8         
                new_file_len = req[ofn_end_ind:nfl_end_ind] 

                nfn_end_ind = ofn_end_ind + int(new_file_len, 2) + 8            
                new_file_name = req[nfl_end_ind:nfn_end_ind]
                
                # Error Validation: File with New Name Already Exists
                # TODO: Or Old/New File Name is server.py 
                if exists(new_file_name) :
                    # Response Code (0b101 ) Specifies Unsuccessful Change
                    res_code  = "101"
                    res_str = res_code + "00000"
                    res = res_str.encode()
                    conn.send(res)
                    continue

                # Rename File
                rename(old_file_name, new_file_name)

                # Response Code (0b000) Specifies Correct Change Request
                res_code = "000"
                res_str = res_code + "00000"
                res = res_str.encode()

                # Request: opcode unused
                conn.send(res)
            # Respond to Help Request with Get List of Commands from Server 
            elif opcode == "011":
                # Response Code (0b110) Specifies Help Response
                res_code =  "110"
                
                help_data="Cmds: get put change help bye"
                help_data_len = len(help_data) + 1

                # Request: opcode help_data_len help_data
                res_str = res_code +  f'{help_data_len:05b}' + help_data
                res = res_str.encode()
                conn.send(res)
            # Respond to Unknown Request
            else:
                # Response Code (0b011) Specifies Unknown Request
                res_code = "011"
                res_str = res_code + "00000"
                res = res_str.encode()
                # Generate Response: res_code unused
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
