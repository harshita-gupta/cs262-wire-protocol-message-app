# Import socket module
import sys
import config
import socket
import clientSend
from clientReceive import *

current_user = None

version = '\x01'

# opcode associations; note that these opcodes will be returned by the server
opcodes = {'\x11': create_success,
           '\x12': create_failure,
           '\x61': logout_success,
           # '\x22': general_failure,
           # '\x31': deposit_success,
           # '\x32': general_failure,
           # '\x41': withdraw_success,
           # '\x42': general_failure,
           # '\x51': balance_success,
           # '\x52': general_failure,
           # '\x61': end_session_success,
           # '\x62': unknown_opcode
           }


def getStartupInput():
    print '''
WELCOME - type the number of a function:
    (1) Create Account
    (2) Log In
    '''
    while True:
        startupInput = raw_input('>> ')
        if int(startupInput) == 1 or int(startupInput) == 2:
            break

    return startupInput


def getSessionInput():
    print '''
YOU ARE LOGGED IN! - type the number of a function:
    (3) Send a message
    (4) List all accounts
    (5) Log out
    (6) Delete your account
    '''
    while True:
        sessionInput = raw_input('>> ')
        if int(sessionInput) > 2 and int(sessionInput) < 7:
            break

    return sessionInput


def processInput(requestNumber):
    # create
    if requestNumber == str(1):
        clientSend.create_request(sock)

    # login
    elif requestNumber == str(2):
        clientSend.login_request(sock)

    # logout
    elif requestNumber == str(5):
        clientSend.logout_request(sock, current_user)

    return


def getResponse():
    # wait for server responses...
    while True:
        try:
            retBuffer = sock.recv(1024)
        except:
            # close the client if the connection is down
            print "ERROR: connection down"
            sys.exit()

        if len(retBuffer) != 0:
            header = unpack(config.pack_header_fmt, retBuffer[0:6])
            # only allow correct version numbers
            if header[0] == version:
                opcode = header[2]
                # send packet to correct handler
                try:
                    success, info = opcodes[opcode](sock, retBuffer)
                except KeyError:
                    break
                if success:
                    # return True and username
                    return True, info
                else:
                    return False, info
            else:
                return
        return


if __name__ == '__main__':

    # SET UP SOCKET
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(('127.0.0.1', config.port))
    except:
        print "ERROR: could not connect to port: " + config.port
        sys.exit()

    # PROCESS INPUT
    while True:

        while True:
            startupInput = getStartupInput()
            processInput(startupInput)
            success, username = getResponse()
            if success:
                current_user = username
                break

        while True:
            sessionInput = getSessionInput()
            processInput(sessionInput)
            getResponse()
            if int(sessionInput) == 5:
                current_user = None
                break

    # mySocket.close()
