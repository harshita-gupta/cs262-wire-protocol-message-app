# Import socket module
import sys
import config
import socket
import select
import clientSend
from clientReceive import *

global current_user

version = '\x01'

# opcode associations; note that these opcodes will be returned by the server
opcodes = {'\x11': create_success,
           '\x12': create_failure,
           '\x21': login_success,
           '\x22': login_failure,
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


def prompt_for_session_input():
    print '''
YOU ARE LOGGED IN! - type the number of a function:
    (3) Send a message
    (4) List all accounts
    (5) Log out
    (6) Delete your account
    '''
    sys.stdout.flush()


def getSessionInput():
    prompt_for_session_input()
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

        if not retBuffer:
            print "ERROR: connection down"
            sys.exit()

        header = unpack(config.pack_header_fmt, retBuffer[0:6])

        # only allow correct version numbers
        if header[0] != version:
            return False

        # send packet to correct handler based on opcode
        opcode = header[2]

        try:
            success, info = opcodes[opcode](sock, retBuffer)
        except KeyError:
            break

        return success, info


def require_log_in():
    while True:
        startupInput = getStartupInput()
        processInput(startupInput)
        success, username = getResponse()
        if success:
            return username
        else:
            print username


if __name__ == '__main__':

    # SET UP SOCKET
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(('127.0.0.1', config.port))
    except:
        print "ERROR: could not connect to port: " + config.port
        sys.exit()

    # UPON LAUNCHING THE PROGRAM, USER MUST LOG IN OR
    # CREATE AN ACCOUNT
    current_user = require_log_in()

    prompt_for_session_input()

    # PROCESS INPUT
    while True:
        socket_list = [sys.stdin, sock]

        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(
            socket_list, [], [])

        for s in read_sockets:
            # incoming message from remote server
            if s == sock:
                # deal w that shit
                data = sock.getResponse()

            # user entered a message
            else:
                while True:
                    sessionInput = getSessionInput()
                    processInput(sessionInput)
                    getResponse()
                    if int(sessionInput) == 5:
                        current_user = require_log_in()

    # mySocket.close()
