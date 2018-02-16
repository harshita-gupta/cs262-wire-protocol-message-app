import config
from struct import unpack

<<<<<<< HEAD

# added the below functions as skeleton code mostly so that we could
# nicely link to them in the dict of opcodes,
# they might just end up being wrappers for calls to the state methods,
# however.


# create new account
def create_request(conn, netBuffer, lock, accounts, active_clients):
    values = unpack('!I', netBuffer[6:14])

    lock.acquire()
    accounts.add_account(values[0])
    # try:
    #     # get balance
    #     if(values[0] >= 0 and values[0] < sys.maxint):
    #         bal = values[0]
    #     else:
    #         general_failure(conn, 'create', "invalid balance")
    #         return

    #     # get account number
    #     if values[1] > 0 and values[1] <= 100:
    #         act = values[1]
    #         if act in myData:
    #             general_failure(conn, 'create', "account already in use")
    #             return

    #     # generate a value if it was -1
    #     elif values[1] == -1:
    #         i = 1
    #         while i in myData:
    #             i += 1
    #             if i == 101:
    #                 general_failure(conn, 'create', "no remaining accounts")
    #                 return
    #         act = i
    #     else:
    #         general_failure(conn, 'create', "invalid account number")
    #         return

    #     myData[act] = bal
    #     create_success(conn, act)
    lock.release()
    print(accounts.show_accounts())

    return

=======
# CREATE REQUEST
>>>>>>> d3272c825b3397ff111bffd562dd8daf241c663d

def send_create_success(username):

    return None


def send_create_failure(username, reason):
    return None


def create_request(connection, buf, lock, accounts, active_clients, pack_fmt):
    values = unpack(pack_fmt, buf[6:14])

    lock.acquire()
    accounts.add_account(values[0])

    return None


# DELETE REQUEST

def send_delete_success(username):
    return None


def send_delete_failure(username, reason):
    return None


def delete_request(connection, buf, lock, accounts, active_clients, pack_fmt):
    return None


# SEND MESSAGE REQUEST


def send_message_failure(reason):
    return None


def send_message_success():
    return None


def send_message_request(connection,
                         buf, lock, accounts, active_clients, pack_fmt):
    return None


# LIST USERS FUNCTIONS

def send_list_users():
    return None


def list_users_request(connection,
                       buf, lock, accounts, active_clients, pack_fmt):
    return None


# LOG OUT FUNCTIONS

def log_out_success(connection):
    return None


def log_out(connection, buf, lock, accounts, active_clients, pack_fmt):
    return None


# LOG IN FUNCTIONS

def log_in_request(connection, buf, lock, accounts, active_clients, pack_fmt):
    return None


# Operation codes that can be received and processed by the server.
opcodes = {'\x10': create_request,
           '\x20': delete_request,
           '\x30': send_message_request,
           '\x50': list_users_request,
           '\x60': log_out,
           '\x70': log_in_request
           }
