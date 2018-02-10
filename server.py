# first of all import the socket library
import socket
import config

# next create a socket object
s = socket.socket()
print "Socket successfully created"

# Next bind to the port
# we have not typed any ip in the ip field
# instead we have inputted an empty string
# this makes the server listen to requests
# coming from other computers on the network
s.bind(('', config.port))
print "socket binded to %s" % (config.port)

# put the socket into listening mode
s.listen(5)
print "socket is listening"

# a forever loop until we interrupt it or
# an error occurs
while True:

    # Establish connection with client.
    c, addr = s.accept()
    print 'Got connection from', addr

    # send a thank you message to the client.
    c.send('Thank you for connecting')

    # Close the connection with the client
    c.close()
