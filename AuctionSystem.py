#AuctionSystem.py
#####  Stratagem Exercise ####
#####  Author: Enrico D'Urso
##############################


#####  Import modules #####
import select
import socket
import sys
import Queue
import json
from socket import error as SocketError
import errno
import re
import math


###    The followings are my external modules ###
import BidTrackerAndItem
from RegUser import RegUser
from RegUser import isValidUser

# code Action, each received message should have
# an Action field
##################
REGISTRATION_REQUEST = 0
BID_FOR_ITEM = 1
LIST_ITEM_FOR_USER = 2
WINNING_BID = 3
GET_ALL_BIDS_FOR_ITEM = 4
##################



def processUserKeyboardInput( userInputKeyboard, userTable, bidTracker ) :
    #userInputKeyboard can be:
    # ShowUserTable --> Asking for showing user table
    # ShowBid ITEM  --> show all bid for ITEM
    # ShowBidFor USERID    --> Get all the items on which a user has bid
    command = userInputKeyboard
    stringToReturn = " Result for command: " + command  + "\n"
    #Deleting useless spaces
    commandParsed = re.sub("\s\s+", " ", command)
    commandArray = commandParsed.split()
    realCommand = commandArray[0].lower()
    if len(commandArray) > 1 :
       optionalArgument = commandParsed.split()[1]
    else :
       optionalArgument = ""

    if realCommand == "showusertable" :
       usersString = ', '.join("%s" % (item) for (item) in userTable.keys() )
       stringToReturn += usersString

    elif realCommand == "showbid" :
       item = optionalArgument
       bidForItemTuple = bidTracker.getAllBidsForItem(item)
       exitValue = bidForItemTuple[0]
       if exitValue == -1 :
          itemList = bidTracker.getListItem()
          stringToReturn = stringToReturn + "item: " + item + " does not exist" + ",  here the item List \n***"
          stringToReturn += itemList + "***\n"
       else :
          bidList = bidForItemTuple[1]
          bidString = ', '.join("%s" % (bid) for (bid) in bidList )
          stringToReturn += bidString

    elif realCommand == "showbidfor" :
        userID = optionalArgument
        try:
            userID = int(userID)
        except ValueError:
            userID = -1
            print 'Please enter an integer'
        res = regUsersDict.get(userID, None)
        if res is not None :
           listItemUser = bidTracker.getUserItem(userID)
           stringBidUser =  ', '.join("%s" % (bid) for (bid) in listItemUser )
           stringToReturn += stringBidUser
        else :
           stringToReturn += "user " + optionalArgument + " does not exist"
    elif realCommand == "close" :
        stringToReturn = "close"

    else :
        stringToReturn += " bad command "
    return stringToReturn

