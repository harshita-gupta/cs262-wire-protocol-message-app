import config
from struct import unpack, pack
from config import * 

# CREATE REQUEST

def send_create_success(connection, username):
  print"sending create success"
  print username 
  connection.send('\x01' + pack('!I',5) +'\x11' + pack(username_fmt, username))
  return


def send_create_failure(connection, username, reason):
  print"sending create failure"
  connection.send('\x01' + pack('!I',4) +'\x12')
  return None


def create_request(connection, buf, lock, accounts, active_clients, pack_fmt):
    values = unpack(pack_fmt, buf[6:14])
    username = values[0]
    lock.acquire()
    success = accounts.add_account(username) 
    if success == True:
      send_create_success(connection, username) 
    else:
      send_create_failure(connection, username, success[1])

    lock.release()
    return 


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
