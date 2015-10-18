import pprint
from pymongo import MongoClient

class db_collection(object):
    '''
    MongoDB collection object
    '''
    def __init__(self, database_name, collection_name):
       '''
       Connects to MongoDB and starts the collection object.
       '''        
       self.client = MongoClient('localhost:27017')
       self.collection = self.client[database_name][collection_name]
       
    def get_collection(self):
        '''
        Returns the collection.
        '''         
        return self.collection
       
    def disconnect(self):
        '''
        Disconnects from MongoDB.
        '''
        return self.client.close()
        
    def aggregation(self, pipeline):
        '''
        Runs the aggregation 'pipeline' on the collection and returns the results.
        '''
        cursor = self.collection.aggregate(pipeline)
        return [result for result in  cursor]
        
if __name__ == "__main__":
    
    #mongoimport --db osm --collection lasvegas --drop --file las_vegas_nevada.json   
    
    db = db_collection('osm', 'lasvegas')
    #Get the number of documents in the collection
    documents = db.get_collection().find().count()
    print 'number of documents:', documents
    #Get the number of 'node' and 'way' in the collection
    pprint.pprint(db.aggregation([{'$group': {'_id':'$type', 'count': {'$sum': 1}}}]))
    #Get the number of unique users that contributed to the collection
    pprint.pprint(db.aggregation([{'$group': {'_id':'overall', 'unique_users': {'$addToSet': '$created.user'}}},
                                  {'$project': {'number_unique_users': {'$size': '$unique_users'}}}]))
    #Get the user with the higher contribution and his contribution (%)
    pprint.pprint(db.aggregation([{'$group': {'_id': '$created.user', 'documents_user': {'$sum': 1}}},
                                  {'$project': {'user_name': '$created.user', 'percentage': {'$multiply': 
                                              [{"$divide": ['$documents_user', documents]}, 100]}}},
                                  {'$sort': {'percentage': -1}},
                                  {'$limit': 1}]))
    #Get total contribution (%) of top 5 contributors
    pprint.pprint(db.aggregation([{'$group': {'_id': '$created.user', 'documents_user': {'$sum': 1}}},
                                  {'$project': {'user_name': '$created.user', 'percentage': {'$multiply': 
                                              [{"$divide": ['$documents_user', documents]}, 100]}}},
                                  {'$sort': {'percentage': -1}},
                                  {'$limit': 5},
                                  {'$group': {'_id': 'top 5', 'ratio': {'$sum': '$percentage'}}}]))
    #Get total contribution (%) of top 10 contributors                           
    pprint.pprint(db.aggregation([{'$group': {'_id': '$created.user', 'documents_user': {'$sum': 1}}},
                                  {'$project': {'user_name': '$created.user', 'percentage': {'$multiply': 
                                              [{"$divide": ['$documents_user', documents]}, 100]}}},
                                  {'$sort': {'percentage': -1}},
                                  {'$limit': 10},
                                  {'$group': {'_id': 'top 10', 'ratio': {'$sum': '$percentage'}}}]))
    #Get number of documents without address
    no_address = db.get_collection().find({'address': {'$exists': 0}}).count()
    print 'number of documents without address:', no_address
    #Get number of documents per 'address.state' in descending order                             
    pprint.pprint(db.aggregation([{'$match': {'address.state': {'$exists': 1}}}, 
                                  {'$group': {'_id':'$address.state', 'count': {'$sum': 1}}}, 
                                  {'$sort': {'count': -1}}]))
    #Get number of documents per 'address.city' in descending order                 
    pprint.pprint(db.aggregation([{'$match': {'address.city': {'$exists': 1}, 'address.state': 'Nevada'}}, 
                                  {'$group': {'_id':'$address.city', 'count': {'$sum': 1}}}, 
                                  {'$sort': {'count': -1}}])) 
    #Get number of documents per 'address.postcode' in descending order that have 'address.city' = Las Vegas (top 5 postcodes)
    pprint.pprint(db.aggregation([{'$match': {'address.postcode': {'$exists': 1}, 
                                   'address.city': 'Las Vegas', 'address.state': 'Nevada'}}, 
                                  {'$group': {'_id':'$address.postcode', 'count': {'$sum': 1}}}, 
                                  {'$sort': {'count': -1}},
                                  {'$limit': 5}]))  
    db.disconnect()
