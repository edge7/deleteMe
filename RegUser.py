class RegUser(object):

    #Please note I do know storing password in plainText is stupid as
    #studying Computer Engineering and do not work in London
    #MD5 + SALT is a solution
    #I will fix this when I am in London, I swear
    def __init__(self, ID, password):
        self.ID = ID
        self.password = password

    def getID(self):
        return self.ID

    def getPass(self):
        return self.password


# @param userID the user id to check
# @param passwd password to check
# @param regUserDict user table
# @return true if user does exist else false
def isValidUser(userID, passwd, regUsersDict):
    if userID is None or passwd is None :
       return False

    res = regUsersDict.get(userID, None)
    if res is not None :
       user = res.getID()
       pwd = res.getPass()
       if( str(user) == str(userID) and str(passwd) == str(pwd) ):
           return True
    print(" \n NOT VALID USER \n")
    return False