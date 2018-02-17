import thread
import logging

# Define the port on which you want to connect
port = 12345
username_length = 5

pack_header_fmt = '!cIc'

username_fmt = "!%is" % username_length

# dictionary linking opcodes to format strings used for packing and unpacking
request_body_fmt = {

    ########
    # ACCOUNT MANAGEMENT CODES
    # must format these with length of reason string
    ########

    '\x10': username_fmt,  # create request
    '\x20': username_fmt,  # log in request
    '\x50': "",            # list users request
    '\x51': "!%is",            # list users success, has list attached
    '\x60': username_fmt,  # log out request
    '\x70': username_fmt, # delete request 

    ########
    # SUCCESS CODES
    ########

    '\x11': username_fmt,  # create success
    '\x71': "",            # delete success, no payload
    '\x21': "",            # log in success, no payload
    '\x31': username_fmt,  # send message success
    '\x81': username_fmt,  # deliver message success

    ########
    # FAILURE CODES
    # must format these with length of reason string
    ########

    '\x12': "!%is",  # create failure
    '\x22': "!%is",  # delete failure
    '\x32': "!%is",  # send message failure
    '\x52': "!%is",  # list users failure
    '\x82': "!%is",  # deliver message failure
    '\x72': "!%is",  # log in failure

    ########
    # Message sending codes
    # must format these with length of reason string
    ########

    # # send message request, must format with length of message string
    '\x30': username_fmt + ("%is" % username_length) + "%is",

    # deliver message request, must format with length of message string
    '\x80': username_fmt + ("%is" % username_length) + "%is",

}

logging_fmt = ('[thread %(threadname)s;'
               '%(funcName)20s() %(asctime)s %(levelname)s] %(message)s')


logging.basicConfig(
    format=logging_fmt)


def send_message(message, conn):
    try:
        conn.send(message)
    except:
        # close the client if the connection is down
        logging.error("ERROR: connection down")
        thread.exit()
    return
