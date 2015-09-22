import xml.etree.cElementTree as ET
import re
import json
          
          
def clean_street_name(street_name, mapping):
    street_type_re = r'\b\S+\.?$'
    found = re.search(street_type_re, street_name, re.IGNORECASE).group()
    street_name = re.sub(found+'$', mapping[found], street_name)

    return street_name


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


def process_map(filename, db):
    file_out = "{0}.json".format(filename)
    with codecs.open(file_out, "w") as w:
        for event, element in ET.iterparse(filename):
            json_elem = shape_element(element)
            if json_elem:
                w.write(json.dumps(json_elem, indent=2)+"\n")
        
