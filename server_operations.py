from struct import unpack, pack
from config import *
# from server_state import send_or_queue_message

# CREATE REQUEST


def send_create_success(connection, username):
    print"sending create success"
    send_message('\x01' + pack('!I', 5) + '\x11' +
                 pack(username_fmt, username), connection)
    return


def send_create_failure(connection, username, reason):
    print"sending create failure"
    # TODO question for lisa: are we sending the reason right now?
    send_message('\x01' + pack('!I', 4) + '\x12', connection)
    return None


def create_request(conn, buf, _, lock, accounts, active_clients, pack_fmt):
    values = unpack(pack_fmt, buf[6:14])
    username = values[0]
    with lock:
        success, error = accounts.add_account(username)
        if success:
            # QUESTION: do we want to automatically log a user in when
            # they create an account?
            active_clients.log_in(username, lock, conn, accounts)
            send_create_success(conn, username)
        else:
            send_create_failure(conn, username, error)
    return


# LOGIN REQUEST

def login_request(conn, buf, _, lock, accounts, active_clients, pack_fmt):
    values = unpack(pack_fmt, buf[6:14])
    username = values[0]
    with lock:
        if username in accounts.accounts and username not in active_clients.sockets:
            print "login ok"
        # if success:
        #     send_create_success(conn, username)
        #     active_clients.log_in(username, lock, conn, accounts)
        # else:
        #     send_create_failure(conn, username, success[1])
    return


# LOGOUT REQUEST


def send_logout_success(connection):
    print"sending logout success"
    send_message('\x01' + pack('!I', 0) + '\x61', connection)
    return


def logout_request(conn, buf, _, lock, accounts, active_clients, pack_fmt):
    values = unpack(pack_fmt, buf[6:14])
    username = values[0]
    print "active: " + str(active_clients.list_active_clients())
    with lock: 
        print "obtained lock"
        success, error = active_clients.log_out(username)
        print "success" + str(success) 
        print "active: " + str(active_clients.list_active_clients())
    # NOTE TO LISA: there is a case in which active_clients.log_out will
    # return failure, i.e. if the user is already logged out --
    # we should accmodate for this i think?
        send_logout_success(conn)
    return


# DELETE REQUEST

def send_delete_success(username):
    return None


def send_delete_failure(username, reason):
    return None


def delete_request(conn, buf, _, lock, accounts, active_clients, pack_fmt):
    return None


# SEND MESSAGE REQUEST


def send_message_failure(connection, reason):

    return None


def send_message_success(connection):
    connection.send('\x01' + pack('!I', 4) + '\x12')
    return None


def send_message_request(connection, buf, payload_len,
                         lock, accounts, active_clients, pack_fmt):
    deliver_header = unpack(pack_header_fmt, netBuffer[0:6])
    deliver_header[3] = '\x80'

    pack_fmt = pack_fmt % payload_len - (2 * username_length)
    receiving_user = unpack(pack_fmt, buf[6:payload_len + 6])[2]

    success, error = send_or_queue_message(
        accounts, active_clients, receiving_user,

        # send_or_queue accepts a packed package of what should be
        # delivered to the client.
        # this is the same as what was received, with a changed op code.
        pack(pack_header_fmt, deliver_header) + buf[6:payload_len + 6])

    with lock:
        if success:
            send_message_success(connection)
        else:
            send_message_failure(connection, error)

    return None


# LIST USERS FUNCTIONS

def send_list_users():
    return None


def list_users_request(connection,
                       buf, _, lock, accounts, active_clients, pack_fmt):
    return None


# LOG OUT FUNCTIONS

def log_out_success(connection):
    return None


def log_out(connection, buf, _, lock, accounts, active_clients, pack_fmt):
    return None


# LOG IN FUNCTIONS

def log_in_request(connection, buf, _,
                   lock, accounts, active_clients, pack_fmt):
    return None


# Operation codes that can be received and processed by the server.
opcodes = {'\x10': create_request,
           '\x20': login_request,
           '\x60': logout_request,
           # '\x30': send_message_request,
           # '\x50': list_users_request,
           # '\x70': log_in_request
           }
