import threading
import logging
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

    def log_out(self, username):
        if not self.sockets.get(username):
            return (False, "Username not currently logged in")
        logging.info("Waiting to obtain lock for active socket conns dict.")
        with self.lock:
            logging.info("waiting to obtain lock for socket for %s", username)
            with self.sockets[username][0]:
                self.sockets[username][1].close()
                logging.info(
                    "Successfully closed connection with %s's socket",
                    username)
                self.sockets[username] = None
        return True

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
        return True


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
        return True

    def add_pending_message(self, sending_user, receiving_user, message):
        # list of accounts should not be modified while adding a message
        logging.info("waiting to obtain accountList")
        with self.lock:
            if sending_user not in self.accounts:
                return (False, "Sending user no longer exists")
            if receiving_user not in self.accounts:
                return (False, "Receiving user no longer exists")
            with self.__pending_messages[receiving_user][0]:
                self.__pending_messages[receiving_user].append(message)
        return True

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
                return True

    def list_accounts(self):
        logging.info("waiting to obtain accountlist")
        with self.lock:
            if not len(self.accounts):
                return "No accounts exist!"
            return ', '.join(str(e) for e in self.accounts)
