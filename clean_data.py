import re
from audit_raw_data import *

class map_element(object):
    
    def __init__(self, elem):

        address_keep_re = r'^addr:([a-z]|_)*$'
        address_skip_re = r'^addr:street:([a-z]|_)*$'
        problemchars = r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]'
        created_list = [ "version", "changeset", "timestamp", "user", "uid"]
        
        json_elem = {}
        created_dict = {}
        pos_list = ["",""]
        address_dict = {}
        refs_list = []
        
        if elem.tag == "node" or elem.tag == "way":
            json_elem["type"] = elem.tag
            for tag in elem.iter("tag"):
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
                    json_elem[k] = tag.attrib['v']
                    
            for tag in elem.iter():
                attributes_dict = tag.attrib
                for key in  attributes_dict.keys():
                    if key in elem.attrib.keys():
                        if key in created_list:
                            created_dict[key] =  attributes_dict[key]
                        elif key == 'lat':
                            pos_list[0] = float(attributes_dict[key])
                        elif key == 'lon':
                            pos_list[1] = float(attributes_dict[key])
                        else:
                            json_elem[key] = attributes_dict[key]                        
                    else:
                        if key == 'k' or key == 'v':
                            continue
                        elif re.search(problemchars, key):
                            continue
                        elif key == 'ref':
                            refs_list.append(attributes_dict[key])
                        else:
                            json_elem[key] = attributes_dict[key]  
                            
            if created_dict.keys() != []:
                json_elem["created"] = created_dict
            if "" not in pos_list:
                json_elem["pos"] = pos_list            
            if address_dict.keys() != []:
                json_elem["address"] = address_dict
            if refs_list != []:
                json_elem["node_refs"] = refs_list  
               
            self.element = json_elem            
        else:
            self.element = None
            
    def get_element(self):
      
        return self.element
            
    def split_field(self, newfield, sourcefield, newfield_re_list):
       
        if 'address' in self.element.keys():
            if sourcefield in self.element['address'].keys():
                source = self.element['address'][sourcefield]           
                for regex in newfield_re_list:
                    expression = re.search(regex, source, re.IGNORECASE)
                    if expression:
                        source = source[:expression.start()] + source[expression.end():]
                        self.element['address'][sourcefield] = source.strip().strip(',')
                        if self.element['address'][sourcefield] == '':
                            del self.element['address'][sourcefield]
                        if newfield not in self.element['address'].keys():
                            self.element['address'][newfield] = expression.group()
                        else:
                            self.element['address'][newfield] += ' ' + expression.group()
        
    def replace_in_field(self, field, replace_mapping):
  
        if 'address' in self.element.keys():
            
            if type(self.element['address']) == str:
                self.element['address'] = replace_mapping['address']
                
            elif field in self.element['address'].keys():
                field = self.element['address'][field]
                
                for key in replace_mapping.keys():
                    expression = re.search(key, field, re.IGNORECASE)
                    if expression:
                        field = re.sub(expression.group(), replace_mapping[key], field)
                
    def limit_field(self, field, limit_pattern):

        if 'address' in self.element.keys():
            if field in self.element['address'].keys():
                field_value = self.element['address'][field]
                clean_field = re.search(limit_pattern, field_value, re.IGNORECASE).group()
                self.element['address'][field] = clean_field
    
    def remove_from_field(self, field, remove_pattern):
 
        if 'address' in self.element.keys():
            if field in self.element['address'].keys():
                field_value = self.element['address'][field]
                remove_string = re.search(remove_pattern, field_value, re.IGNORECASE) 
                if remove_string:
                    field_value = field_value[:remove_string.start()] + field_value[remove_string.end():]
                self.element['address'][field] = field_value.upper().strip()          
                      
def clean(mapElem):
    '''
    Performs all the data reallocation and cleaning tasks on a given  element.
    '''
    #Divide the string in the key 'address' of one of the elements into all the
    #appropriate "sub-keys"
    mapElem.replace_in_field('address', {'address': {'housenumber': '275',
                                                     'street': 'East Tropicana Ave.', 
                                                     'suite': 'Suite 100',
                                                     'city': 'Las Vegas', 
                                                     'state': 'NV',
                                                     'postcode': '89169'}})
    #Remove any 'suite' data (end of 'street' starting with 'Suite' or 'Ste'/'STE'
    #and followed by one letters/digits combination) from 'street' and add it to 'suite'
    mapElem.split_field('suite', 'street', [r'(Suite|Ste)\s(\S)*$'])
    #Remove any 'housenumber' data (start of 'street' composed by a number with 
    #1 to 5 digits) from 'street' and add it to 'housenumber'
    mapElem.split_field('housenumber', 'street', [r'^[0-9]{1,5}'])
    #Remove any 'door' data end of 'street' starting with '#' and followed by
    #by one number with between 1 and 5 digits) from 'street' and add it to 'door'
    mapElem.split_field('door', 'street', [r'#([0-9]{1,5})$'])
    #Remove any 'state' name ('NV' or 'Nevada') from 'postcode' and add it to 'state'
    mapElem.split_field('state', 'postcode', [r'NV', r'Nevada'])
    #Remove any 'state' name ('NV') from 'city' and add it to 'state'
    mapElem.split_field('state', 'city', [r'NV']) 
    #Remove any 'door' data (# followed by a 3-digit number or a letter optionally
    #followed by a dash and a digit) from 'housenumber and add it to 'door'
    mapElem.split_field('door', 'housenumber', [r'#([0-9]{3})', r'[A-Z](\-[0-9])?\b'])
    #Clean 'street' data, expanding all abbreviations in the dictionary to the respective full word
    mapElem.replace_in_field('street', {r'\b(S)(\.|\b)': 'South', r'\b(N)(\.|\b)': 'North',
                                        r'\b(W)(\.|\b)': 'West', r'\b(E)(\.|\b)': 'East',
                                        r'\b(Ave)(\.|\b)': 'Avenue', r'\b(Blvd)(\.|\b)': 'Boulevard',
                                        r'\b(Dr)(\.|\b)': 'Drive', r'\b(Ln)(\.|\b)': 'Lane',
                                        r'\b(Mt)(\.|\b)': 'Mountain', r'\b(Pkwy)(\.|\b)': 'Parkway', 
                                        r'\b(Rd)(\.|\b)': 'Road', r'\b(St)(\.|\b)': 'Street'})
    #Clean 'postcode', reducing it to a 5-digit number starting with 889 or 89 (Nevada postal codes)    
    mapElem.limit_field('postcode', r'(889[0-9]{2})|(89[0-9]{3})')
    #Clean 'state', expanding all abbreviations in the dictionary to the respective full word
    mapElem.replace_in_field('state', {'AZ': 'Arizona', 'CA': 'California','NV': 'Nevada'})
    #Clean 'country', expanding the abbreviation 'US' to 'USA
    mapElem.replace_in_field('country', {'US': 'USA'})
    #Clean 'postcode', reducing it to a number with between 1 and 5 digits
    mapElem.limit_field('housenumber', r'([0-9]{1,5})')                                
    #Clean 'suite', removing the "Suite" expression, as well as its abbreviations
    mapElem.remove_from_field('suite', r'Suite|Ste')
    #Clean 'door', removing the character "#"
    mapElem.remove_from_field('door', r'#')
              
if __name__ == "__main__":
    
    mapfile = map_file('las_vegas_nevada.osm')    
    mapfile.process(clean)
