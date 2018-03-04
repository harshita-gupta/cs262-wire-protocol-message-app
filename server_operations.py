from struct import unpack, pack
from config import *
from server_state import send_or_queue_message


################################################
# SERVER OPERATIONS ########################
################################################

'''
This file contains the implementations for all operations that the server
supports.
'''


# OPERATION 1: CREATE REQUEST

def create_request(conn, buf, _, lock, accounts, active_clients, pack_fmt):
    '''
    Processes a creation request from a client.
    If the operation succeeds, sends a creation success message to the client
    at conn, and if it fails, sends a creation failure message to the client
    at conn. Failure and success requirements are defined by the
    accounts.add_account method,
    which create_request is simply a user-interaction wrapper for.

    If the user is successfully created, also logs in the client that initiated
    the request.

    :param conn: socket object containing the connection to the client.
    :param buf: byte buffer containing the create request message body
    :param lock: the lock primitive that we use to ensure that only one message
    is sent to a server at a time, and two messages originating from different
    threads (eg. server's response to a request and another client's
    message delivery) do not get delivered simultaneously and thus
    garble each other's byes. The lock object is acquired before any
    connection.send operation.
    :param accounts: the server_state.AccountList object. This is a
    reference to the server's database that this client will send
    access/transaction requests to.
    :param active_clients: the server_state.ActiveClients object.
    This is also a reference to a server database object that facilitates
    the transaction requests initated by the server.
    :param pack_fmt: The fornat used to unpack the message body of the create
    request.

    :return: None.
    '''

    # Helper functions
    def send_create_success(connection, username):
        print"sending create success"
        send_message('\x01' + pack('!I', 5) + '\x11' +
                     pack(username_fmt, username), connection)

    def send_create_failure(connection, username, reason):
        print"sending create failure"
        send_message(
            '\x01' + pack('!I', len(reason)) + '\x12' +
            pack(request_body_fmt['\x12'] % len(reason), reason),
            connection)

    values = unpack(pack_fmt, buf[6:14])
    username = values[0]
    success, error = accounts.add_account(username)
    with lock:
        if success:
            active_clients.log_in(username, lock, conn, accounts)
            send_create_success(conn, username)
        else:
            send_create_failure(conn, username, error)


# OPERATION 2: LOGIN REQUEST

def login_request(conn, buf, _, lock, accounts, active_clients, pack_fmt):
    '''
    Processes a log in request from a client.
    If the operation succeeds, sends a log in success message to the client
    at conn, and if it fails, sends a log in failure message to the client
    at conn. Failure and success requirements are defined by the
    active_clients.log_in method,
    which login_request is simply a user-interaction wrapper for.

    If the client successfully logs in, also attempts to deliver
    all the pending messages to the client
    using the acounts.deliver_pending_messages method.

    :param conn: socket object containing the connection to the client.
    :param buf: byte buffer containing the login request message body
    :param lock: the lock primitive that we use to ensure that only one message
    is sent to a server at a time, and two messages originating from different
    threads (eg. server's response to a request and another client's
    message delivery) do not get delivered simultaneously and thus
    garble each other's byes. The lock is acquired before any
    connection.send operation.
    :param accounts: the server_state.AccountList object. This is a
    reference to the server's database that this client will send
    access/transaction requests to.
    :param active_clients: the server_state.ActiveClients object.
    This is also a reference to a server database object that facilitates
    the transaction requests initated by the server.
    :param pack_fmt: The fornat used to unpack the message body of the login
    request.

    :return: None.
    '''

    # Helper functinos
    def send_login_success(connection, username):
        print"sending login success"
        send_message('\x01' + pack('!I', 5) + '\x21' +
                     pack(username_fmt, username), connection)

    def send_login_failure(connection, reason):
        print"sending login failure"
        send_message(
            '\x01' + pack('!I', len(reason)) + '\x22' +
            pack(request_body_fmt['\x22'] % len(reason), reason),
            connection)

    values = unpack(pack_fmt, buf[6:14])
    username = values[0]
    success, info = active_clients.log_in(username, lock, conn, accounts)
    if success:
        with lock:
            send_login_success(conn, username)
        dsuccess, dinfo = accounts.deliver_pending_messages(
            username, lock, conn)
        if not dsuccess:
            print "Delivery of pending messages failed", dinfo
    else:
        with lock:
            send_login_failure(conn, info)


# OPERATION 3: LOGOUT REQUEST

def send_logout_success(connection):
    print"sending logout success"
    send_message('\x01' + pack('!I', 0) + '\x61', connection)


