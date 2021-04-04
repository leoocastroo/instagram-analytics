import pymongo


class MongoConnector():

    def __init__(self):
        self.mongodb = pymongo.MongoClient("mongodb://localhost:27017/")

        self.instalytics = self.mongodb['instalytics']

    def insert_user(self, user):
        self.instalytics["users"].insert_one(user)

    def insert_users(self, users):
        self.instalytics["users"].insert_many(users)