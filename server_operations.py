import config
from struct import unpack

# CREATE REQUEST

def send_create_success(username):

    return None


def send_create_failure(username, reason):
    return None


def create_request(connection, buf, lock, accounts, active_clients, pack_fmt):
    values = unpack(pack_fmt, buf[6:14])

    lock.acquire()
    accounts.add_account(values[0])

    print(accounts.list_accounts())

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
