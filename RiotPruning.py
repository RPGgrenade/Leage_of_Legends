from pymongo import MongoClient

#Only to be run to remove duplicates

client = MongoClient('localhost', 27017)
db = client.test_database
collection = db.test_collection
collection.aggregate(
    [
        { "$sort": { "_id": 1 } },
        { "$group": { "_id": "$gameId", "doc": { "$first": "$$ROOT" }}},
        { "$replaceRoot": { "newRoot": "$doc" }},
        { "$out": "test_collection" }
    ],
    allowDiskUse = True
)