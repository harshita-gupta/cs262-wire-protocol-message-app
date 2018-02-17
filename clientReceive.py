from struct import unpack
from config import *


def create_success(conn, netBuffer):
    values = unpack(username_fmt, netBuffer[6:14])
    current_user = values[0]
    print "Account creation successful"
    return True, current_user


def create_failure(conn, netBuffer):
    print "Account creation failure--username already exists"
    return False, ""


def login_success(conn, netBuffer):
    values = unpack(username_fmt, netBuffer[6:14])
    current_user = values[0]
    print "Account creation successful"
    return True, current_user


def login_failure(conn, netBuffer):
    print "Login failure. Please enter an existing username."
    return False, ""


def logout_success(conn, netBuffer):
    print "Successfully logged out"
    return True, ""


def delete_success(conn, netBuffer):
    print "Successfully deleted account"
    return True, ""

def delete_failure(conn, netBuffer):
    print "Cannot delete account because of pending messages or account does not exist"
    return True, ""


def send_message_success(conn, netBuffer):
    values = unpack(username_fmt, netBuffer[6:14])
    print "Successfully sent message to %s" % values[0]


def send_message_failure(conn, netBuffer):
    header = unpack(pack_header_fmt, retBuffer[0:6])
    reason = unpack(request_body_fmt['\x32'] %
                    header[1] - (2 * username_length),
                    netBuffer[6:header[1] + 6])[0]

    print "Message sending failed.", reason
