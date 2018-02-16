from struct import unpack
from sys import exit

#create new account
def create_success(conn, netBuffer):
    values = unpack('!I',netBuffer[6:10])
    print "Account creation successful " + str(values[0])
    return

def create_failure(conn, netBuffer):
    values = unpack('!I',netBuffer[6:10])
    print "Account creation failure " + str(values[0])
    return