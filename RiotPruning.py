from pymongo import MongoClient

#Only to be run to remove duplicates

client = MongoClient('localhost', 27017)
db = client.lol_database
collection = db.preseason_2018
collection.aggregate(
    [
        { "$sort": { "_id": 1 } },
        { "$group": { "_id": "$gameId", "doc": { "$first": "$$ROOT" }}},
        #{ "$group": { "_id": "$status", "doc": { "$first": "$$ROOT" }}},
        { "$replaceRoot": { "newRoot": "$doc" }},
        { "$out": "test_collection" }
    ],
    allowDiskUse = True
)