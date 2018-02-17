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
    send_message(
        '\x01' + pack('!I', 0) + '\x12',
        connection)
    return None


def create_request(conn, buf, _, lock, accounts, active_clients, pack_fmt):
    values = unpack(pack_fmt, buf[6:14])
    username = values[0]
    success, error = accounts.add_account(username)
    with lock:
        if success:
            active_clients.log_in(username, lock, conn, accounts)
            send_create_success(conn, username)
        else:
            send_create_failure(conn, username, error)
    return


# LOGIN REQUEST

def send_login_success(connection, username):
    print"sending login success"
    send_message('\x01' + pack('!I', 5) + '\x21' +
                 pack(username_fmt, username), connection)
    return


def send_login_failure(connection):
    print"sending login failure"
    send_message(
        '\x01' + pack('!I', 0) + '\x22',
        connection)
    return None

def login_request(conn, buf, _, lock, accounts, active_clients, pack_fmt):
    values = unpack(pack_fmt, buf[6:14])
    username = values[0]
    print active_clients.list_active_clients()
    success, info = active_clients.log_in(username, lock, conn, accounts)
    if success == True:
        with lock: 
            send_login_success(conn, username) 
    else:
        with lock: 
            send_login_failure(conn)
    return


# LOGOUT REQUEST


def send_logout_success(connection):
    print"sending logout success"
    send_message('\x01' + pack('!I', 0) + '\x61', connection)
    return


def logout_request(conn, buf, _, lock, accounts, active_clients, pack_fmt):
    values = unpack(pack_fmt, buf[6:14])
    username = values[0]
    active_clients.log_out(username)
    with lock:
        send_logout_success(conn)
    return


# DELETE REQUEST

def send_delete_success(conn):
    print"sending delete success"
    send_message('\x01' + pack('!I', 0) + '\x71', conn)
    return


def send_delete_failure(conn, reason):
    print"sending delete failure"
    send_message('\x01' + pack('!I', 0) + '\x72', conn)


def delete_request(conn, buf, _, lock, accounts, active_clients, pack_fmt):
    values = unpack(pack_fmt, buf[6:14])
    username = values[0]
    if username in active_clients.sockets: 
        active_clients.log_out(username)
    success, reason = accounts.delete_account(username)
    if success == True: 
        with lock:
            send_delete_success(conn)
    else:
        with lock: 
            send_delete_failure(conn, reason)
    return


# LIST REQUEST

def send_list_success(conn, accounts):
    print"sending list success"
    send_message('\x01' + pack('!I', 0) + '\x51', conn)
    return


def list_request(conn, buf, _, lock, accounts, active_clients, pack_fmt):
    accounts = accounts.list_accounts()
    print accounts
    with lock: 
            send_list_success(conn, accounts)
    return


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


# Operation codes that can be received and processed by the server.
opcodes = {'\x10': create_request,
           '\x20': login_request,
           '\x50': list_request,
           '\x60': logout_request,
           '\x70': delete_request}
           # '\x30': send_message_request,
           # '\x50': list_users_request,
