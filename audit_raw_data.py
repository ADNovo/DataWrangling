import xml.etree.cElementTree as ET
import re
import pprint
import json
import codecs
from collections import defaultdict
from clean_data import * 

class map_file(object):
    '''
    Map file class
    '''
    def __init__(self, filename):
        self.filename = filename
        
    def count_tags(self):
       '''
       Processes the map file and returns a dictionary with the tags in the file 
       as keys and the number of times each is present as values.
       ''' 
       counter = defaultdict(int)
       
       for event, elem in ET.iterparse(self.filename, events = ('start',)):
           counter[elem.tag] += 1
          
       return dict(counter)
    
    def count_keys(self, filter_key = None):
        '''
        Processes the map file and returns a dictionary with the values of the 'tag' attribute 'k' 
        of 'node's and 'way's in the file as keys and the number of times each is present as values.
        If the string 'filter_key' is not 'None', filters the 'tag' attribute 'k' keys to the
        ones that match the regex expression 'filter_key'.
        '''
        counter = defaultdict(int)
        
        for event, elem in ET.iterparse(self.filename):
            if elem.tag == "node" or elem.tag == "way":
                for tag in elem.iter("tag"):
                    if filter_key: 
                        if re.search(filter_key, tag.attrib['k']):
                            counter[tag.attrib['k']] += 1
                    else:
                        counter[tag.attrib['k']] += 1                   
                               
        return dict(counter)
    
    def get_values(self, filter_key = None):
        '''
        Processes the map file and returns a dictionary with the 'tag' attribute 'k' 
        of 'node's and 'way's in the file as keys and the related 'tag' attribute 'v' as values.
        If the string 'filter_key' is not 'None', filters the 'tag' attribute 'k' keys to the
        ones that match the regex expression 'filter_key'.
        '''
        values = defaultdict(set)
        
        for event, elem in ET.iterparse(self.filename):
            if elem.tag == "node" or elem.tag == "way":
                for tag in elem.iter("tag"):
                    if filter_key: 
                        if re.search(filter_key, tag.attrib['k']):
                            values[tag.attrib['k']].add(tag.attrib['v'])
                                                          
        return dict(values)
    
    
    def audit_key_types(self):
        '''
        Processes the map file and divides the values of 'tag' attributes 'k' of 'node's and 'way's 
        in the file in four groups: lower case without colon ('lower'), lower case with colon 
        ('lower_colon'), with problematic characters ('problemchars' and other ('other').
        Returns a dictionary with the group labels as keys and the number of times each is present
        as values.
        '''
        lower = r'^([a-z]|_)*$' 
        lower_colon = r'^([a-z]|_)*:([a-z]|_)*$'
        problemchars = r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]' 
        keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
        
        for event, elem in ET.iterparse(self.filename):
            if elem.tag == "node" or elem.tag == "way":
                for tag in elem.iter("tag"):
                    key_type = tag.attrib['k']
                    #Counts lower case tag keys without colon and problematic characters
                    if re.search(lower, key_type):
                        keys["lower"] += 1
                    #Counts lower case tag keys with colon and without problematic characters
                    elif re.search(lower_colon, key_type):
                        keys["lower_colon"] += 1  
                    #Counts tag keys with colon problematic characters
                    elif re.search(problemchars, key_type):
                        keys["problemchars"] += 1  
                    #Counts the remaining tag keys 
                    else:
                        keys["other"] += 1 
            
        return keys
          
    def audit_key_values(self, key_type, expected_dict):
        '''
        Processes the map file and checks the 'tag' attribute 'v' of 'node's and 'way's 
        with 'attribute 'k' equal to 'key_type'. Returns a dictionary with:
        1) Tag ' attribute 'v' as values for the ones that contain a string that matches 
        one of the regex expressions in 'expected_dict' keys and the string as value, if
        the string is not in the respective expected_dict value;
        2) Tag ' attribute 'v' as value and key for the ones that do not contain a string
        that matches one of the regex expressions in 'expected_dict' keys.
        '''
        keys_to_check = defaultdict(set)
        
        for event, elem in ET.iterparse(self.filename):
            if elem.tag == "node" or elem.tag == "way":
                for tag in elem.iter("tag"):
                    if tag.attrib['k'] == key_type:
                        for regex in expected_dict.keys():
                            found = re.search(regex, tag.attrib['v'], re.IGNORECASE)
                            if found:
                                expression = found.group()
                                if expression not in expected_dict[regex]:
                                    keys_to_check[expression].add(tag.attrib['v'])
                            else:
                                keys_to_check[tag.attrib['v']].add(tag.attrib['v'])
                                
        return dict(keys_to_check)
               
    def audit_key_pattern(self, key_type, expected_field_re):
        '''
        Processes the map file and checks the 'tag' attribute 'v' of 'node's and 'way's 
        with 'attribute 'k' equal to 'key_type'. Returns a dictionary with the 'tag' attribute 
        'v' that do not match the regex expression in ' expected_field_re' as keys and the
        number of times they are present in the file as values.
        ''' 
        keys_to_check = defaultdict(int)
        
        for event, elem in ET.iterparse(self.filename):
            if elem.tag == "node" or elem.tag == "way":
                for tag in elem.iter("tag"):
                    if tag.attrib['k'] == key_type:
                        found = re.search(expected_field_re, tag.attrib['v'])
                        if found == None:
                            keys_to_check[tag.attrib['v']] += 1
                            
        return dict(keys_to_check)
                
    def process(self, clean_function):
        '''
        Processes the map file and generates a json file with the same name, 
        cleaning the data with clean_function. 
        '''
        file_out = "{0}.json".format(self.filename[:-4])
        
        with codecs.open(file_out, "w") as w:
            for event, elem in ET.iterparse(self.filename):
                map_elem = map_element(elem)
                if map_elem.get_element():
                    clean_function(map_elem)
                    w.write(json.dumps(map_elem.get_element(), indent=2)+"\n")
                    