# @param message_as_a_dict the message just received
# @param regUsersDict is a dict which contains registered users
# @param bidTracker is the concrete bidTracker object instance
# @return a tuple like this: (ExitValue, [messageToSendBack])
#      please note that messageToSend back does exists if and only if ExitValue is != -1
#      -1 is error
def dispatch(message_as_a_dict, regUsersDict, bidTracker):

    #If you do not like global variable, just wrap currentID in a object and
    # then pass it to this function
    global currentID

    #Getting action, that is the main field, to understand
    #which action we need to do
    action = message_as_a_dict.get('Action', -1)

    #For a full explanation of action, please refer to the documentation,here a brief explanation
    #action  REGISTRATION_REQUEST --> Asking for registration, therefore passwd field must exist
    #action  BID_FOR_ITEM --> Bid for a item, therefore item field must exist
    #action  LIST_ITEM_FOR_USER --> Get the current winning bid for an item, therefore item must exist
    #action  WINNING_BID --> Get Winning bid

    toReturn = (-1,) #Default, bad message

    # Registration
    # Precondition for the correct message for a registration request:
    # message_as_a_dict must be like this: { 'action' : REGISTRATION_REQUEST, 'passwd' : "anypasswd" }
    if action == REGISTRATION_REQUEST :
       passwd = message_as_a_dict.get('passwd')
       if passwd is None :
          toReturn = (-1, )
       else : #Creating new user instance
          reg = RegUser(currentID, passwd)
          regUsersDict[currentID] = reg
          #Creating packet to send back to the user
          message = {'Action': REGISTRATION_REQUEST, 'passwd': passwd, 'id': currentID }

          #Please note that I can safe increment currentID because of single-thread design
          currentID += 1
          toReturn = (0, message)

    #BidForAnItem
    elif action == BID_FOR_ITEM :
       print("BID FOR ITEM ")
       userID = message_as_a_dict.get('id')
       passwd = message_as_a_dict.get('passwd')
       bid = message_as_a_dict.get('bid')

       try:
           bid = float(bid)
           if bid <= 0 or math.isinf(bid) or math.isnan(bid): #If here no exception, check if greater than 0, inf and NaN
              bid = None
              print("bid not valid ")
       except Exception: #Bid is not a valid float
           bid = None
           print("bid not valid")

       item = message_as_a_dict.get('item')
       res = isValidUser(userID, passwd, regUsersDict)
       # User does exist, let's go to bid!!
       if res == True and bid is not None and item is not None :
          insertOk = bidTracker.recordUserBid(userID, bid, item)
          if insertOk:
             message = {'Action': BID_FOR_ITEM, 'res': 0, 'error' : "" }
             toReturn = (0, message)
          else :
             itemList = bidTracker.getListItem()
             message = {'Action' : BID_FOR_ITEM, 'res' : -1, 'error' : "itemDoesNotExist", 'itemList' : itemList}
             toReturn = (0, message)
       else : #User does not exist
          toReturn = (-1, )

    #LIST_ITEM_FOR_USER
    elif action == LIST_ITEM_FOR_USER :
       print('LIST_ITEM_FOR_USER')
       userID = message_as_a_dict.get('id')
       passwd = message_as_a_dict.get('passwd')
       res = isValidUser(userID, passwd, regUsersDict)
       if res:
          listItemUser = bidTracker.getUserItem(userID)
          message = {'Action' : LIST_ITEM_FOR_USER, 'itemListForUser' : listItemUser}
          toReturn = (0, message)
       else : #User does not exist
          toReturn = (-1, )

    #WINNING_BID
    elif action == WINNING_BID :
       print('WINNING_BID')
       userID = message_as_a_dict.get('id')
       passwd = message_as_a_dict.get('passwd')
       item = message_as_a_dict.get('item')
       res = isValidUser(userID, passwd, regUsersDict)
       if res == True and item is not None :
          winningBid = bidTracker.currentWinningBidForItem(item)
          if winningBid == -2 :
             itemList = bidTracker.getListItem()
             message = {'Action' : WINNING_BID, 'res' : -1, 'error' : "itemDoesNotExist", 'itemList' : itemList}
             toReturn = (0, message)
          else :
             message = {'Action' : WINNING_BID, 'winningBid' : winningBid}
             toReturn = (0, message)
       else : #user does not exist
          toReturn = (-1, )

    #GET_ALL_BID_FOR_ITEM
    elif action == GET_ALL_BIDS_FOR_ITEM :
       print('GET_ALL_BIDS_FOR_ITEM')
       userID = message_as_a_dict.get('id')
       passwd = message_as_a_dict.get('passwd')
       item = message_as_a_dict.get('item')
       res = isValidUser(userID, passwd, regUsersDict)
       if res == True and item is not None:
          bidForItemTuple = bidTracker.getAllBidsForItem(item)
          exitValue = bidForItemTuple[0]
          if exitValue == -1 :
             itemList = bidTracker.getListItem()
             message = {'Action' : GET_ALL_BIDS_FOR_ITEM, 'res' : -1, 'error' : "itemDoesNotExist", 'itemList' : itemList}
             toReturn = (0, message)
          else :
             bidList = bidForItemTuple[1]
             message = {'Action' : GET_ALL_BIDS_FOR_ITEM, 'bidList' : bidList}
             toReturn = (0, message)
       else :
           toReturn = (-1 , )

    return toReturn