def logout_request(conn, buf, _, lock, accounts, active_clients, pack_fmt):
    '''
    Processes a log in request from a client.
    If the operation succeeds, sends a log in success message to the client
    at conn, and if it fails, sends a log in failure message to the client
    at conn. Failure and success requirements are defined by the
    active_clients.log_in method,
    which login_request is simply a user-interaction wrapper for.

    If the client successfully logs in, also attempts to deliver
    all the pending messages to the client
    using the acounts.deliver_pending_messages method.

    :param conn: socket object containing the connection to the client.
    :param buf: byte buffer containing the login request message body
    :param lock: the lock primitive that we use to ensure that only one message
    is sent to a server at a time, and two messages originating from different
    threads (eg. server's response to a request and another client's
    message delivery) do not get delivered simultaneously and thus
    garble each other's byes. The lock is acquired before any
    connection.send operation.
    :param accounts: the server_state.AccountList object. This is a
    reference to the server's database that this client will send
    access/transaction requests to.
    :param active_clients: the server_state.ActiveClients object.
    This is also a reference to a server database object that facilitates
    the transaction requests initated by the server.
    :param pack_fmt: The fornat used to unpack the message body of the login
    request.

    :return: None.
    '''

    values = unpack(pack_fmt, buf[6:14])
    username = values[0]
    active_clients.log_out(username)
    with lock:
        send_logout_success(conn)
    return


# OPERATION 4: DELETE REQUEST

def send_delete_success(conn):
    print"sending delete success"
    send_message('\x01' + pack('!I', 0) + '\x71', conn)
    return


def send_delete_failure(conn, reason):
    print"sending delete failure"
    send_message('\x01' + pack('!I', 0) + '\x72', conn)


def delete_request(conn, buf, _, lock, accounts, active_clients, pack_fmt):
    values = unpack(pack_fmt, buf[6:12])
    username = values[0][0:5]
    own = values[0][5]
    if username in active_clients.sockets:
        # if username is logged in and it's not yourself
        if own == "F":
            with lock:
                send_delete_failure(
                    conn,
                    ("Cannot delete account of a different"
                        " user who is currently logged in."))
            return
        active_clients.log_out(username)
    success, reason = accounts.delete_account(username)
    if success:
        with lock:
            send_delete_success(conn)
    else:
        with lock:
            send_delete_failure(conn, reason)
    return


# OPERATION 5: LIST REQUEST

def send_list_success(conn, accounts):
    logging.info("sending list success")
    send_message(
        '\x01' + pack('!I', len(accounts)) + '\x51' +
        pack(request_body_fmt['\x51'] % len(accounts), accounts), conn)


def list_request(conn, buf, payload_len, lock, accounts,
                 active_clients, pack_fmt):
    header = unpack(pack_header_fmt, buf[:6])
    pack_fmt = pack_fmt % payload_len
    print pack_fmt
    print buf[6:14]
    regexp = unpack(pack_fmt, buf[6:14])[0]
    if regexp == ".*":
        accs = accounts.list_accounts()
    else:
        accs = accounts.list_accounts_with_regex(regexp)
    print accs
    with lock:
            send_list_success(conn, accs)


# OPERATION 6: SEND MESSAGE REQUEST


def send_message_failure(connection, reason):
    print "Sending failure of send message operation"
    send_message(
        '\x01' + pack('!I', len(reason)) + '\x32' +
        pack(request_body_fmt['\x32'] % len(reason), reason), connection)
    return None


def send_message_success(username, connection):
    print "sening success of send message"
    send_message('\x01' + pack('!I', 5) + '\x31' +
                 pack(username_fmt, username), connection)
    return None


def send_message_request(connection, buf, payload_len,
                         lock, accounts, active_clients, pack_fmt):
    header = unpack(pack_header_fmt, buf[:6])
    pack_fmt = pack_fmt % (payload_len - (2 * username_length))
    receiving_user = unpack(pack_fmt, buf[6:payload_len + 6])[1]

    success, error = send_or_queue_message(
        accounts, active_clients, receiving_user,

        # send_or_queue accepts a packed package of what should be
        # delivered to the client.
        # this is the same as what was received, with a changed op code.
        pack(pack_header_fmt, header[0], header[1], '\x80') +
        buf[6:payload_len + 6])

    with lock:
        if success:
            send_message_success(receiving_user, connection)
        else:
            send_message_failure(connection, error)

    return None


################################################
# DELIVERY CONFIRMATIONS ########################
################################################

# This section of the file contains the two functions
# that confirm to the server that a client received its delivery.

# CONFIRM RECEIPT
def deliver_message_success(conn, netBuffer, payload_len, lock, accounts,
                            active_clients, pack_fmt):
    values = unpack(username_fmt, netBuffer[6:14])
    print "\nSuccessfully delivered message to %s" % values[0]


def deliver_message_failure(conn, netBuffer, payload_len, lock, accounts,
                            active_clients, pack_fmt):
    reason = unpack(request_body_fmt['\x32'] %
                    payload_len - (2 * username_length),
                    netBuffer[6:payload_len + 6])[0]

    print "\nDelivering message failed.", reason


################################################
# OPERATION CODES - FUNCTION MAPPINGS ##########
################################################


# Operation codes that can be received and processed by the server.
opcodes = {'\x10': create_request,
           '\x20': login_request,
           '\x50': list_request,
           '\x60': logout_request,
           '\x70': delete_request,
           '\x30': send_message_request,
           '\x81': deliver_message_success,
           '\x82': deliver_message_failure
           }
