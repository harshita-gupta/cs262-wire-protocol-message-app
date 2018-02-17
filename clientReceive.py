from struct import unpack
import config
from config import *


def reason_string(buf):
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
    return True, ""


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
    print "\nMessage sending failed.", reason_string(buf)
    return True, ""
