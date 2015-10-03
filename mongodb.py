import pprint
from pymongo import MongoClient

class database(object):
    
    def __init__(self, database_name, collection_name):
        
       self.client = MongoClient('localhost:27017')
       self.db = self.client[database_name][collection_name]
       
    def disconnect(self):
        
        return self.client.close()
       
    def search_one(self, criteria_dict = {}):
        
        pprint.pprint(self.db.find_one(criteria_dict))
       
    def search(self, criteria_dict = {}):
        
        cursor = self.db.find(criteria_dict)
        
        for entry in cursor:
            pprint.pprint(entry)
        
    def aggregation(self, pipeline):
        
        cursor = self.db.aggregate(pipeline)
        
        for entry in cursor:
            pprint.pprint(entry)
        
if __name__ == "__main__":
    
    #mongoimport --db osm --collection lasvegas --drop --file las_vegas_nevada.json   
    
    db = database('osm', 'lasvegas')
    
    db.aggregation([{'$group': {'_id': '# nodes or ways', 'count': {'$sum': 1}}}])
    
    db.aggregation([{'$match': {'address.state': {'$exists': 1}}}, 
                    {'$group': {'_id':'$address.state', 'count': {'$sum': 1}}}, 
                    {'$sort': {'count': -1}}])
                    
    db.aggregation([{'$match': {'address.city': {'$exists': 1}, 'address.state': 'Nevada'}}, 
                    {'$group': {'_id':'$address.city', 'count': {'$sum': 1}}}, 
                    {'$sort': {'count': -1}}]) 
                    
    db.aggregation([{'$match': {'address.postcode': {'$exists': 1}, 
                                'address.city': 'Las Vegas', 'address.state': 'Nevada'}}, 
                    {'$group': {'_id':'$address.postcode', 'count': {'$sum': 1}}}, 
                    {'$sort': {'count': -1}},
                    {'$limit': 5}])  
                    
    db.disconnect()
