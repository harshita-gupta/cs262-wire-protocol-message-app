import thread

# Define the port on which you want to connect
port = 12345




def send_message(message, conn):
    try:
        conn.send(message)
    except:
        # close the client if the connection is down
        print "ERROR: connection down"
        thread.exit()
    return