if __name__ == "__main__":
    
    mfile = map_file('las_vegas_nevada.osm') 
    #Count each tag
    pprint.pprint(mfile.count_tags()) 
    #Count each 'tag' attribute 'k' in 'node' or 'way' that contain the string 'addr'
    pprint.pprint(mfile.count_keys(r'^addr'))
    #Check 'tag' attribute 'v' of 'tag' attribute 'k' = 'address'
    pprint.pprint(mfile.get_values(r'^address$'))
    #Audit street types to check if the last word is one in the following dictionary values
    expected_dict = {r'\b\S+\.?$': ["Street", "Avenue", "Road", "Boulevard", "Drive", "Highway",
                            "Lane", "Parkway", "Way", "Court", "Circle"]}               
    pprint.pprint(mfile.audit_key_values("addr:street", expected_dict))
    #Audit postcode to check if it is a 5-digit number starting with 889 or 89 
    pprint.pprint(mfile.audit_key_pattern("addr:postcode", r'(^889[0-9]{2}$)|(^89[0-9]{3}$)'))
    #Audit city to check if it matches "Las Vegas"    
    pprint.pprint(mfile.audit_key_values("addr:city", {"^Las Vegas$": "Las Vegas"}))
    #Audit state to check if it matches "Nevada"    
    pprint.pprint(mfile.audit_key_values("addr:state", {"^Nevada$":"Nevada"}))
    #Audit country to check if it matches "USA"
    pprint.pprint(mfile.audit_key_values("addr:country", {"^USA$":"USA"}))
    #Audit housenumber to check if it is a number with between 1 and 4 digits
    pprint.pprint(mfile.audit_key_pattern("addr:housenumber", r'(^[0-9]{1,5}$)'))        
    #Check 'tag' attribute 'v' of 'tag' attribute 'k' = 'addr:suite'
    pprint.pprint(mfile.get_values(r'^addr:suite$'))
    #Check 'tag' attribute 'v' of 'tag' attribute 'k' = 'addr:door'
    pprint.pprint(mfile.get_values(r'^addr:door$'))
    #Check 'tag' attribute 'v' of 'tag' attribute 'k' = 'addr:interpolation'
    pprint.pprint(mfile.get_values(r'^addr:interpolation$'))
