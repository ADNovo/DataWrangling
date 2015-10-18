import pprint
from pymongo import MongoClient
    
#mongoimport --db osm --collection lasvegas --drop --file las_vegas_nevada.json   

client = MongoClient('localhost:27017')
collection = client.osm.lasvegas
#Get the number of documents in the collection
documents = collection.find().count()
print 'number of documents:', documents
#Get the number of 'node' and 'way' in the collection
cursor = collection.aggregate([{'$group': {'_id':'$type', 'count': {'$sum': 1}}}])
pprint.pprint([result for result in cursor])
#Get the number of unique users that contributed to the collection
cursor = collection.aggregate([{'$group': {'_id':'overall', 'unique_users': {'$addToSet': '$created.user'}}},
                              {'$project': {'number_unique_users': {'$size': '$unique_users'}}}])
pprint.pprint([result for result in cursor])
#Get the user with the higher contribution and his contribution (%)
cursor = collection.aggregate([{'$group': {'_id': '$created.user', 'documents_user': {'$sum': 1}}},
                              {'$project': {'user_name': '$created.user', 'percentage': {'$multiply': 
                                          [{"$divide": ['$documents_user', documents]}, 100]}}},
                              {'$sort': {'percentage': -1}},
                              {'$limit': 1}])
pprint.pprint([result for result in cursor])
#Get total contribution (%) of top 5 contributors
cursor = collection.aggregate([{'$group': {'_id': '$created.user', 'documents_user': {'$sum': 1}}},
                              {'$project': {'user_name': '$created.user', 'percentage': {'$multiply': 
                                          [{"$divide": ['$documents_user', documents]}, 100]}}},
                              {'$sort': {'percentage': -1}},
                              {'$limit': 5},
                              {'$group': {'_id': 'top 5', 'ratio': {'$sum': '$percentage'}}}])
pprint.pprint([result for result in cursor])
#Get total contribution (%) of top 10 contributors                           
cursor = collection.aggregate([{'$group': {'_id': '$created.user', 'documents_user': {'$sum': 1}}},
                              {'$project': {'user_name': '$created.user', 'percentage': {'$multiply': 
                                          [{"$divide": ['$documents_user', documents]}, 100]}}},
                              {'$sort': {'percentage': -1}},
                              {'$limit': 10},
                              {'$group': {'_id': 'top 10', 'ratio': {'$sum': '$percentage'}}}])
pprint.pprint([result for result in cursor])
#Get number of documents without address
no_address = collection.find({'address': {'$exists': 0}}).count()
print 'number of documents without address:', no_address
#Get number of documents per 'address.state' in descending order                             
cursor = collection.aggregate([{'$match': {'address.state': {'$exists': 1}}}, 
                              {'$group': {'_id':'$address.state', 'count': {'$sum': 1}}}, 
                              {'$sort': {'count': -1}}])
pprint.pprint([result for result in cursor])
#Get number of documents per 'address.city' in descending order                 
cursor = collection.aggregate([{'$match': {'address.city': {'$exists': 1}, 'address.state': 'Nevada'}}, 
                              {'$group': {'_id':'$address.city', 'count': {'$sum': 1}}}, 
                              {'$sort': {'count': -1}}]) 
pprint.pprint([result for result in cursor])
#Get number of documents per 'address.postcode' in descending order that have 'address.city' = Las Vegas (top 5 postcodes)
cursor = collection.aggregate([{'$match': {'address.postcode': {'$exists': 1}, 
                               'address.city': 'Las Vegas'}}, 
                              {'$group': {'_id':'$address.postcode', 'count': {'$sum': 1}}}, 
                              {'$sort': {'count': -1}},
                              {'$limit': 5}])                 
pprint.pprint([result for result in cursor])

client.close()
