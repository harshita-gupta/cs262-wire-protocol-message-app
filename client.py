# Import socket module
import sys
import config
import socket
import clientSend

current_user = None


def getStartupInput():
    print '''
WELCOME - type the number of a function:
    (1) Create Account
    (2) Log In
    '''
    startupInput = raw_input('>> ')
    return startupInput


def processInput(requestNumber):
    # create
    if requestNumber == str(1):
        clientSend.create_request(sock)

    # delete
    elif requestNumber == str(2):
        clientSend.login_request(sock)

    return


if __name__ == '__main__':

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(('127.0.0.1', config.port))
    except:
        print "ERROR: could not connect to port: " + config.port
        sys.exit()

    while True:
        startupInput = getStartupInput()
        processInput(startupInput)
        # getResponse()

    # mySocket.close()
