from myServerSend import general_failure, end_session_success, create_success
from myServerSend import delete_success, deposit_success, withdraw_success
from myServerSend import balance_success
from struct import unpack
import sys

# create new account
def create_request(conn, netBuffer, lock, accounts, active_clients):
    values = unpack('!I', netBuffer[6:14])

    lock.acquire()
    accounts.add_account(values[0])
    # try:
    #     # get balance
    #     if(values[0] >= 0 and values[0] < sys.maxint):
    #         bal = values[0]
    #     else:
    #         general_failure(conn, 'create', "invalid balance")
    #         return

    #     # get account number
    #     if values[1] > 0 and values[1] <= 100:
    #         act = values[1]
    #         if act in myData:
    #             general_failure(conn, 'create', "account already in use")
    #             return

    #     # generate a value if it was -1
    #     elif values[1] == -1:
    #         i = 1
    #         while i in myData:
    #             i += 1
    #             if i == 101:
    #                 general_failure(conn, 'create', "no remaining accounts")
    #                 return
    #         act = i
    #     else:
    #         general_failure(conn, 'create', "invalid account number")
    #         return

    #     myData[act] = bal
    #     create_success(conn, act)
    finally:
        lock.release()
        print accounts

    return
