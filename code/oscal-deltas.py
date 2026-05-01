# Stand 25.04.2026
from flatten_catalog import locators_and_their_items
from helper_functions import read_json_file, sort_list_naturally, visualize
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

PATH_CATALOG_A = config['orte']['path_catalog_a']
PATH_CATALOG_FLATTENED_REVERSED_A = config['orte']['path_catalog_flattened_reversed_a']
PATH_CONTROL_ATTRIBUTES_A = config['orte']['path_control_attributes_a']

PATH_CATALOG_B = config['orte']['path_catalog_b']
PATH_CATALOG_FLATTENED_REVERSED_B = config['orte']['path_catalog_flattened_reversed_b']
PATH_CONTROL_ATTRIBUTES_B = config['orte']['path_control_attributes_b']

def get_container_of_item(catalog: dict, locator_of_item: str):
    container = catalog
    for locator_part in locator_of_item[:-1]:
        container = container[locator_part]
    return container

def get_locator_of_item(catalog_items_and_locators: dict, item: str, item_identifier = '') -> list:
    locator_list = catalog_items_and_locators.get(item, '')
    if locator_list and item_identifier: #es gibt das item im catalog und ein 
                                         #item_identifier ist vorgegeben (z.B. 'id')
        for locator in locator_list: #items im catalog haben können mehr als einen locator haben
            if str(locator[-1]) == item_identifier: #die letzte Stelle des 
                                                    #locators passt zum item_identifier                         
                return locator #der erste locator mit item_identifier 
                               #als key (dict) oder index (list) für item           
        return '' #kein locator mit item_identifier als key (dict) oder index (list) für item       
    elif locator_list: # kein item_identifier vorgegeben
        return locator_list[0] #wenn es mehrere locator gibt, der erste in der Liste
    else:
        return []    

def main():    
    control_ids_a = CONTROL_ATTRIBUTES_A.keys()
    control_ids_b = CONTROL_ATTRIBUTES_B.keys()
    intersection_control_ids = sort_list_naturally(set(control_ids_a) & set(control_ids_b))
    
    for control_id in intersection_control_ids: 
        locator_of_item_a = get_locator_of_item(CATALOG_FLATTENED_REVERSED_A, control_id, 'id')
        container_of_item_a = get_container_of_item(CATALOG_A, locator_of_item_a)
        locators_in_container_a = set(locators_and_their_items(container_of_item_a).keys())
        
        locator_of_item_b = get_locator_of_item(CATALOG_FLATTENED_REVERSED_B, control_id, 'id')
        container_of_item_b = get_container_of_item(CATALOG_B, locator_of_item_b)
        locators_in_container_b = set(locators_and_their_items(container_of_item_b).keys())
        
        if locators_in_container_a != locators_in_container_b:
            intersection = locators_in_container_a & locators_in_container_b            
            print('A', control_id, locators_in_container_a - intersection)
            print('B', control_id, locators_in_container_b - intersection)
            print()

if __name__ == "__main__":
    CATALOG_A = read_json_file(PATH_CATALOG_A)    
    CATALOG_FLATTENED_REVERSED_A = read_json_file(PATH_CATALOG_FLATTENED_REVERSED_A)
    CONTROL_ATTRIBUTES_A = read_json_file(PATH_CONTROL_ATTRIBUTES_A)
    
    CATALOG_B = read_json_file(PATH_CATALOG_B)    
    CATALOG_FLATTENED_REVERSED_B = read_json_file(PATH_CATALOG_FLATTENED_REVERSED_B)
    CONTROL_ATTRIBUTES_B = read_json_file(PATH_CONTROL_ATTRIBUTES_B)
    
    main()

