This is our client-server wire protocol assignment.
All connections are on port 12345.

SECTION 1. RUNNING SERVER AND CLIENT 
1) To run, open a terminal and run python server.py.
2) Open a second terminal and run python client.py.
3) When prompted for IP in client.py, enter the public IP of the computer running server.py or 127.0.0.1 if running the two server and client processes on the same computer. 

SECTION 2. USING THE CHAT INTERFACE 
You will now see the prompt "WELCOME - type the number of a function:"
1) To test the create account function, type 1 into the terminal and press enter. Your username must be an alphanumeric string that is EXACTLY 5 characters long. Otherwise, you will be re-prompted for a new input. Input a legal username and press enter. After creating an account, you will automatically be logged in. You will see the "YOU ARE LOGGED IN! - type the number of a function:" prompt 
Note: the following steps can only be executed after you have logged in 
2) You can only delete your OWN account if you are logged in. To delete your account, type in 3 and press enter. You will see the message "Successfully deleted account" and it will bring you back to the "WELCOME - type the number of a function:" page from step 1 of this section. 
3) While you are logged in, you can also list all accounts on the server by typing 4 and pressing enter. You will see the message "Accounts: x, y, z" where x, y, z are usernames or you will see "Accounts: No accounts exist!" if there are no accounts on the server. You will then be re-prompted to input the number of another function from the "YOU ARE LOGGED IN!" page. 
4) While you are logged in, you can also log out. To log out, type 6 and press enter. You will see the message "Successfully logged out" and be re-directed back to the "WELCOME" page of step 1 of this section. You MUST log out every time you want to end a client process before you "ctrl+c" -- if you don't, the user will remain logged in and will not be able to log back in on another client process! 
Note: the following steps can only be executed when you are NOT logged in 
5) If you are logged in, log out. We have already covered (1) Create account. Now, the second thing you can do is log in. Do this by typing 2 and pressing enter. You will be prompted to "Enter your username." If you do not enter an existing username, you will get a message that says "Login failure, [reason]" and be redirected to the "WELCOME" page. Try logging in by using an existing username. You will then be directed to the "YOU ARE LOGGED IN!" page 
6) Log back out if you are logged in. The third thing you can do from the "WELCOME" page is deleting ANY account on the server. To do this, type 3 and press enter. If you enter a username that does not exist, you will receive a message saying "Cannot delete account" and be re-directed to the "WELCOME" page. If you enter an existing username, the account will be deleted from the server and you will see a "Successfully deleted account" message and be redirected to the "WELCOME" page. 
7) The last thing you can do from the "WELCOME" page is listing all accounts. This is the same as step 3 of this section. Type 4 and press enter. Refer to step 3 of this section for what you are supposed to see. 
