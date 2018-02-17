# File that implements key functions for the server.
# Calls methods in serverSend.py and serverReceive.py

# first of all import the socket library
import socket
import traceback
import thread
import config
import logging
from server_operations import opcodes, send_logout_success
from server_state import AccountList, ActiveClients
from struct import unpack


version = '\x01'


# handle invalid opcodes
def unknown_opcode(conn):
    conn.send('\x01\x00\x00\x00\x00\x62')
    return


def recordConnect(addr):
    print 'Opened connection with ' + addr
    logging.info('Opened connection with ' + addr + '\n')
    logging.flush()


# threaded method for handling an individual client
def handle_client(connection, lock, accounts, active_clients):
    # keep track of erroneous opcodes
    second_attempt = 0
    while True:
        try:
            netBuffer = connection.recv(1024)
        except:
            print "ERROR: connection down"
            thread.exit()
        if len(netBuffer) >= 6:
            # unpack the header of the message, i.e.
            # version number, payload length, op code
            # therefore !cIc
            header = unpack(config.pack_header_fmt, netBuffer[0:6])
            print header

            # only allow correct version numbers and
            # buffers that are of the appropriate length
            sent_version = header[0]
            payload_len = header[1]
            if sent_version == version and len(netBuffer) == payload_len + 6:
                opcode = header[2]
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
        thread.start_new_thread(
            handle_client, (sock, lock, accounts, active_clients))
