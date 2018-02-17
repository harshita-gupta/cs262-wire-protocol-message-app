import config
from config import send_message
from struct import pack
from sys import maxint, exit


# create new account
def create_request(conn):

    print "CREATING AN ACCOUNT \n"
    print "enter a an alphanumeric username five characters long:"
    while True:
        userInput = raw_input('>> ')
        if(userInput.isalnum() and len(userInput) == 5):
            username = userInput
            break

    send_message('\x01' + pack('!I', 5) + '\x10' +
                 pack(config.username_fmt, username), conn)

    return


# log in to an existing account
def login_request(conn):

    print "LOGGING IN \n"
    print "Enter your username"
    while True:
        userInput = raw_input('>> ')
        if(userInput.isalnum() and len(userInput) <= 5):
            username = userInput
            break

    send_message('\x01' + pack('!I', 5) + '\x20' +
                 pack(config.username_fmt, username), conn)
    return


# log out
def logout_request(conn, username):
    print "LOGGING OUT \n"
    send_message('\x01' + pack('!I', 5) + '\x60' +
                 pack(config.username_fmt, username), conn)

    return


# delete
def delete_request(conn, username):
    if username != None: 
        print "DELETING YOUR ACCOUNT \n"
        send_message('\x01' + pack('!I', 5) + '\x70' +
                     pack(config.username_fmt, username), conn)
    else:
        username = raw_input('Enter the username of the account to be deleted: ')
        send_message('\x01' + pack('!I', 5) + '\x70' +
                     pack(config.username_fmt, username), conn)

    return

# list
def list_request(conn):
    print "LISTING ALL ACCOUNTS \n"
    send_message('\x01' + pack('!I', 5) + '\x50' +
        pack(config.username_fmt, ""), conn)

    return


# message sending
def send_message_request(sock, current_user):
    while True:
        print '''
        Enter the username of the user who you would like to send a
        message to. Usernames are five characters long.
        '''
        receiving_user = raw_input()
        if len(receiving_user) == 5:
            break

    print "Enter the message you'd like to send to this user."
    message = raw_input()
    send_message('\x01' +
                 pack('!I', (2 * config.username_length) + len(message)) +
                 '\x30' +
                 pack(config.request_body_fmt['\x30'] % len(message), message),
                 sock)
    # send message!


# message delivery
def deliver_request_success(conn, username):
    send_message('\x01' + pack('!I', 5) + '\x10' +
                 pack(config.username_fmt, username), conn)


def deliver_request_failure(conn, reason):
    send_message(
        '\x01' + pack('!I', len(reason)) + '\x10' +
        pack(config.deliver_request_failure % len(reason), reason), conn)
