# Import socket module
import sys
import config
import socket
import clientSend
from clientReceive import * 

current_user = None

version = '\x01'

#opcode associations; note that these opcodes will be returned by the server
opcodes = {'\x11': create_success,
           '\x12': create_failure,  
           # '\x21': delete_success,
           # '\x22': general_failure,
           # '\x31': deposit_success,
           # '\x32': general_failure,
           # '\x41': withdraw_success,
           # '\x42': general_failure,
           # '\x51': balance_success,
           # '\x52': general_failure,
           # '\x61': end_session_success,
           # '\x62': unknown_opcode
           }


def getStartupInput():
    print '''
WELCOME - type the number of a function:
    (1) Create Account
    (2) Log In
    '''
    startupInput = raw_input('>> ')
    return startupInput

def getSessionInput():
    print '''
YOU ARE LOGGED IN! - type the number of a function:
    (1) Send a message 
    (2) List all accounts 
    (3) Delete your account
    '''
    sessionInput = raw_input('>> ')
    return sessionInput 


def processInput(requestNumber):
    # create
    if requestNumber == str(1):
        clientSend.create_request(sock)

    # delete
    elif requestNumber == str(2):
        clientSend.login_request(sock)


    return

def getResponse():
    #wait for server responses...
    while True:
        try:
            retBuffer = sock.recv( 1024 )
        except:
            #close the client if the connection is down
            print "ERROR: connection down"
            sys.exit()
            
        if len(retBuffer) != 0:
            header = unpack(config.pack_header_fmt, retBuffer[0:6])
            #only allow correct version numbers
            if header[0] == version:
                opcode = header[2]
                #send packet to correct handler
                try:
                    success = opcodes[opcode](sock,retBuffer)
                except KeyError:
                    break
                if success == True: 
                    return True 
                else:
                    return False 
            else:
                return 
        return 

if __name__ == '__main__':

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(('127.0.0.1', config.port))
    except:
        print "ERROR: could not connect to port: " + config.port
        sys.exit()

    while True:
        startupInput = getStartupInput()
        processInput(startupInput) 
        success = getResponse() 
        if success == True: 
            break 

    while True:
        sessionInput = getSessionInput() 
        getResponse()

    # mySocket.close()
