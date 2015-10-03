import pprint
from pymongo import MongoClient

class db_collection(object):
    
    def __init__(self, database_name, collection_name):
        
       self.client = MongoClient('localhost:27017')
       self.collection = self.client[database_name][collection_name]
       
    def disconnect(self):
        
        return self.client.close()
    
    def get_collection(self):
        
        return self.collection
        
    def aggregation(self, pipeline):
        
        cursor = self.collection.aggregate(pipeline)
        
        return [result for result in  cursor]
        
if __name__ == "__main__":
    
    #mongoimport --db osm --collection lasvegas --drop --file las_vegas_nevada.json   
    
    db = db_collection('osm', 'lasvegas')
    
    print(db.get_collection().find().count()) 
    
    pprint.pprint(db.aggregation([{'$group': {'_id':'$type', 'count': {'$sum': 1}}}]))
    
    pprint.pprint(db.aggregation([{'$group': {'_id':'overall', 'unique_users': {'$addToSet': '$created.user'}}},
                                  {'$project': {'number_unique_users': {'$size': '$unique_users'}}}])
                                  
    pprint.pprint(db.aggregation([{'$match': {'address.state': {'$exists': 1}}}, 
                                  {'$group': {'_id':'$address.state', 'count': {'$sum': 1}}}, 
                                  {'$sort': {'count': -1}}]))
                    
    pprint.pprint(db.aggregation([{'$match': {'address.city': {'$exists': 1}, 'address.state': 'Nevada'}}, 
                                  {'$group': {'_id':'$address.city', 'count': {'$sum': 1}}}, 
                                  {'$sort': {'count': -1}}])) 
                    
    pprint.pprint(db.aggregation([{'$match': {'address.postcode': {'$exists': 1}, 
                                   'address.city': 'Las Vegas', 'address.state': 'Nevada'}}, 
                                  {'$group': {'_id':'$address.postcode', 'count': {'$sum': 1}}}, 
                                  {'$sort': {'count': -1}},
                                  {'$limit': 5}]))  
                    
    db.disconnect()
