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
    '''
    If the element is the one with the unexpected field 'address',
    returns that element with the content of that field divided
    amongst the appropriate fields.
    '''
    if 'address' in element.keys():
        if type(element['address']) == str:
            element['address'] = {'housenumber': '275',
                                    'street': 'East Tropicana Ave.', 
                                    'suite': 'Suite 100',
                                    'city': 'Las Vegas', 
                                    'state': 'NV',
                                    'postcode': '89169'}
    return element
        

def split_field(element, newfield, sourcefield, newfield_list):
    
    if 'address' in element.keys():
        if sourcefield in element['address'].keys():
            source = element['address'][sourcefield]           
            for regex in newfield_list:
                expression = re.search(regex, source, re.IGNORECASE)
                if expression:
                    source = source[:expression.start()] + source[expression.end():]
                    element['address'][sourcefield] = source.strip().strip(',')
                    if element['address'][sourcefield] == '':
                        del element['address'][sourcefield]
                    if newfield not in element['address'].keys():
                        element['address'][newfield] = expression.group()
                    else:
                        element['address'][newfield] += ' ' + expression.group()

    return element
    
    
def clean_street(element, mapping):
    if 'address' in element.keys():
        if 'street' in element['address'].keys():
            street = element['address']['street']
            for regex in mapping.keys():
                expression = re.search(regex, street, re.IGNORECASE)
                if expression:
                    street = re.sub(expression.group(), mapping[regex], street)
            
            for word in street.split():
                capitalized = re.search(r'^[A-Z]+$', word)
                if capitalized:
                    street = re.sub(capitalized.group()[1:], capitalized.group()[1:].lower(), street)    
            element['address']['street'] = street
      
    return element

    
def clean_postcodeORhousenumber(element, field, cleaning_pattern):

    if 'address' in element.keys():
        if field in element['address'].keys():
            field_value = element['address'][field]
            clean_field = re.search(cleaning_pattern, field_value, re.IGNORECASE).group()
            element['address'][field] = clean_field
    
    return element
    
    
def clean_stateORcountry(element, field, mapping):
    if 'address' in element.keys():
        if field in element['address'].keys():
            for key in mapping.keys():
                if key == element['address'][field]:
                    element['address'][field] = mapping[key]  
                    
    return element
           
def clean_element(element):
    '''
    Performs all the data reallocation and cleaning tasks on a given  element.
    '''
    #Divide the string in the key 'address' of one of the elements into all the
    #appropriate "sub-keys"
    element = clean_address(element)
    #Remove any 'suite' data (end of 'street' starting with 'Suite' or 'Ste'/'STE'
    #and followed by one letters/digits combination) from 'street' and add it to 'suite'
    element = split_field(element, 'suite', 'street', [r'(Suite|Ste)\s(\S)*$'])
    #Remove any 'housenumber' data (start of 'street' composed by a number with 
    #1 to 5 digits) from 'street' and add it to 'housenumber'
    element = split_field(element, 'housenumber', 'street', [r'^[0-9]{1,5}'])
    #Remove any 'door' data end of 'street' starting with '#' and followed by
    #by one number with between 1 and 5 digits) from 'street' and add it to 'door'
    element = split_field(element, 'door', 'street', [r'#([0-9]{1,5})$'])
    #Remove any 'state' name ('NV' or 'Nevada') from 'postcode' and add it to 'state'
    element = split_field(element, 'state', 'postcode', [r'NV', r'Nevada'])
    #Remove any 'door' data (# followed by a 3-digit number or a letter optionally
    #followed by a dash and a digit) from 'housenumber and add it to 'door'
    element = split_field(element, 'door', 'housenumber', [r'#([0-9]{3})', r'[A-Z](\-[0-9])?\b'])
    
    #Clean 'street' data, expanding all abbreviations in the dictionary to the respective full word
    element = clean_street(element, {r'\b(S)(\.|\b)': 'South', r'\b(N)(\.|\b)': 'North',
                                     r'\b(W)(\.|\b)': 'West', r'\b(E)(\.|\b)': 'East',
                                     r'\b(Ave)(\.|\b)': 'Avenue', r'\b(Blvd)(\.|\b)': 'Boulevard',
                                     r'\b(Dr)(\.|\b)': 'Drive', r'\b(Ln)(\.|\b)': 'Lane',
                                     r'\b(Mt)(\.|\b)': 'Mountain', r'\b(Pkwy)(\.|\b)': 'Parkway', 
                                     r'\b(Rd)(\.|\b)': 'Road', r'\b(St)(\.|\b)': 'Street'})
    #Clean 'postcode', reducing it to a 5-digit number starting with 889 or 89 (Nevada postal codes)    
    element = clean_postcodeORhousenumber(element, 'postcode', r'(^889[0-9]{2}$)|(^89[0-9]{3}$)')
    #Clean 'state', expanding all abbreviations in the dictionary to the respective
    #full word
    clean_stateORcountry(element, 'state', {'AZ': 'Arizona', 'CA': 'California', 
                                  'NV': 'Nevada'})
    #Clean 'country', expanding the abbreviation 'US' to 'USA
    clean_stateORcountry(element, 'country', {'US': 'USA'})
    #Clean 'postcode', reducing it to a number with between 1 and 5 digits
    clean_postcodeORhousenumber(element, 'housenumber', r'([0-9]{1,5})')                                
                               
    return element
        
             
def process_map(filename):
    '''
    Processes the map file and generates a json file with the same name, with 
    the data cleaned and each element formatted accordingly to the function 
    shape_element.
    '''
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
