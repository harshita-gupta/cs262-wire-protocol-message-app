import re
import threading
import logging
import thread
from struct import unpack
import config
from clientReceive import reason_string
from collections import deque

################################################
# STATE HANDLING ########################
################################################

'''
The server has three primary pieces of state that it needs to handle:
1. The list of created accounts that have not been deleted
2. Queues of undelivered messages for a given username, if that user is not
    currently connected to the server
3. A mapping from usernames of clients currently logged in to the socket
    socket objects that represent connections with these clients.

These pieces of state are encapsulated by the ActiveClients and
AccountList classes. The instance variables of these classes should not be
directly accessed, but instead object methods should be invoked to make
state modifications.
'''


def get_client_message(connection):
    ''' Retrieves a message over a socket and exists the client thread
    if the socket connection is down.
    :param connection: The socket object that represents the connection to the
    client.
    :return: Returns None if no message large enough to have a header was
    received. If a message large enough was received, returns a 4 element
    tuple with the protocol version number, the payload size, the opcode
    number, and the buffer containing the header and the payload.
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


class ActiveClients(object):
    '''
    ActiveClients handles the third piece of state described above.

    The primary data structure in Active Clients is a dictionary self.sockets
    that stores mappings of currently active usernames to their socket objects.

    Along with a lock associated with the top-level dictionary data structure,
    ActiveClients creates a lock for each spcific socket object.

    This socket-level lock is critical since distinct threads initiated by
    distinct clients can be interacting with the same socket,
    this occurs when one client is initiating a message delivery to another
    client.
    '''

    def __init__(self):
        """
        Constructor.
        """
        self.lock = threading.Lock()

        # dictionary that stores username as keys and
        # (locks, socket objects) as values
        self.sockets = {}

    def is_active(self, username):
        '''
        Checks if a user is active or not.

        :param username: Username of the user we are checking for.
        :return: Boolean indicating whether the user is logged in or not.
        '''
        with self.lock:
            if username in self.sockets:
                return True
            return False

    def log_out(self, username):
        '''
        Logs out a currently logged in user. Fails if user is not
        currently logged in, or does not exist.

        :param username: Username of the user to log out.
        :return: Tuple of Boolean, string, where boolean indicates whether
        the logout was successful and string is set to a failure reason
        if the logout failed.
        '''
        if not self.sockets.get(username):
            return (False, "Username not currently logged in")
        logging.info("Waiting to obtain lock for active socket conns dict.")
        with self.lock:
            logging.info("waiting to obtain lock for socket for %s", username)
            with self.sockets[username][0]:
                # self.sockets[username][1].close()
                logging.info(
                    "Successfully logged out %s's socket", username)
                del self.sockets[username]
        return (True, "")

    def log_in(self, username, lock, sock, account_list):
        '''
        Logs a client in as a user that exists in the database
        and that is not already logged in.

        :param username: The username of the user that the client
        wishes to log in as.
        :param lock: The lock for the client's connection
        :param sock: The socket object for the client connection
        :account_list: The account database object for the server.
        :return: Tuple of Boolean, string, where boolean indicates whether
        the login was successful and string is set to a failure reason
        if the login failed.
        '''
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
                        "User %s is already logged in." % username)
                self.sockets[username] = (lock, sock)
        return (True, "")


class AccountList(object):
    '''
    AccountList handles the first and second piece of server state,
    namely the list of all accounts that are undeleted, and
    queues of undelivered messages for a given username.

    There are two top-level data structures in AccountList.

    a. The list of accounts self.accounts, which has the lock self.lock
       associated with it.
    b. The dictionary that maps usernames to undelivered messages.
       Each username's undelivered message queue has a lock associated with it.
       Undelivered messages are stored as packed buffers of data
       matching the format of the x80 opcode.
    '''

    def __init__(self):

        self.lock = threading.Lock()

        # list of all valid usernames
        self.accounts = set()

        # dictionary with usernames as keys
        # values are tuples of
        #       1) a Lock and
        #       2) a deque that contains undelivered messages
        self.__pending_messages = {}

    def add_account(self, username):
        '''
        Adds a new account to the server database
        Fails if the account already exists, or if it does not meet
        the username length requirement.

        :param username: username of the new account
        :return: tuple of (boolean, String).
                 Returns (True, "") if the request succeeds, adn
                 (False, failure-reason) if the request fails.
        '''
        logging.info("Waiting to obtain accountList")
        with self.lock:
            if username in self.accounts:
                return (False, "Username already exists.")
            elif len(username) != 5:
                return (
                    False, "Username is only allowed to be five characters.")
            else:
                self.accounts.add(username)
                self.__pending_messages[username] = (threading.Lock(),
                                                     deque())
        return (True, "")

    def add_pending_message(self, receiving_user, pm):
        '''
        Adds a pending message to the dequeue of undelivered messages for
        that user, to be sent when the user is next online.

        :param receiving_user: The message recepient's username.
        :param pm: The message that should be sent to the user.
        pm is a message of bytes packed using struct.pack, packed according to
        the specifications for DELIVER_MESSAGE_REQUEST of a
        protocol version that the receiving user can understand.
        pm will be delivered to the receiving user in an unaltered format.

        :return: tuple of (boolean, String).
                 Returns (True, "") if the request succeeds, and
                 (False, failure-reason) if the request fails. Fails
                 if receiving_user does not exist in the server's database.
        '''
        logging.info("waiting to obtain accountList")
        with self.lock:
            # lock: list of accounts shouldn't be modified while adding message
            if receiving_user not in self.accounts:
                return (False, "Receiving user no longer exists")
            with self.__pending_messages[receiving_user][0]:
                self.__pending_messages[receiving_user][1].append(pm)
        return (True, "")

    def deliver_pending_messages(self, receiving_username, lock, sock):
        '''
        Delivers all pending messages for a given user to a client.
        Fails if the account does not exist, or if delivery to the client
        is responded to with an error message.

        :param receiving_username: username of the user whose pending messages
        should be dequeued and sent over the socket.
        :param lock: lock object that should be acquired before any
        messages are sent over the socket.
        :param sock: socket object over which to send messages,

        :return: tuple of (boolean, String).
                 Returns (True, "") if the request succeeds, and
                 (False, failure-reason) if the request fails.
        '''
        if not self.account_exists(receiving_username):
            return (False, "account %s does not exist." % receiving_username)
        logging.info(
            "waiting for lock on pending messages for %s" % receiving_username)
        with self.__pending_messages[receiving_username][0]:
            logging.info("waiting for lock on client thread")
            with lock:
                dq = self.__pending_messages[receiving_username][1]
                while dq:
                    config.send_message(dq[0], sock)
                    client_message = get_client_message(sock)
                    if not client_message:
                        print "connection with client dropped"
                        thread.exit()
                    _, payload_len, opcode, buf = client_message

                    if opcode != '\x81':
                        return (False, "Delivery failed." + reason_string(buf))
                    dq.popleft()

        return True, ""

    def delete_account(self, username):
        '''
        Deletes an account from the server's database. Deletion fails if
        the username does not exist, or if there are messages still pending
        to that user.

        :param username: the username of the account to be deleted.

        :return: tuple of (boolean, String).
                 Returns (True, "") if the request succeeds, and
                 (False, failure-reason) if the request fails.
        '''
        logging.info("waiting to obtain accountList")
        with self.lock:
            if username not in self.accounts:
                return (False, "username does not exist.")
            logging.info("Waiting to obtain pending info list")
            with self.__pending_messages[username][0]:
                if len(self.__pending_messages[username][1]):
                    mes = ("Messages still pending delivery to %s. "
                           "Cannot delete account until user logs in." %
                           username)
                    return (False, mes)
                self.accounts.remove(username)
                del self.__pending_messages[username]
                return (True, "")

    def account_exists(self, username):
        '''
        Checks if a given account exists in the server's database.

        :param username: username to check for.
        :return: boolean indicating existence of account.
        '''
        logging.info("waiting to obtain accountList")
        with self.lock:
            if username in self.accounts:
                return True
            return False

    def list_accounts(self):
        '''
        Returns a comma-separated string of all accounts that exist
        on the server.

        :return: comma separated string of all accounts that exist on the
        server.
        '''
        logging.info("waiting to obtain accountlist")
        with self.lock:
            if not len(self.accounts):
                return "No accounts exist!"
            return ', '.join(str(e) for e in self.accounts)

    def list_accounts_with_regex(self, regex):
        '''
        Returns a comma-separated string of all accounts that exist
        on the server that contain a string matching the
        provided regex sequence.

        :param regex: string containing the regex sequence that each account
        returned should contin a match for.

        :return: comma separated string of all accounts that exist on the
        server that contain a substring that matches the given regex string.
        '''
        logging.info("waiting to obtain accountlist")
        with self.lock:
            accs = [acc for acc in self.accounts if re.search(regex, acc)]
            if not len(accs):
                return "No matching accounts exist!"
            return ', '.join(str(e) for e in accs)


def send_or_queue_message(accounts, active_clients, receiving_user,
                          packed_message):
    '''
    References server database and active clients registry in order to
    determine whether a message should be immediately delivered (if the
    receipient is currently logged in and online) or queued for delivery
    (if the recepient is not online).

    :param active_clients: ActiveClients object that represents
    server's current connection with clients.
    :param accounts: AccountList object that represents server account
    database.
    :param receiving_user: the username of the recepient user.
    :param packed_message: The message that should be sent to the recepient.
        packed_message is a message of bytes packed using struct.pack,
        packed according to the specifications for the DELIVER_MESSAGE_REQUEST
        of a protocol version that the receiving user can understand.
    '''
    # check if receiving user exists
    if not accounts.account_exists(receiving_user):
        return (False, "Account %s does not exist." % receiving_user)

    # If the receiving user is currently logged in,
    # send the message immediately.
    # Otherwise, queue it for delivery.
    if active_clients.is_active(receiving_user):
        lock, sock = active_clients.sockets[receiving_user]
        print "Waiting to obtain lock for %s's socket" % receiving_user
        try:
            print "waiting on lock"
            with lock:
                sock.send(packed_message)
            return (True, "")
        except Exception as e:
            # queue message for delivery if connection is down
            print e
            print "ERROR: connection down, queeing message for delivery instead"
    return accounts.add_pending_message(receiving_user, packed_message)
