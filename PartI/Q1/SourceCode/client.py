import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65430  # The port used by the server

def encrypt(text,s):
    result = ""

    if(s == "rev"): 
    	#This represents the 'Transpose' fucntionality of the crypt layer.
    	#It reverses the contents in a word by word manner.
        result = text[::-1]
        return result
  
    for i in range(len(text)):
        char = text[i]
  
        #uppercase characters
        if (char.isupper()):
            result += chr((ord(char) + s-65) % 26 + 65)

        #newline command
        if(char == "\n"):
            result += "\n"

        #special characters
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

    s.connect((HOST, PORT)) #connect to the host and port specified above

    while True:
        command = input() #take input the command you want to execute
        offset = "rev" #this is value of offset to be provided to make use of the 
        #services of the crypt layer. How to use this is defined below.
        # for Plain text => 0
        # for Caesar cipher => 2
        # for Transpose  => "rev" 
        # print(offset)
        command = encrypt(command, offset) #we encrypt the command before sending it to the server
        #using .sendall() we send all the data in binary form as packets 
        s.sendall(bytes(command, 'utf-8'))
        #for checking which command we have run, we need to decrypt the data back
        command = encrypt(command, offset)

        #for retrieving the path of the current working directory for the user
        if(command == "cwd"):
            data = s.recv(1024).decode() #data recieved is in encrypted form
            data_decrypted = encrypt(data, offset) #decrypt the data
            print(data_decrypted)

        #List the files/folders present in the current working directory
        elif(command == "ls"):
            data = s.recv(1024).decode() #data recieved is in encrypted form
            data_decrypted = encrypt(data, offset) #decrypt the data
            print(data_decrypted)

        #Change the directory to directory specified by the client
        elif(command[:2] == "cd"):
        	data = s.recv(1024).decode() #recieve the succesful directory change message
        	if not data:
        		print("Directory not changed. Status: NOK")
        		break
        	data_decrypted = encrypt(data, offset) #decrypt the recieved message
        	print("Directory successfuly changed. Status: OK")

        #Download the specified file by the user on server to client
        elif(command[:3] == "dwd"):
            data = s.recv(1024).decode() #reciving the data
            if not data:
                print("No data recieved. Status: NOK")
                break
            filename = command[4:] #specified filename
            file = open(filename, 'w') #open the file in 'write' mode so than we can write in it
            data_decrypted = encrypt(data, offset) #decrypt the recieved data
            file.write(data_decrypted) #write the decrypted data to the file open in 'w' mode
            file.close() #close the file to avoid unnecessary errors in the future
            print("File successfuly downloaded. Status: OK") 

        #Upload the specified file on client to the remote server in CWD    
        elif(command[:3] == "upd"):
            filename = command[4:]
            # print(filename)
            file = open(filename, "r")
            data1 = file.read() #read the data from file
            # print(data1)
            # print("I am encrypting the data")
            data_encrypted = encrypt(data1, offset) #encrypt the data
            # print(data_encrypted)
            s.sendall(bytes(data_encrypted, 'utf-8')) #send the encrypted data
            print("Go to server's terminal window")
            file.close()  

        elif(command == "stop"): #If you want to stop the service
        	print("Program successfuly stopped")
        	break

        else: #if any other unknown command is inputted
        	print("Not a valid command")