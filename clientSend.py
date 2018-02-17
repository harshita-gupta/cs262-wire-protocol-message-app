import config
from config import send_message
from struct import pack
from sys import maxint, exit


# create new account
def create_request(conn):

    print "CREATING AN ACCOUNT \n"
    print "enter a username of alphanumeric characters under 20 characters:"
    while True:
        userInput = raw_input('>> ')
        if(userInput.isalnum() and len(userInput) <= 5):
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
    print "DELETING YOUR ACCOUNT \n"
    send_message('\x01' + pack('!I', 5) + '\x70' +
                 pack(config.username_fmt, username), conn)

    return

# message delivery
def deliver_request_success(conn, username):
    send_message('\x01' + pack('!I', 5) + '\x10' +
                 pack(config.username_fmt, username), conn)


def deliver_request_failure(conn, reason):
    send_message(
        '\x01' + pack('!I', len(reason)) + '\x10' +
        pack(config.deliver_request_failure % len(reason), reason), conn)
