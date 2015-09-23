import xml.etree.cElementTree as ET
import re
import pprint
from collections import defaultdict


def count_tags(filename):
    '''
    Processes the map file and returns a dictionary with the tags in the file 
    as keys and the number of times each is present.
    ''' 
    counter = defaultdict(int)
    
    for event, elem in ET.iterparse(filename, events = ('start',)):
        counter[elem.tag] += 1
          
    return dict(counter)
    
        
def count_keys(filename, filter_key = None):
    '''
    Processes the map file and returns a dictionary with the values of the 'tag' attribute 'k' 
    of 'node's and 'way's in the file as keys and the number of times each is present.
    If the string 'filter_key' is not 'None', filters the 'tag' attribute 'k' keys to the
    ones that match the regex expression 'filter_key'.
    '''
    counter = defaultdict(int)
    
    for event, elem in ET.iterparse(filename):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if filter_key: 
                    if re.search(filter_key, tag.attrib['k']):
                        counter[tag.attrib['k']] += 1
                else:
                    counter[tag.attrib['k']] += 1                   
                           
    return dict(counter)
    
def get_values(filename, filter_key = None):
    '''
    Processes the map file and returns a dictionary with the 'tag' attribute 'k' 
    of 'node's and 'way's in the file as keys and the related 'tag' attribute 'v' as values.
    If the string 'filter_key' is not 'None', filters the 'tag' attribute 'k' keys to the
    ones that match the regex expression 'filter_key'.
    '''
    values = defaultdict(set)
    
    for event, elem in ET.iterparse(filename):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if filter_key: 
                    if re.search(filter_key, tag.attrib['k']):
                        values[tag.attrib['k']].add(tag.attrib['v'])
                                                      
    return dict(values)
    
    
def audit_key_types(filename):
    
    '''
    Processes the map file and divides the values of 'tag' attributes 'k' of 'node's and 'way's 
    in the file in four groups: lower case without colon ('lower'), lower case with colon 
    ('lower_colon'), with problematic characters ('problemchars' and other ('other').
    Returns a dictionary with the group labels as keys and the number of times each is present.
    '''
    
    lower = r'^([a-z]|_)*$' 
    lower_colon = r'^([a-z]|_)*:([a-z]|_)*$'
    problemchars = r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]'
    
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    
    for event, elem in ET.iterparse(filename):
        if elem.tag == "node" or elem.tag == "way":
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

    
def audit_street_type(keys_to_check, street_name, expected_dict):
    '''
    Checks if each regex expression in 'expected_dict' keys can match a string
    in 'street_name'. If it does, checks if that string is in the corresponding
    list in 'expected_dict' value. If it isn't, adds the string to the dictionary 
    'keys_to_check' as key and 'street_name' as value.
    '''
    for regex in expected_dict keys():
        found = re.search(regex, street_name, re.IGNORECASE)
        if found:
            street_type = found.group()
            if street_type not in expected_dict[regex]:
                keys_to_check[street_type].add(street_name)
            
            
def audit_postcode(keys_to_check, postcode, expected_postcode_re):
    '''
    Checks if the 'postcode' matches the regex expression in 'expected_postcode_re'.
    If not adds it to the dictionary 'keys_to_check' as both key and value.
    ''' 
    found = re.search(expected_postcode_re, postcode)
    if found == None:
        keys_to_check[postcode].add(postcode) 


def audit_state_name(keys_to_check, state_name, expected_state_name):
    '''
    Checks if the state_name is equal to the 'expected_state_name'.
    If not adds it to the dictionary 'keys_to_check' as key and increases the number
    it is present (value) by 1.
    '''
    if state_name != expected_state_name:
        keys_to_check[state_name] += 1
        

def audit_key(filename, key_type, audit_key_function, expected_keys, dict_value_type):
    '''
    Processes the map file and returns a dictionary with the values of the 'tag' 
    attribute 'k' of 'node's and 'way's that are equal to 'key_type' and for
    which 'audit_key_function' adds a key, value pair (value is int or set
    depending on 'dict_value_type'.
    '''
    keys_to_check = defaultdict(dict_value_type)
    for event, elem in ET.iterparse(filename):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if tag.attrib['k'] == key_type:
                    audit_key_function(keys_to_check, tag.attrib['v'], expected_keys)
                    
    return dict(keys_to_check)
    
    
if __name__ == "__main__":
    
    filename = 'las_vegas_nevada.osm' 
    
    #Count each tag
    pprint.pprint(count_tags(filename)) 
    
    #Count each 'tag' attribute 'k' in 'node' or 'way' that contain the string 'addr'
    pprint.pprint(count_keys(filename, r'^addr'))
    
    #Check 'tag' attribute 'v' of 'tag' attribute 'k' = 'address'
    pprint.pprint(get_values(filename, r'^address$'))
    
    #Audit postcode format (Nevada postcodes start with 889-891)
    expected_postcode_re = r'^(889|890|891)[0-9]{2}$'
    pprint.pprint(audit_key(filename, "addr:postcode", audit_postcode, expected_postcode_re, set))
    
    #Audit street types
    expected_dict = {r'\b\S+\.?$': ["Street", "Avenue", "Road", "Boulevard", "Drive", "Highway",
                            "Lane", "Parkway", "Way", "Court", "Circle"]}               
                            
    pprint.pprint(audit_key(filename, "addr:street", audit_street_type, expected_dict, set))
