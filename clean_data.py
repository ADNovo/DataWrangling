import xml.etree.cElementTree as ET
import re
import json
import codecs
          
          
def shape_element(element):
    address_keep_re = r'^addr:([a-z]|_)*$'
    address_skip_re = r'^addr:street:([a-z]|_)*$'
    problemchars = r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]'
    created_list = [ "version", "changeset", "timestamp", "user", "uid"]
    
    node = {}
    created_dict = {}
    pos_list = ["",""]
    address_dict = {}
    refs_list = []
    
    if element.tag == "node" or element.tag == "way":
        node["type"] = element.tag
        for tag in element.iter("tag"):
            k = tag.attrib['k']
            if re.search(problemchars, k):
                continue
            elif re.search(address_keep_re, k):
                sub_key_re = r':([a-z]|_)*$'
                sub_key = re.search(sub_key_re, k).group()[1:]
                address_dict[sub_key] = tag.attrib['v']
            elif re.search(address_skip_re, k):
                continue
            else:
                node[k] = tag.attrib['v']
                
        for tag in element.iter():
            attributes_dict = tag.attrib
            for key in  attributes_dict.keys():
                if key in element.attrib.keys():
                    if key in created_list:
                        created_dict[key] =  attributes_dict[key]
                    elif key == 'lat':
                        pos_list[0] = float(attributes_dict[key])
                    elif key == 'lon':
                        pos_list[1] = float(attributes_dict[key])
                    else:
                        node[key] = attributes_dict[key]                        
                else:
                    if key == 'k' or key == 'v':
                        continue
                    elif re.search(problemchars, key):
                        continue
                    elif key == 'ref':
                        refs_list.append(attributes_dict[key])
                    else:
                        node[key] = attributes_dict[key]  
                        
        if created_dict.keys() != []:
            node["created"] = created_dict
        if "" not in pos_list:
            node["pos"] = pos_list            
        if address_dict.keys() != []:
            node["address"] = address_dict
        if refs_list != []:
            node["node_refs"] = refs_list  
            
        return node
        
    else:
        return None
        

def clean_address(element):
    if 'address' in element.keys():
        if type(element['address']) == str:
            element['address'] = {'housenumber': '275',
                                    'street': 'East Tropicana Ave.', 
                                    'suite': 'Suite 100',
                                    'city': 'Las Vegas', 
                                    'state': 'NV',
                                    'postcode': '89169'}
    return element   
    
    
def add_state(element, state_list):
          
    if 'state' not in element['address'].keys() and 'postcode' in element['address'].keys():
          for state in state_list:
                    if state in element['address']['postcode']:
                        element['address']['state'] = state  
                        
    return element


def clean_postcode(element, cleaning_pattern):

    if 'address' in element.keys():
        if 'postcode' in element['address'].keys():
            postcode = element['address']['postcode']
            clean_postcode = re.search(cleaning_pattern, postcode).group()
            element['address']['postcode'] = clean_postcode
    
    return element
    
   
def clean_street_name(element, cleaning_pattern):
    '''
    If element has an address with street, checks if the last word of 
    the street name is a key in 'cleaning_patern'. If it is, replaces 
    that word by the corresponding value in 'cleaning_patern'
    '''
    pass
   
 
def clean_element(element):
    
    element = clean_address(element)
    element = add_state(element, ['NV', 'Nevada')
    element = clean_postcode(element, r'(889|890|891)[0-9]{2}')
    
    return element
    
             
def process_map(filename, cleaning_functions_dict = {}, cleaning_pattern_dict = {}, before_clean = None):
    file_out = "{0}.json".format(filename[:-4])
    with codecs.open(file_out, "w") as w:
        for event, element in ET.iterparse(filename):
            json_elem = shape_element(element)
            if json_elem:
                clean_json_elem = clean_element(json_elem)
                w.write(json.dumps(clean_json_elem, indent=2)+"\n")
                
                
if __name__ == "__main__":
    
    filename = 'las_vegas_nevada.osm'
    process_map(filename)
