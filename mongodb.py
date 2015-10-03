import pprint
from pymongo import MongoClient

class database(object):
    
    def __init__(self, database_name, collection_name):
        
       client = MongoClient('localhost:27017')
       self.db = client[database_name][collection_name]
       
    def search_one(self, criteria_dict = {}):
        
        cursor = self.db.find_one(criteria_dict)
        pprint.pprint(entry)
       
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
    
    db.search_one()
    
    db.aggregation([{'$group': {'_id': '# nodes or ways', 'count': {'$sum': 1}}}])
