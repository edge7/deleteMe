import unittest
import BidTrackerAndItem
import random

class BidTrackerTestClass(unittest.TestCase):
    def setUp(self):

        #Listing items on which user can bind
        listItems = ['Python-Book', 'MachineLearningBook', 'Spark-Book', 'TCP-IP-BOOK', 'StrataBet', 'RyanairTicketForLondon']

        #Creating Object from string, I like lamda expression, I've been frequently using that in Scala language
        listItemsObj = map(lambda itemString: BidTrackerAndItem.Item(itemString) , listItems)

        #Creating bidTracker Object
        bidTracker = BidTrackerAndItem.BidTracker(listItemsObj)
        self.bidTracker = bidTracker

    def testAContructor(self):
        # Correct List
        listItemsOK = ['Python-Book', 'MachineLearningBook', 'Spark-Book', 'TCP-IP-BOOK', 'StrataBet', 'RyanairTicketForLondon']
        # Bad List
        listItemsKO = ['Python-Book', 'MachineLearningBook', 'TCP-IP-BOOK', 'StrataBet', 'RyanairTicketForLondon']
        # Ignore case
        listItemsOK = map(lambda x: x.lower(), listItemsOK )
        listItemsKO = map(lambda x: x.lower(), listItemsKO )

        #Get item list from object in testing
        listItemsToCheck = self.bidTracker.getItemsAsList()
        listItemsToCheck = map( lambda x: x.lower(), listItemsToCheck )

        self.assertTrue(sorted( listItemsOK) == sorted( listItemsToCheck), 'Incorrect Constructor')
        self.assertFalse(sorted ( listItemsToCheck ) == sorted( listItemsKO) , 'Incorrect Constructor')

    def testBGetHighestBid(self):

        listItemsOK = ['Python-Book', 'MachineLearningBook', 'Spark-Book', 'TCP-IP-BOOK', 'StrataBet', 'RyanairTicketForLondon']

        #Checking that if nobody has bid then highest bid is 0
        for i in listItemsOK :
            maxBedToCheck = self.bidTracker.currentWinningBidForItem(i)
            self.assertEquals( maxBedToCheck, 0, "Default bid is not 0 ")

        #Checking that the highest bid is being stored
        itemOK = 'Python-Book'
        #Random userID
        userIDRandom = [random.randrange(0, 100, 1) for _ in range (100)]
        #Random float bed
        randomBed = [random.uniform(0.1, 1000.0) for _ in range (100)]
        currentMax = -1
        #Not every randomBed will be using, getting the max of the ones that will be
        #The following code could be less clear, but I've been starting to like
        # the way :'less code, the better'.
        #It is the same as:
        # tmpList = []
        # for i in userIDRandom
        #     tmpList.insert(0, randomBed[i])
        # maxBed = max(tmpList)
        #
        maxBed = max( map(randomBed.__getitem__, userIDRandom) )

        for i in userIDRandom :
            # Using i as randomBed index and userID
            self.bidTracker.recordUserBid(i, randomBed[i], itemOK)
            maxBedToCheck = self.bidTracker.currentWinningBidForItem(itemOK)
            #Continuosly updating the currentMax for inline check
            if randomBed[i] > currentMax :
               currentMax = randomBed[i]
            #Check
            self.assertEquals(maxBedToCheck, currentMax, ' max bed error ')

        #Check again, there is no need, though
        self.assertEquals(maxBedToCheck, maxBed, ' max bed error ')

        #Checking that if item does not exist then result is -2
        listItemsKO = ['None of', 'these items', 'do actually', 'exist', 'therefore', 'result', 'must be', ' -2 ']
        for i in listItemsKO :
            result = self.bidTracker.currentWinningBidForItem(i)
            self.assertEquals( result, -2, "Result is not -2 ")


    def testCGetAllBidsForItem(self):
        listItemsOK = ['MachineLearningBook', 'Spark-Book', 'TCP-IP-BOOK', 'StrataBet', 'RyanairTicketForLondon']
        listItemsKO = ['None of', 'these items', 'do actually', 'exist', 'therefore', 'result', 'must be', ' (-1,) ']
        dictItemsBid = {}
        for i in listItemsOK :
            dictItemsBid[i] = []
        #Random userID
        userIDRandom = [random.randrange(0, 100, 1) for _ in range (100)]
        #Random float bed
        randomBed = [random.uniform(0.1, 1000.0) for _ in range (100)]

        for i in listItemsOK :
            for userID in range(0, 2000) :
                bed = randomBed[random.randrange(0, 100, 1)]
                self.bidTracker.recordUserBid(userID, bed, i)
                dictItemsBid[i].insert(0, bed)

        for i in listItemsOK :
            self.assertEquals( self.bidTracker.getAllBidsForItem(i)[0] , 0 , "not the same ")
            self.assertEquals( sorted(self.bidTracker.getAllBidsForItem(i)[1] ), sorted(dictItemsBid[i]) , "not the same ")

        for i in listItemsKO :
            self.assertEquals( self.bidTracker.getAllBidsForItem(i) , (-1,) , "not the same ")

    # Testing: bidTracker.recordUserBid(userID, bid, item)
    def testDRecordUserBid(self):

        userID = 1
        itemOK = "Spark-Book"
        itemKO = "ITEM_DOES_NOT_EXIST"
        bid = 123.213
        returnValue = self.bidTracker.recordUserBid(userID, bid, itemOK)
        #Return Value should be True as itemOK does exist
        self.assertTrue(returnValue, ' returnValue is False even if with correct item ')
        #Return Value should be False as itemKO does not exist
        returnValue = self.bidTracker.recordUserBid(userID, bid, itemKO)
        self.assertFalse(returnValue, ' returnValue is True even if with bad item ')

        #Check if bid has been stored
        (errorCode, allBids) = self.bidTracker.getAllBidsForItem(itemOK)
        self.assertTrue( cmp( (errorCode, sorted(allBids)), (0, sorted( [bid] ) ) ) == 0, "DifferentTuple" )
        self.assertEquals( self.bidTracker.getUserItem(userID), [itemOK], "item has not been stored in user list")


    def testEGetUserItem(self):

        listItemsOK = ['Python-Book', 'MachineLearningBook', 'Spark-Book', 'TCP-IP-BOOK', 'StrataBet', 'RyanairTicketForLondon']
        bid = 123.213
        #Creating UserID
        userIDList = set([random.randrange(0, 50000, 1) for _ in range (40000)])
        #Dict like this: {userID: set([item1, item2..])} Itemi is generic item on which userID has bid
        userID_Items = {}
        for i in userIDList :
        	self.bidTracker.getUserItem(i)

        #for each User
        for i in userIDList :
        	#Create an empty set
        	userID_Items[i] = set()
        	#make 3 bids, to generate a list of item for userID in object
        	for j in range(0, 3) :
        		#Get items to bid on
        		whichItems = listItemsOK[ random.randrange(0, len(listItemsOK), 1) ]
        		self.bidTracker.recordUserBid(i, bid, whichItems)
        		#Register bid on my local data structure for later checking
        		userID_Items[i].add(whichItems)

        for i in userIDList:
        	self.assertEquals( sorted(userID_Items[i]), sorted(self.bidTracker.getUserItem(i))   )



if __name__ == '__main__':
    unittest.main()

