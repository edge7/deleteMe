
import abc

class Item(object):
      def __init__(self, itemString) :
          self.itemString = itemString
          self.userAndBidDict = {} #user: bid
          self.bedBest = 0

      def getCurrentWinningBid(self) :
          return self.bedBest

      def getAllBidsForItem(self) :
          return self.userAndBidDict.values()

      # @param userID the userID of the user who is bidding on the item
      # @param bid the bid for the item
      # @return None
      #
      # Explanation: I set bid as value for userAndBidDict[userID], so each user has en entry
      #              also, check if the currentBid is greater than the current highest (bidBest)
      #
      # A COUPLE OF WORDS ABOUT TIME COMPLEXITY :
      #
      #              Let us assume that the hash function for the dict is sufficiently robust to make collisions uncommon.
      #              self.userAndBidDict[userID] has O(1) time Complexity

      def recordUserBid(self, userID, bid) :
          self.userAndBidDict[userID] = bid
          if bid > self.bedBest :
             self.bedBest = bid

      # @param userID is the user id we want to check
      # @return True in case user has bid else False
      #
      #
      # A COUPLE OF WORDS ABOUT TIME COMPLEXITY :
      #
      #              Let us assume that the hash function for the dict is sufficiently robust to make collisions uncommon.
      #              self.userAndBidDict.get(userID) has O(1) time Complexity

      def hasUserBidOnItem(self, userID) :
          bid = self.userAndBidDict.get(userID)
          if bid is not None :
              return True
          else :
              return False


class BidTrackerInterface(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def recordUserBid(self, user, bid, item):
        """User bid on a item
        :param user:
        """
        return

    @abc.abstractmethod
    def currentWinningBidForItem(self, item ):
        """Get the current winning bid for an item"""
        return

    @abc.abstractmethod
    def getAllBidsForItem(self, item ):
        """Get all bids for an item"""
        return

    @abc.abstractmethod
    def getUserItem(self, user ):
        """Get all the items on which a user has bid"""
        return


class BidTracker(BidTrackerInterface):

    def __init__(self, listItemsObj):
        #initialize hash-table
        self.dictItemsObj = {} #{ ItemString : ItemObject }

        for k in listItemsObj :
            self.dictItemsObj[ k.itemString ] = k

    # @param userID the user id who is bidding (integer)
    # @param bid the user bid  (double)
    # @param item user is bidding on this item  (string)
    # @return false if item does not exist, else true
    #
    # EXPLANATION :
    #                we get the itemObject using item string as key
    #                since in this implementation user can try to bid on a item that does not exist
    #                we check that item really exists, if does
    #                we call recordUserBid method of Item class which finally records the bid
    # A COUPLE OF WORDS ABOUT TIME COMPLEXITY :
    #                Let us assume that the hash function for the dict is sufficiently robust to make collisions uncommon.
    #                self.dictItemsObj.get(item) has O(1) time Complexity
    #                recordUserBid has O(1) time Complexity as described above
    #                Therefore the overall complexity should be O(1)
    #
    #                If you want read more: https://wiki.python.org/moin/TimeComplexity

    def recordUserBid(self, userID, bid, item):
        itemObj = self.dictItemsObj.get(item)
        if itemObj is not None :
           itemObj.recordUserBid(userID, bid)
           return True
        return False

    # @param item the item (string) we want to get the highest bid
    # @return the currentWinningBid (note it can be -1, in case of no bid)
    #         return -2 if item is not
    # EXPLANATION :
    #                we get the itemObject using item string as key
    #                since in this implementation user can try to bid on a item that does not exist
    #                we check that item really exists, if it does
    #                we call getCurrentWinningBid on it
    #
    # A COUPLE OF WORDS ABOUT TIME COMPLEXITY :
    #
    #                Let us assume that the hash function for the dict is sufficiently robust to make collisions uncommon.
    #                self.dictItemsObj.get(item) has O(1) time Complexity
    #                getCurrentWinningBid is trivial function
    #                Therefore the overall complexity should be O(1)
    #
    #                If you want read more: https://wiki.python.org/moin/TimeComplexity
    def currentWinningBidForItem(self, item):
        itemObj = self.dictItemsObj.get(item)
        if itemObj is not None:
           currentWinningBid = itemObj.getCurrentWinningBid()
           return currentWinningBid
        return -2


    # @param item the item (string) we want to get bid list
    # @return a 1 or 2 elements tuple, tuple[0] is the error code: 0 no error, -1 error
    #         tuple[1] is bid list if there is no error, instead in case of error it does not even exist
    #         that means tuple is 1 element
    # EXPLANATION :
    #                we get the itemObject using item string as key
    #                since in this implementation users can try to bid on a item that does not exist
    #                we check that item really exists, if it does
    #                we call getAllBidsForItem
    # A COUPLE OF WORDS ABOUT TIME COMPLEXITY :
    #                Let us assume that the hash function for the dict is sufficiently robust to make collisions uncommon.
    #                self.dictItemsObj.get(item) has O(1) time Complexity
    #                itemObj.getAllBidsForItem() calls userAndBidDict.values() which should have O(N) time complexity
    #                Therefore the overall complexity should be O(N)
    #                O(N) means linear complexity, sometimes is ok sometimes is not acceptable,
    #                If it is not acceptable, we can create an additional list to keep track
    #                of all bids for a particular item, of couse doing that we need to use
    #                more memory, and we have an additional data-structure to preserve integrity.
    #                Trade-Off between memory complexity and time complexity is a well-known computer science problem.
    #                Without knowing the hardware-infrastracture and business requirements is hard saying which one is better.
    #
    #                If you want read more: https://wiki.python.org/moin/TimeComplexity
    def getAllBidsForItem(self, item ):
        itemObj = self.dictItemsObj.get(item)
        if itemObj is not None:
           allBids = itemObj.getAllBidsForItem()
           return (0, allBids)
        return (-1, )

    # @param user the user id  we want to get item list on which he/she has bid on
    # @return an item list which can be empty
    # EXPLANATION :
    #                we iterate on each item object stored on the bidTracker, for each of them
    #                 we call hasUserBidOnItem that verifies if the user has previously bid on that particular item
    #                 if user does the method returns true else false
    #                 in positive case we add that item (just the string) in a list, which will be returned
    # A COUPLE OF WORDS ABOUT TIME COMPLEXITY :
    #                Since we iterate on all items complexity is O(N), so it linearly scales with the number of item
    #                we can consider hasUserBidOnItem a O(1) function so the overall complexity is O(N)
    #                Actually, we can do better that that, creating an additional data-structure in which we store
    #                for each userId the item list on which he/she has bid on, something like:
    #                {userID: listItem}, but for this demo I avoided creating that
    #
    #                If you want read more: https://wiki.python.org/moin/TimeComplexity
    def getUserItem(self, user):
        itemForUser = []
        #Loop on self.dictItemsObj.values
        for itemObj in self.dictItemsObj.values() :
            hasUserBidOnItemBoolean =  itemObj.hasUserBidOnItem(user)
            if hasUserBidOnItemBoolean == True :
               itemForUser.insert(0, itemObj.itemString) #li.insert(0, a) is around 5x faster than li = [a] + l

        return itemForUser

    #Additional functions
    def getListItem(self):
        itemString = ' - '.join("%s" % (item) for (item) in self.dictItemsObj.keys() )
        return itemString

    #TestPurpose
    def getItemsAsList(self):
        return self.dictItemsObj.keys() # pragma: no cover