import threading
import logging
import config
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
        @param urls list of urls to check
        @param output file to write urls output
        """
        self.lock = threading.Lock()

        # dictionary that stores username as keys and
        # (locks, socket objects) as values
        self.sockets = {}

    def is_active(self, username):
        with self.lock:
            if username in self.sockets:
                return True
            return False

    def log_out(self, username):
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

    def list_active_clients(self):
        with self.lock:
            return ', '.join(str(e) for e in self.sockets.keys())


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
        # TODO check that username is alphanumeric
        logging.info("Waiting to obtain accountList")
        with self.lock:
            if username in self.accounts:
                return (False, "Username already exists.")
            else:
                self.accounts.add(username)
                self.__pending_messages[username] = (threading.Lock,
                                                     deque())
        return (True, "")

    def add_pending_message(self, receiving_user, packed_message):
        # list of accounts should not be modified while adding a message
        logging.info("waiting to obtain accountList")
        with self.lock:
            if receiving_user not in self.accounts:
                return (False, "Receiving user no longer exists")
            with self.__pending_messages[receiving_user][0]:
                self.__pending_messages[receiving_user].append(packed_message)
        return (True, "")

    def deliver_pending_messages(self, receiving_username, lock, sock):
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
                    dq.popleft()

        # TODO this function should be called in server_operations log_in
        return None

    def delete_account(self, username, active_clients):
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
                self.__pending_messages.remove(username)
                return (True, "")

    def account_exists(self, username):
        logging.info("waiting to obtain accountList")
        with self.lock:
            if username in self.accounts:
                return True
            return False

    def list_accounts(self):
        logging.info("waiting to obtain accountlist")
        with self.lock:
            if not len(self.accounts):
                return "No accounts exist!"
            return ', '.join(str(e) for e in self.accounts)


def send_or_queue_message(accounts, active_clients, receiving_user,
                          packed_message):
    # If the receiving user is currently logged in,
    # send the message immediately.
    # Otherwise, queue it for delivery.
    if active_clients.is_active(receiving_user):
        lock, sock = active_clients.sockets[receiving_user]
        logging.info("Waiting to obtain lock for %s's socket" % receiving_user)
        with lock:
            config.send_message(packed_message, sock)
            # TODO check for send failure
        return (True, "")

    # receiving user is not logged in, queue for delivery
    if not accounts.account_exists(receiving_user):
        return (False, "Account %s does not exist." % receiving_user)

    accounts.add_pending_message(receiving_user, packed_message)
