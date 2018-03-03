# File that implements key functions for the server.
# Calls methods in server_state.py and server_operations.py

import socket
import traceback
import thread
import config
import logging
from server_operations import opcodes, send_logout_success
from server_state import AccountList, ActiveClients
from struct import unpack


version = '\x01'


def unknown_opcode(conn):
    '''
    Sends a message to conn that indicates that an invalid opcode
    was sent to the server.

    :param conn: the socket object that is used to send the message to the
                problematic client
    :return: None
    '''
    conn.send('\x01\x00\x00\x00\x00\x62')
    return


def recordConnect(addr):
    '''
    A function without side effects that logs the opening of a connection to
    addr by flushing it to the log file and printing it to console.

    :param addr: the address of the connection created.
    :return: none
    '''
    print 'Opened connection with ' + addr
    logging.info('Opened connection with ' + addr + '\n')
    logging.flush()


def get_client_message(connection):
    '''
    Attempts to receive a message from the client.
    Checks for a message that is MESSAGE_MAX_SIZE.
    Ends the client's thread if the connection is down.
    If a message is successfully received, unpacks its header
    and returns the header's three properties: protocol version number,
    payload length, and the operation code. In addition to the header's
    three properties, returns a buffer containing the message body.

    :param conn: socket object containing the connection to the client.
    :return: tuple with four elements. (protocol version number,
    payload length, operation code, message body buffer)
    '''

    try:
        netBuffer = connection.recv(1024)
    except:
        print "ERROR: connection down"
        thread.exit()

    if len(netBuffer) < 6:
        return None

    # unpack the header of the message, i.e.
    # version number, payload length, op code
    # therefore !cIc
    header = unpack(config.pack_header_fmt, netBuffer[0:6])
    return header[0], header[1], header[2], netBuffer


# threaded method for handling an individual client
def handle_client(connection, lock, accounts, active_clients):
    '''
    handle_client is started on a new thread by the primary server loop.
    It monitors the connection with each individual client, receives messages
    from the client, and responds to them.

    If an invalid opcode is sent to the server, the server allows the
    client a second attempt before closing the connection,
    so that no spamming clients are supported.

    :param connection: socket object representing the connection to the client.
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

    :return: Only returns if the connection with the client is dropped,
    either because the client sent too many erroneous messages
    or because the client shut down, in which case it returns None.
    '''

    # keep track of erroneous opcodes
    second_attempt = 0
    while True:

        client_message = get_client_message(connection)
        if not client_message:
            continue

        recv_version, payload_len, opcode, netBuffer = client_message

        # only allow correct version numbers and
        # buffers that are of the appropriate length
        if recv_version == version and len(netBuffer) == payload_len + 6:

            # try to send packet to correct handler
            try:
                print opcodes[opcode]
                opcodes[opcode](
                    connection, netBuffer, payload_len, lock, accounts,
                    active_clients, config.request_body_fmt[opcode])

            # catch unhandled opcodes
            # we allow one retry before the client is booted
            # for sending useless inputs too often.
            except:
                traceback.print_exc()
                if second_attempt:

                    # disconnect the client
                    with active_clients.lock:
                        for key, (l, s) in active_clients.sockets:
                            if s == connection:
                                del active_clients.sockets[key]
                                break
                    with lock:
                        send_logout_success(connection)
                    return
                else:
                    # send incorrect opcode message
                    second_attempt = 1
                    unknown_opcode(connection)
        else:
            # TODO can potentially check to make sure that
            # there is no pending delivery waiting in socket
            continue


if __name__ == '__main__':
    '''
    Server's main loop logic. Completes basic configuration for the
    server and then sets up a socket to receive client connections over.
    Instantiates state objects i.e. active clients list, account list,
    pending messages list.
    Receives connections from clients and spawns new thread to manage each
    client, where it receives messages and responds to them.
    '''
    # set up logging
    logging.basicConfig(
        format=config.logging_fmt,
        filename="serverLog.log")

    # next create a socket object
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print "Socket successfully created"

    # Next bind to the port
    # we have not typed any ip in the ip field
    # instead we have inputted an empty string
    # this makes the server listen to requests
    # coming from other computers on the network
    s.bind(('', config.port))
    print "socket binded to %s" % (config.port)

    # put the socket into listening mode
    s.listen(5)
    print "socket is listening"

    # CREATE STATE OBJECTS
    accounts = AccountList()
    active_clients = ActiveClients()

    # a forever loop until we interrupt it or
    # an error occurs
    while True:

        # Establish connection with client.
        sock, addr = s.accept()

        # log connection
        # recordConnect(str(addr))

        # send a thank you message to the client.
        # start a new thread
        lock = thread.allocate_lock()

    # the handle_client method receives client messages
    # and triggers the appropriate server operation to respond to that
    # client message.
        thread.start_new_thread(
            handle_client, (sock, lock, accounts, active_clients))
