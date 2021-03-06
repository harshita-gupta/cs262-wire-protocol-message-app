
'''
This is the main file for the client.
It sets up a connection with a server, prompts the user for input,
and processes these input.
Processed input and raw data from the server is used to determine
which functions in clientReceive and clientSend should be called.
The functions within clientReceive and clientSend handle specific
operations.
'''

import sys
import config
import socket
import select
import clientSend
import atexit
from clientReceive import *

global current_user

version = '\x01'

# opcode associations; note that these opcodes will be returned by the server
opcodes = {'\x11': create_success,
           '\x12': create_failure,
           '\x21': login_success,
           '\x22': login_failure,
           '\x61': logout_success,
           '\x71': delete_success,
           '\x72': delete_failure,
           '\x31': send_message_success,
           '\x32': send_message_failure,
           '\x51': list_success
           }


def getStartupInput():
    '''
    Prompts user for numerical input corresponding to a function.

    :return: Returns the string representation of the numerical input
    '''
    print '''
WELCOME - type the number of a function:
    (1) Create account
    (2) Log in
    (3) Delete an account
    (4) List accounts
    '''
    while True:
        startupInput = raw_input('>> ')
        # Input must be a digit between 0 and 5 exclusive
        if (startupInput.isdigit() and
                int(startupInput) > 0 and int(startupInput) < 5):
            break
    return startupInput


def prompt_for_session_input():
    '''
    Displays menu of functions to user
    '''
    print '''
YOU ARE LOGGED IN! - type the number of a function:
    (3) Delete your account
    (4) List accounts
    (5) Send a message
    (6) Log out
    '''
    sys.stdout.flush()


def getSessionInput():
    '''
    Prompts user for numerical input corresponding to a function.

    :return: Returns the string representation of the numerical input
    '''
    prompt_for_session_input()
    while True:
        sessionInput = raw_input('>> ')
        if (sessionInput.isdigit() and
                int(sessionInput) > 2 and int(sessionInput) < 7):
            break

    return sessionInput


def processInput(requestNumber):
    '''
    Processes user function request by relaying it to the corresponding
    function in clientSend.py

    :param requestNumber: Function number inputted by user
    '''
    # create
    if requestNumber == str(1):
        clientSend.create_request(sock)

    # login
    elif requestNumber == str(2):
        clientSend.login_request(sock)

    # delete
    elif requestNumber == str(3):
        clientSend.delete_request(sock, current_user)

    # list
    elif requestNumber == str(4):
        clientSend.list_request(sock)

    # message
    elif requestNumber == str(5):
        clientSend.send_message_request(sock, current_user)

    # logout
    elif requestNumber == str(6):
        clientSend.logout_request(sock, current_user)

    return


def get_server_message():
    '''
    Listens for and receives incoming messages from the server

    :return: header of server's message and entire message
    (including header)
    '''
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

    return header, retBuffer


def getResponse():
    '''
    Wait for server responses...
    '''
    while True:
        header, buf = get_server_message()

        # only allow correct version numbers
        if header[0] != version:
            return False

        # send packet to correct handler based on opcode
        opcode = header[2]
        try:
            success, info = opcodes[opcode](sock, buf)
        except KeyError:
            "got a keyerror"
            break

        return success, info


def require_log_in():
    '''
    Brings the user back to the WELCOME page. If the user is creating
    an account or logging in, it will return the username if getResponse()
    is successful in order to set the current_user variable. Otherwise,
    process input as usual.

    :return: Returns username if user is creating an account or logging in
    '''
    while True:
        startupInput = getStartupInput()

        # if creating account or logging in
        if int(startupInput) == 1 or int(startupInput) == 2:
            processInput(startupInput)
            success, username = getResponse()
            if success:
                return username
            else:
                print username
        else:
            processInput(startupInput)
            getResponse()


def logout_current_user(conn):
    global current_user
    clientSend.logout_request(conn, current_user)


if __name__ == '__main__':

    global current_user
    logging.basicConfig(
        format=logging_fmt,
        filename="clientLog.log")

    # SET UP SOCKET
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((raw_input("IP: "), config.port))
    except:
        print "ERROR: could not connect to host or port"
        sys.exit()

    # UPON LAUNCHING THE PROGRAM, USER MUST LOG IN OR
    # CREATE AN ACCOUNT
    current_user = None
    current_user = require_log_in()
    atexit.register(logout_current_user, sock)

    prompt_for_session_input()

    # PROCESS INPUT
    while True:
        socket_list = [sys.stdin, sock]

        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(
            socket_list, [], [])

        for s in read_sockets:

            # Incoming message from remote server
            if s == sock:
                header, retbuf = get_server_message()
                if header[2] != '\x80':
                    logging.info(("received server message with unexpected"
                                  "op code, ignoring."))
                    continue
                message_len = header[1] - (2 * username_length)
                values = unpack(config.request_body_fmt['\x80'] % message_len,
                                retbuf[6:6 + header[1]])
                if values[1] != current_user:
                    clientSend.deliver_request_failure(
                        sock,
                        "Message intended for %s. %s is currently logged in" %
                        (values[1], current_user))
                else:
                    print "Message from %s: %s" % (values[0], values[2])
                    clientSend.deliver_request_success(sock, current_user)

            # User entered a message.
            # We stay within this block until the message is processed
            # by the server and we receive a success or failure message from
            # the server.
            # Therefore, no chat messages will deliver until the entire
            # transaction between the client and server for a given operation
            # is complete.
            else:
                sessionInput = getSessionInput()
                processInput(sessionInput)
                getResponse()
                if int(sessionInput) == 3 or int(sessionInput) == 6:
                    current_user = None
                    current_user = require_log_in()
                prompt_for_session_input()

    # mySocket.close()
