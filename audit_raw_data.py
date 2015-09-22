import xml.etree.cElementTree as ET
import re
import pprint
from collections import defaultdict


def count_tags(filename):
    '''
    Processes the map file and returns a dictionary with the tags in the file 
    as keys and the number of times each is present
    ''' 
    counter = defaultdict(int)
    
    for event, elem in ET.iterparse(filename, events = ('start',)):
        counter[elem.tag] += 1
          
    return dict(counter)
    
        
def count_keys(filename, filter_key = None):
    '''
    Processes the map file and returns a dictionary with the values of a 'tag' attribute 'k' 
    from 'node's and 'way's in the file as keys and the number of times each is present
    If the string 'filter_key' is not 'None', filters the 'tag' attribute 'k' keys to the
    ones that contain the string 'filter_key'
    '''
    counter = defaultdict(int)
    
    for event, elem in ET.iterparse(filename):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if filter_key: 
                    if filter_key in tag.attrib['k']:
                        counter[tag.attrib['k']] += 1
                else:
                    counter[tag.attrib['k']] += 1                   
                           
    return dict(counter)
    
    
def audit_key_types(filename):
    
    lower = r'^([a-z]|_)*$' 
    lower_colon = r'^([a-z]|_)*:([a-z]|_)*$'
    problemchars = r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]'
    
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    
    for event, elem in ET.iterparse(filename):
        if elem.tag == "tag":
            for tag in elem.iter("tag"):
                k_type = tag.attrib['k']
                
                #Counts lower case tag keys without colon and problematic characters
                if re.search(lower, k_type):
                    keys["lower"] += 1
                #Counts lower case tag keys with colon and without problematic characters
                elif re.search(lower_colon, k_type):
                    keys["lower_colon"] += 1  
                #Counts tag keys with colon problematic characters
                elif re.search(problemchars, k_type):
                    keys["problemchars"] += 1  
                #Counts the remaining tag keys 
                else:
                    keys["other"] += 1 
        
    return keys


def audit_key(filename, key_type, audit_key_function, expected_keys = ''):
    '''
    Processes the map file and returns a dictionary with the values of the 'tag' 
    attribute 'k' from 'node's and 'way's that are equal to 'key_type' and for
    which 'audit_key_function' adds a key, value pair
    '''
    keys_to_check = defaultdict(set)
    for event, elem in ET.iterparse(filename):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if tag.attrib['k'] == key_type:
                    audit_key_function(keys_to_check, tag.attrib['v'], expected_keys)
                    
    return dict(keys_to_check)
    
    
#Audit functions that require less than 3 parameters have 'placeholder's so that
#the function 'audit_key' can be used with any of them
    
def audit_street_type(keys_to_check, street_name, expected_last_words):
    '''
    Checks if the last word in 'street_name' is one of the 'expected_last_words'
    If not adds the last word to the dictionary 'keys_to_check' as key and 
    'street_name' as value
    '''
    street_type_re = r'\b\S+\.?$'
    found = re.search(street_type_re, street_name, re.IGNORECASE)
    if found:
        street_type = found.group()
        if street_type not in expected_last_words:
            keys_to_check[street_type].add(street_name)
            
            
def audit_postcode(keys_to_check, postcode, expected_postcode_re):
    '''
    Checks if the 'postcode' matches the pattern in 'expected_postcode_re'.
    If not adds it to the dictionary 'keys_to_check' as both key and value
    ''' 
    found = re.search(expected_postcode_re, postcode)
    if found == None:
        keys_to_check[postcode].add(postcode) 


def audit_state_name(keys_to_check, state_name, expected_state_name):
    '''
    Checks if the state_name is equal to the 'expected_state_name'.
    If not adds it to the dictionary 'keys_to_check' as both key and value
    '''
    if state_name != expected_state_name:
        keys_to_check[state_name].add(state_name)
    
    
if __name__ == "__main__":
    
    filename = 'las_vegas_nevada.osm' 
    
    #Count each tag
    pprint.pprint(count_tags(filename)) 
    
    #Count each 'tag' attribute 'k' in 'node' or 'way' that starts with 'addr:'
    pprint.pprint(count_keys(filename, "addr:"))
    
    #Audit postcode format (Nevada postcodes start with 889-891)
    expected_postcode_re = r'^(889|890|891)[0-9]{2}$'
    pprint.pprint(audit_key(filename, "addr:postcode", audit_postcode, expected_postcode_re))
    
    #Audit street types
    expected_last_words = ["Street", "Avenue", "Road", "Boulevard", "Drive", "Highway",
                            "Lane", "Parkway", "Way", "Court", "Circle"]               
                            
    pprint.pprint(audit_key(filename, "addr:street", audit_street_type, expected_last_words))
