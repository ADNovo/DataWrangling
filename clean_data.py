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
        
        
def clean_postcode(element, cleaning_pattern):
    '''
    
    '''
    if 'address' in element.keys():
        if 'postcode' in element['address'].keys():
            postcode = element['address']['postcode']
            clean_postcode = re.search(cleaning_pattern['re_expression'], postcode).group()
            
            if 'state' not in element['address'].keys() and 'state' in cleaning_pattern.keys():
                for state in cleaning_pattern['state']:
                    if state in postcode:
                        element['address']['state'] = state    
           
            element['address']['postcode'] = clean_postcode
    
    return element
    
       
def clean_street_name(element, cleaning_pattern):
    '''
    If element has an address with street, checks if the last word of 
    the street name is a key in 'cleaning_patern'. If it is, replaces 
    that word by the corresponding value in 'cleaning_patern'
    '''
    pass
   
 
def clean_element(element, cleaning_functions_dict, cleaning_pattern_dict):
      
    if set(cleaning_functions_dict.keys()) != set(cleaning_pattern_dict.keys()):
        raise ValueError
                           
    for key in cleaning_functions_dict.keys():
        element = cleaning_functions_dict[key](element, cleaning_pattern_dict[key])
    
    return element
    
    
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
    
             
def process_map(filename, cleaning_functions_dict = {}, cleaning_pattern_dict = {}, before_clean = None):
    file_out = "{0}.json".format(filename[:-4])
    with codecs.open(file_out, "w") as w:
        for event, element in ET.iterparse(filename):
            json_elem = shape_element(element)
            if json_elem:
                if before_clean != None:
                    json_elem = before_clean(json_elem)
                clean_json_elem = clean_element(json_elem, cleaning_functions_dict, cleaning_pattern_dict)
                w.write(json.dumps(clean_json_elem, indent=2)+"\n")
                
                
if __name__ == "__main__":
    
    filename = 'las_vegas_nevada.osm'
    
    cleaning_functions_dict = {'address_postcode': clean_postcode}
    
    clean_pattern_address_postcode = {'re_expression': r'(889|890|891)[0-9]{2}',
                                        'state': ['NV', 'Nevada']}
    
    cleaning_pattern_dict = {'address_postcode': clean_pattern_address_postcode}
    
    process_map(filename, cleaning_functions_dict, cleaning_pattern_dict, clean_address)