#Using the following syntax avoids that this script run if imported
if __name__ == '__main__':

    PORT_TO_BIND = 10000
    # Create a TCP/IP socket
    # Internet Protocol v4 addresses
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(0)
    currentID = 0

    #Listing items on which user can bind
    listItems = ['Python-Book', 'MachineLearningBook', 'Spark-Book', 'TCP-IP-BOOK', 'StrataBet', 'RyanairTicketForLondon'];

    #Creating Object from string, I like lambda expression, I've been frequently using that in Scala language
    listItemsObj = map(lambda itemString: BidTrackerAndItem.Item(itemString) , listItems)

    #Creating bidTracker Object
    bidTracker = BidTrackerAndItem.BidTracker(listItemsObj)

    # This is a registrationTable, currently implemented as a dict,
    # Please avoid this kind of stuff in production, i.e.: Use a Database
    regUsersDict = {}

    # Bind the socket to the port
    server_address = ('0.0.0.0', PORT_TO_BIND)
    print >>sys.stderr, 'starting up on %s port %s' % server_address
    server.bind(server_address)

    # Listen for incoming connections
    server.listen(5)

    # Sockets from which we expect to read
    inputs = [ server, sys.stdin ]

    # Sockets to which we expect to write
    outputs = [ ]

    #Client address dict
    clientAddressDict = {}

    # Outgoing message queues (socket:Queue)
    message_queues = {}
    maxTogether = 0
    #Start Main Loop
    while inputs:

        # Wait for at least one of the sockets to be ready for processing
        print >>sys.stderr, '\nwaiting for the next event'
        print "#Connected Clients: " + str(len(inputs) - 2 )
        print "#Record Connected Clients " + str(maxTogether)

        if maxTogether < len(inputs) - 2 :
           maxTogether = len(inputs) - 2

        readable, writable, exceptional = select.select(inputs, outputs, inputs)
        # Handle inputs
        for s in readable:

            if s is server:
                # A "readable" server socket is ready to accept a connection
                connection, client_address = s.accept()

                print >>sys.stderr, 'new connection from', client_address

                connection.setblocking(0)
                # appending this socket in the input list
                inputs.append(connection)

                #Setting this client_address in the ClientAddress Dict
                clientAddressDict[connection] = client_address
                # Give the connection a queue for data we want to send
                message_queues[connection] = Queue.Queue()

            elif s == sys.stdin:
                # handle standard input
                userInputKeyboard = sys.stdin.readline()
                if userInputKeyboard != "\n" :
                   print("USER INPUT KEYBOARD " + userInputKeyboard)
                   toPrint = processUserKeyboardInput( userInputKeyboard, regUsersDict, bidTracker)

                   if toPrint == 'close' :
                      for x in readable :
                          x.close()
                      for y in writable :
                          y.close()
                      sys.exit(0)

                   print toPrint

            #Checking for data from network, please note that if connection has been closed, then data is empty.
            #This is standard for TCP connection
            else:
                #Getting data from socket
                #Please, assume here that we receive the whole packet without checking it out
                try :
                    data = s.recv(8192)

                except SocketError as e :
                    if e.errno != errno.ECONNRESET :
                       raise
                    #Interpret error as data empty
                    data = ''

                print data

                # If data is not empty then something has really been received
                if data:
                    #Deserialization
                    try :
                        message_as_a_dict = json.loads(data) #data loaded
                    except ValueError :
                        #Bad message, turn it in empty Dict
                        message_as_a_dict = {}

                    #calling dispatch and getting result
                    result = dispatch(message_as_a_dict, regUsersDict, bidTracker)
                    exit_value = result[0]

                    # -1 means error, Just close the connection in this trivial demo
                    if exit_value == -1 :
                       if s in outputs:
                          outputs.remove(s)
                          message_queues.pop(s, "None")
                       inputs.remove(s)
                       print "closing socket "
                       s.close()

                    else :
                        print >>sys.stderr, 'received "%s" from %s' % (data, s.getpeername())
                        message_queues[s].put(result[1])
                        # Add output channel for response
                        if s not in outputs:
                            outputs.append(s)
                else:
                    # Interpret empty result as closed connection
                    client_address = clientAddressDict[s]
                    del clientAddressDict[s]
                    print >>sys.stderr, 'closing', client_address, 'after reading no data'
                    # Stop listening for outputs on the connection
                    if s in outputs:
                       outputs.remove(s)
                       message_queues.pop(s, "None")
                    inputs.remove(s)
                    s.close()

        # Handle outputs
        for s in writable:
            try:
                next_msg = message_queues[s].get_nowait()
            except (Queue.Empty, KeyError):
                # No messages waiting so stop checking for writability if not already done.
                if s in outputs:
                   outputs.remove(s)
            else:
                print >>sys.stderr, 'sending "%s" to %s' % (next_msg, s.getpeername())
                data_string = json.dumps(next_msg)
                try :
                    s.send(data_string)
                except SocketError as e :
                       print e

        # Handle "exceptional conditions"
        for s in exceptional:
            print >>sys.stderr, 'handling exceptional condition for', s.getpeername()
            # Stop listening for input on the connection
            inputs.remove(s)
            if s in outputs:
                outputs.remove(s)
            s.close()

            # Remove message queue
            del message_queues[s]

