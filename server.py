# File that implements key functions for the server.
# Calls methods in serverSend.py and serverReceive.py

# first of all import the socket library
import socket
import thread
import config
import threading
import logging
from collections import deque


version = '\x01'

# Operation codes that can be received and processed by the server.
opcodes = {'\x10': myServerReceive.create_request,
           '\x20': myServerReceive.delete_request,
           '\x30': myServerReceive.deposit_request,
           '\x40': myServerReceive.withdraw_request,
           '\x50': myServerReceive.balance_request,
           '\x60': myServerReceive.end_session
           }


class ActiveClients(object):
    def __init__(self):
        """
        Constructor.
        @param urls list of urls to check
        @param output file to write urls output
        """
        self.lock = threading.lock()

        # dictionary that stores username as keys and
        # socket objects as values
        self.sockets = {}

    def log_out(self, username):
        if not self.sockets.get(username):
            return (False, "Username not currently logged in")
        logging.info("Waiting to obtain lock for active socket conns dict.")
        with self.lock:
            self.sockets[username].close()
            logging.info(
                "Successfully closed connection with socket for username %s",
                username)
        return True

    def log_in(self, username, sock, account_list):
        logging.info("Waiting to obtain lock for account list")
        with account_list.lock:
            if username not in account_list.accounts:
                return (
                    False,
                    "Username %s does not exist any longer." % username)
            with self.lock:
                if self.sockets.get(username):
                    return (
                        False,
                        "User %s is already logged in elsewhere." % username)
                self.sockets[username] = sock
        return True


class AccountList(object):
    def __init__(self):
        """
        Constructor.
        @param urls list of urls to check
        @param output file to write urls output
        """
        self.lock = threading.lock()

        # list of all valid usernames
        self.accounts = []

        # dictionary with usernames as keys
        # values are tuples of
        #       1) a Lock and
        #       2) a deque that contains undelivered messages
        self.pending_messages = {}

    def add_account(self, username):
        # TODO check that username is alphanumeric
        logging.info("Waiting to obtain accountList")
        with self.lock:
            if username in accounts:
                return (False, "Username already exists.")
            else:
                self.accounts.append(username)
                self.pending_messages[username] = (threading.Lock,
                                                   deque())
        return True

    def add_pending_message(self, sending_user, receiving_user, message):
        # list of accounts should not be modified while adding a message
        logging.info("waiting to obtain accountList")
        with self.lock:
            if sending_user not in self.accounts:
                return (False, "Sending user no longer exists")
            if receiving_user not in self.accounts:
                return (False, "Receiving user no longer exists")
            with self.pending_messages[receiving_user][0]:
                self.pending_messages[receiving_user].append(message)
        return True


accounts = AccountList()
active_clients = ActiveClients()

def create_request(username):
    # define request creation here
    return None


def send_create_success(username):

    return None


def send_create_failure(username, reason):
    return None


def delete_request(username):
    return None


def send_delete_success(username):
    return None


def send_delete_failure(username, reason):
    return None


def send_message_request(sending_user, receiving_user, message):
    return None


def send_message_failure(reason):
    return None


def send_message_success():
    return None


def list_users_request():
    return None


def send_list_users_success():
    return None


def send_list_users_failure():
    return None


def recordConnect(addr):
    print 'Opened connection with ' + addr
    logging.info('Opened connection with ' + addr + '\n')
    logging.flush()


# threaded method for handling an individual client
def handle_client(connection, lock):
    # keep track of erroneous opcodes
    second_attempt = 0
    while True:
        try:
            netBuffer = conn.recv(1024)


if __name__ == '__main__':
    # set up logging
    logging.basicConfig(
        format='[thread %(threadname)s; %(funcName)20s() %(asctime)s [%(levelname)s] %(message)s',
        filename="serverLog.log")

    # next create a socket object
    s = socket.socket()
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

    # a forever loop until we interrupt it or
    # an error occurs
    while True:

        # Establish connection with client.
        sock, addr = s.accept()

        # log connection
        recordConnect(str(addr))

        # send a thank you message to the client.
        sock.send('Thank you for connecting')

        # start a new thread
        lock = thread.allocate_lock()
        thread.start_new_thread(handle_client, (sock, lock))
