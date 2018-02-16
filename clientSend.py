import config 
from config import send_message
from struct import pack
from sys import maxint, exit


# create new account
def create_request(conn):

    print "CREATING AN ACCOUNT \n"
    print "enter a username of alphanumeric characters under 20 characters:"
    while True:
        userInput = raw_input('>> ')
        if(userInput.isalnum() and len(userInput) <= 5):
            username = userInput
            break

    send_message('\x01' + pack('!I', 5) + '\x10' + pack(config.username_fmt, username), conn)

    return

# log in to an existing account
def login_request(conn):

    print "LOGGING IN \n"
    print "Enter your username"
    while True:
        userInput = raw_input('>> ')
        if(userInput.isalnum() and len(userInput) <= 5):
            username = userInput
            break

    send_message('\x01' + pack('!I', 5) + '\x20' + pack(config.username_fmt, username), conn)

    return

# log out 
def logout_request(conn, username):
    print "LOGGING OUT \n"
    send_message('\x01' + pack('!I', 5) + '\x60' + pack(config.username_fmt, username), conn)

    return

# #deposit to an existing account
# def deposit_request(conn):
#     print "DEPOSITING SOME DOUGH \n"
#     print "enter a an account number 1-100:"
#     while True:
#         try:
#             netBuffer = int(raw_input('>> '))
#         except ValueError:
#             continue

#         if(netBuffer > 0 and netBuffer <= 100):
#             act = netBuffer
#             break
#     print "enter an amount to deposit:"
#     while True:
#         try:
#             netBuffer = int(raw_input('>> '))
#         except ValueError:
#             continue
#         if(netBuffer >= 0 and netBuffer < maxint):
#             bal = netBuffer
#             break

#     send_message('\x01' + pack('!I',8) + '\x30' + pack('!II',act,bal),conn)
#     return

# #withdraw from an existing account
# def withdraw_request(conn):
#     print "WITHDRAWING SOME DOUGH \n"
#     print "enter a an account number 1-100:"
#     while True:
#         try:
#             netBuffer = int(raw_input('>> '))
#         except ValueError:
#             continue

#         if(netBuffer > 0 and netBuffer <= 100):
#             act = netBuffer
#             break

#     print "enter an amount to withdraw:"
#     while True:
#         try:
#             netBuffer = int(raw_input('>> '))
#         except ValueError:
#             continue
#         if(netBuffer >= 0 and netBuffer < maxint):
#             bal = netBuffer
#             break

#     send_message('\x01' + pack('!I',8) + '\x40' + pack('!II',act,bal),conn)
#     return


# #withdraw from an existing account
# def balance_request(conn):
#     print "CHECKING THE BALANCE OF AN ACCOUNT \n"
#     print "enter a an account number 1-100:"
#     while True:
#         try:
#             netBuffer = int(raw_input('>> '))
#         except ValueError:
#             continue

#         if(netBuffer > 0 and netBuffer <= 100):
#             act = netBuffer
#             break

#     send_message('\x01' + pack('!I',4) + '\x50' + pack('!I',act),conn)
#     return

# #end a session
# def end_session(conn):
#     send_message('\x01\x00\x00\x00\x00\x60',conn)
#     return

# def send_message(message, conn):
#     try:
#         conn.send(message)
#     except:
#             #close the client if the connection is down
#             print "ERROR: connection down"
#             exit()
#     return

