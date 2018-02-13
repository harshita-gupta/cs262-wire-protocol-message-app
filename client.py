# Import socket module
import config
import socket

current_user = None

# Create a socket object
s = socket.socket()

# connect to the server on local computer
s.connect((raw_input("IP:"), config.port))

# receive data from the server
print s.recv(1024)
# close the connection
s.close()
