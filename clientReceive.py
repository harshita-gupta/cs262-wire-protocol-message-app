from struct import unpack
from sys import exit

#create new account
def create_success(conn, netBuffer):
    print "Account creation successful"
    return

def create_failure(conn, netBuffer):
    print "Account creation failure--username already exists"
    return