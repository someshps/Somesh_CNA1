import socket #importing the socket module from python
import os


HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65430  # Port to listen on (non-privileged ports are > 1023)

def encrypt(text,s):
    result = ""

    if(s == "rev"):
        #This represents the 'Transpose' fucntionality of the crypt layer.
        #It reverses the contents in a word by word manner.
        result = text[::-1]
        return result
  
    # traverse text
    for i in range(len(text)):
        char = text[i]
  
        #uppercase characters
        if (char.isupper()):
            result += chr((ord(char) + s-65) % 26 + 65)

        if(char == "\n"):
            result += "\n"
        
        if(ord(char)>=32 and ord(char)<=47):
            result+=char
        if(ord(char)>=58 and ord(char)<=64):
            result+=char
        if(ord(char)>=91 and ord(char)<=96):
            result+=char
        if(ord(char)>=123 and ord(char)<=126):
            result+=char
  
        #lowercase characters
        else:
            result += chr((ord(char) + s - 97) % 26 + 97)
  
    return result


#We create a socket object using socket.socket()
#AF_INET is the Internet address family for IPv4
#socket.SOCK_STREAM specifies the TCP protocol
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    s.bind((HOST, PORT)) #used to associate the socket with a specific network interface and port number
    s.listen() #enables a server to accept connections.

    print("Hello, I am a server and I am waiting for a client to connect with me.")

    conn, addr = s.accept() #creating the client socket object conn
    # .accept() method blocks execution and waits for an incoming connection.
    # When a client connects, it returns a new socket object representing the connection
    # and a tuple holding the address of the client. The tuple will contain (host, port) for IPv4 connections

    # we have a new socket object from .accept(). 
    # it’s the socket that you’ll use to communicate with the client. 
    # It’s distinct from the listening socket that the server is using to accept new connections. 

    with conn: #with statement automatically closes the socket at the end of the block
        print("Client came and is now connected by ", {addr}) 
        # This prints the client’s IP address and TCP port number.
        while True:
            #We first recieve the command which was given from the client
            data = conn.recv(1024).decode()
            offset = "rev"
            #now decrypt the command recieved. The value of offset woudl be as follows
            # for Plain text => 0
            # for Caesar cipher => -2
            # for Transpose  => "rev" 
            data = encrypt(data, offset)

            #now you have the command in its original form which was given in client

            #for retrieving the path of the current working directory for the user
            if(data == "cwd"):
                dir = os.getcwd()
                data_encrypted = encrypt(dir, offset)
                conn.sendall(bytes(data_encrypted, 'utf-8'))

            #List the files/folders present in the current working directory
            elif(data == "ls"):
                elem = os.listdir()
                # print("this is what listdir returns: ", elem)
                string1 = str(elem)
                data_encrypted = encrypt(string1, offset)
                # print(data_encrypted)
                conn.sendall(bytes(data_encrypted, 'utf-8'))

            #Change the directory to directory specified by the client
            elif(data[:2]=="cd"):
                directory = data[3:]
                os.chdir(directory)
                string1 = "Directory successfully changed. Status: OK"
                data_encrypted = encrypt(string1, offset)
                conn.sendall(bytes(data_encrypted, 'utf-8'))
                # print("Directory successfully changed. Status: OK", os.getcwd())

            #Download the specified file by the user on server to client
            elif(data[:3]=="dwd"):
                filename = data[4:]
                file=open(filename, "r")
                data = file.read()
                # print(data)
                # print("I am encrypting the data")
                data_encrypted = encrypt(data, "rev")
                # print(data_encrypted)
                conn.sendall(bytes(data_encrypted, 'utf-8'))
                file.close()

            #Upload the specified file on client to the remote server in CWD
            elif(data[:3]=="upd"):
                file_data = conn.recv(1024).decode()
                if not file_data:
                    print("No data recieved. Status: NOK")
                    break
                filename = data[4:]
                # print("the name of the file recieved by the server is: ", filename)
                file = open(filename, 'w')
                data_decrypted = encrypt(file_data, -2)
                file.write(data_decrypted)
                file.close()
                print("File successfuly uploaded. Status: OK")

            elif(data == "stop"): #If you want to stop the service
                print("Program successfuly stopped")
                break

            else: #if any other unknown command is inputted
                print("Not a valid command")