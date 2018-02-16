from struct import unpack
from sys import exit
from config import * 

#create new account
def create_success(conn, netBuffer):
  	values = unpack(username_fmt, netBuffer[6:14])
	current_user = values[0]
	print "Account creation successful"
	return True, current_user 

def create_failure(conn, netBuffer):
    print "Account creation failure--username already exists"
    return False, ""