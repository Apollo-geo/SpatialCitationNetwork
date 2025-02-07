from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['LiteratureNetwork']
references_collection = db['Papers']

# Aggregation operation, delete the records with duplicate Title and keep only one
pipeline = [
    {
        "$group": {
            "_id": "$Title",
            "doc_ids": {"$push": "$_id"},
            "count": {"$sum": 1}
        }
    },
    {
        "$match": {
            "count": {"$gt": 1}
        }
    }
]

# Perform aggregation operations
cursor = references_collection.aggregate(pipeline)

# Delete duplicate records
for doc in cursor:
    doc_ids_to_delete = doc['doc_ids'][1:]
    references_collection.delete_many({"_id": {"$in": doc_ids_to_delete}})

print("Duplicate PaperTitles removed.")
