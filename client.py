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
           '\x71': delete_success,
           '\x72': delete_failure,
           '\x31': send_message_success,
           '\x32': send_message_failure, 
           '\x51': list_success
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
    (1) Create account
    (2) Log in
    (3) Delete an account
    (4) List all accounts 
    '''
    while True:
        startupInput = raw_input('>> ')
        if int(startupInput) > 0 and int(startupInput) < 5:            
            break

    return startupInput


def prompt_for_session_input():
    print '''
YOU ARE LOGGED IN! - type the number of a function:
    (3) Delete your account 
    (4) List all accounts
    (5) Send a message
    (6) Log out 
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
    # wait for server responses...
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
            break

        return success, info


def require_log_in():
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



if __name__ == '__main__':

    logging.basicConfig(
        format=logging_fmt,
        filename="clientLog.log")


    # SET UP SOCKET
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(('127.0.0.1', config.port))
    except:
        print "ERROR: could not connect to port: " + config.port
        sys.exit()

    # UPON LAUNCHING THE PROGRAM, USER MUST LOG IN OR
    # CREATE AN ACCOUNT
    current_user = None
    current_user = require_log_in()

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
                                retbuf)
                if values[1] != current_user:
                    clientSend.deliver_request_failure(
                        sock,
                        "Message intended for %s. %s is currently logged in" %
                        values[1], current_user)
                else:
                    print "Message from %s: %s" % values[0], values[3]
                    clientSend.deliver_request_success(conn, current_user)

            # User entered a message.
            # We stay within this block until the message is processed
            # by the server and we receive a success or failure message from
            # the server.
            # Therefore, no chat messages will deliver until the entire
            # transaction between the client and server for a given operation
            # is complete.
            else:
                while True:
                    sessionInput = getSessionInput()
                    processInput(sessionInput)
                    getResponse()
                    if int(sessionInput) == 5 or int(sessionInput) == 6:
                        current_user = None 
                        current_user = require_log_in()

    # mySocket.close()
