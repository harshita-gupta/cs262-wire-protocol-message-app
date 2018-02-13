# Import socket module
import config
import socket

current_user = None

if __name__ == '__main__':
        
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # mySocket.connect ( ( '', int(myPort)) )
        s.connect(('', 8080))
    except:
        print "ERROR: could not connect to " + myHost + ":" + myPort
        sys.exit()

    while True:
        netBuffer = getInput()
        #menu selection and function priming
        processInput(netBuffer)
        getResponse()

    mySocket.close()

# connect to the server on local computer
s.connect((raw_input("IP:"), config.port))

# receive data from the server
print s.recv(1024)
# close the connection
s.close()
