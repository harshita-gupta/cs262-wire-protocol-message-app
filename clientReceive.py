from struct import unpack
import config
from config import *

'''
These functions deliver success/failure messages to the client after 
recceiving them from the server. These functions are called by client.py 
after receiving a response from the server (which comes after the client 
sends a request in clientSend.py). In the cases where a reason is provided
for the success or failure, the function will display that reason to the 
client as well. 

:param netBuffer: Raw message received over the wire from the server 
:return: Except for reason_string(buf), all functions return a tuple of 
a boolean representing success (True) or failure (False) and an optional 
field that can be used to pass the current_id back to the client if 
the login was successful, so that the client may reset that variable. 
'''

def reason_string(buf):
    '''
    Unpacks the header and reason string of a message from the server 
    sent over the wire. 

    :param buf: Raw message received over the wire from the server
    :return: String representation of the reason 
    '''
    header = unpack(pack_header_fmt, buf[0:6])
    reason = unpack(request_body_fmt['\x32'] %
                    header[1],
                    buf[6:header[1] + 6])[0]
    return reason


def create_success(conn, netBuffer):
    values = unpack(username_fmt, netBuffer[6:14])
    current_user = values[0]
    print "\nAccount creation successful"
    return True, current_user


def create_failure(conn, netBuffer):
    print "\nAccount creation failure.", reason_string(netBuffer)
    return False, ""


def login_success(conn, netBuffer):
    values = unpack(username_fmt, netBuffer[6:14])
    current_user = values[0]
    print "\nLog in successful"
    return True, current_user


def login_failure(conn, netBuffer):
    print "\nLogin failure.", reason_string(netBuffer)
    return False, ""


def logout_success(conn, netBuffer):
    print "\nSuccessfully logged out"
    return True, ""


def delete_success(conn, netBuffer):
    print "\nSuccessfully deleted account"
    return True, ""


def delete_failure(conn, netBuffer):
    print "\nCannot delete account", reason_string(netBuffer)
    return False, ""


def list_success(conn, netBuffer):
    header = unpack(config.pack_header_fmt, netBuffer[0:6])
    length = header[1]
    values = unpack(
        config.request_body_fmt['\x51'] % length, netBuffer[6:6 + length])
    print "Accounts: " + values[0]
    return True, ""


def send_message_success(conn, netBuffer):
    values = unpack(username_fmt, netBuffer[6:11])
    print "\nSuccessfully sent message to %s" % values[0]
    return True, ""


def send_message_failure(conn, netBuffer):
    print "\nMessage sending failed.", reason_string(netBuffer)
    return False, ""
