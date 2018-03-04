import config
from config import send_message
from struct import pack

################################################
# ClIENT SEND OPERATIONS ########################
################################################

'''
This file contains the implementations for all requests the client
sends to the server.
'''

# create new account
def create_request(conn):
    '''
    Prompts user to input an original username. Repeats prompt if username
    does not follow the specs of being alphanumeric and exactly 5 characters
    long. Packs and send the message to the server.

    :param conn: connection to the server
    '''
    print "\nCREATING AN ACCOUNT \n"
    print "enter a an alphanumeric username five characters long:"
    while True:
        userInput = raw_input('>> ')
        if(userInput.isalnum() and len(userInput) == 5):
            username = userInput
            break
        print "We only support usernames that are alphanumeric and exactly 5 characters long. \nPlease try again."

    send_message('\x01' + pack('!I', 5) + '\x10' +
                 pack(config.request_body_fmt['\x10'], username), conn)


# log in to an existing account
def login_request(conn):
    '''
    Prompts user to input an existing username. Repeats prompt if username
    does not follow the specs of being alphanumeric and exactly 5 characters
    long. Packs and send the message to the server.

    :param conn: connection to the server
    '''
    print "\nLOGGING IN \n"
    print "Enter your username"
    while True:
        userInput = raw_input('>> ')
        if(userInput.isalnum() and len(userInput) == 5):
            username = userInput
            break
        print "We only support usernames that are alphanumeric and exactly 5 characters long. \nPlease try again."

    send_message('\x01' + pack('!I', 5) + '\x20' +
                 pack(config.request_body_fmt['\x20'], username), conn)


# log out
def logout_request(conn, username):
    '''
    Sends logout request to the server containing the username to be
    removed from the active_clients list

    :param conn: connection to server
    :param username: current_user variable to be removed from active_clients
    list
    '''
    print "\nLOGGING OUT \n"
    send_message('\x01' + pack('!I', 5) + '\x60' +
                 pack(config.request_body_fmt['\x60'], username), conn)


# delete
def delete_request(conn, username):
    '''
    If the user is logged in, then indicate that they are deleting their
    own account by setting own = "T". Otherwise, retrieve the input of which
    account they want to delete. Pack and send to server.

    :param username: current_id from client side
    '''
    if username:
        print "\nDELETING YOUR ACCOUNT \n"
        own = "T"
    else:
        username = raw_input(
            'Enter the username of the account to be deleted: ')
        own = "F"
    username += own
    print "here"
    send_message('\x01' + pack('!I', 6) + '\x70' +
                     pack(config.request_body_fmt['\x70'], username), conn)


# list
def list_request(conn):
    '''
    Requests user to make a selection from functions. Set the
    regular expression accordingly. Pack and send to server
    '''
    raw = raw_input(
        '''
        Choose from the following options:
        0) List all users
        1) List users whose username match a specified regular expression.

        Please enter your choice below.
        ''')
    if raw == str(0):
        print "\nLISTING ALL ACCOUNTS \n"
        regexp = ".*"
    else:
        regexp = raw_input("Enter the regexp used to search the user list.")

    send_message('\x01' + pack('!I', len(regexp)) + '\x50' +
                 pack(config.request_body_fmt['\x50'] % len(regexp), regexp),
                conn)

# message sending
def send_message_request(sock, current_user):
    '''
    Method is executed once a user has indicated that they wish to
    send a message to another user.
    Prompts user for details of this message, and sends it.

    :param sock: Socket object of connection to client.
    :param current_user: string, sending user's username.
    '''
    while True:
        print '''
        Enter the username of the user who you would like to send a
        message to. Usernames are five characters long.
        '''
        receiving_user = raw_input()
        if len(receiving_user) == 5:
            break

    print ("Enter the message you'd like to send to this user. "
           "Messages are limited to 1008 characters.")
    message = raw_input("you to %s:" % receiving_user)
    while len(message) > 1008:
        message = raw_input("you to %s:" % receiving_user)

    payload_len = (2 * config.username_length) + len(message)
    fmt_str = config.request_body_fmt['\x30'] % len(message)
    send_message('\x01' + pack('!I', payload_len) + '\x30' +
                 pack(fmt_str,
                      current_user, receiving_user, message),
                 sock)


# message delivery
def deliver_request_success(conn, username):
    '''
    Message sent from the client to the server indicating that a
    chat message has successfully been recvd by the client and displayed.

    :param conn: Socket object representing connection to server.
    :param username: current user logged in, to whom delivery succeeded.
    '''
    send_message('\x01' + pack('!I', 5) + '\x81' +
                 pack(config.request_body_fmt['\x81'], username), conn)


def deliver_request_failure(conn, reason):
    '''
    Message sent from the client to the server indicating that a
    chat message has not successfully been recvd by the client and displayed.

    :param conn: Socket object representing connection to server.
    :param reason: A string indicating why the delivery might have failed, for
    example the user logged in is not the one for whom the message was
    intended.
    '''
    send_message(
        '\x01' + pack('!I', len(reason)) + '\x82' +
        pack(config.request_body_fmt['\x82'] % len(reason), reason), conn)
