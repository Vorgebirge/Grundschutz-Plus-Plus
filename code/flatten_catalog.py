# Stand 16.03.2026
import re
from helper_functions import read_json_file, sort_list_naturally, write_json_file
from collections import defaultdict
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

CONTROL_ATTRIBUTES_DICT = dict(([key, config['control_attributes'][key]]) for key in config['control_attributes'])
CONTROL_ATTRIBUTES = CONTROL_ATTRIBUTES_DICT.keys()
PRAKTIK_TYPES_DICT = dict(([key.upper(), config['praktik_types'][key]]) for key in config['praktik_types'])

PATH_CATALOG = config['orte']['path_catalog']
PATH_CATALOG_FLATTENED = config['orte']['path_catalog_flattened']
PATH_CATALOG_FLATTENED_REVERSED = config['orte']['path_catalog_flattened_reversed']
PATH_CONTROL_ATTRIBUTES = config['orte']['path_control_attributes']

# Reguläre Ausdrücke https://regex101.com/)
RE_CONTROL_ID = r'^[A-Z]{2,4}(\.\d+){2,}$'
RE_PRAKTIK_ID = r'^[A-Z]{2,4}'
RE_PRAKTIK_THEMA_ID = r'^[A-Z]{2,4}(\.\d+)'

def locators_and_their_items(catalog_segment: dict) -> dict:
    ''' Der GS++ catalog des BSI im Format json in github ist ein dictionary mit einer 
    tiefverschachtelten Struktur aus weiteren dictionaries und lists und den eigentlichen 
    Inhalten des catalog wie z. B. Titel, Texte Hinweise der Anforderungen (Struktur konform
    zu oscal).
    Der vorliegende catalog wird in ein flaches dict überführt. Dessen key sind locator gebildet  
    aus dem ursprünglichen dict und value die entsprechenden Werte. Die Locator bilden die verschachtelte
    Struktur aus dict und list ab. Sie bestehen aus den keys (dict) und indizes (list) zu einem 
    Wert. Beispiele:
    
    "('catalog', 'uuid')": "bf5d3cde-1c6b-4329-9a10-fdbe84279177"
    Locator ist ('catalog', 'uuid') und Wert ist bf5d3cde-1c6b-4329-9a10-fdbe84279177
    
     "('catalog', 'groups', 0, 'groups', 0, 'id')": "GC.1"
    Locator ist ('catalog', 'groups', 0, 'groups', 0, 'id') und Wert ist GC.1
    
    "('catalog', 'groups', 6, 'groups', 2, 'controls', 0, 'parts', 0, 'props', 1, 'value')": "Arbeitsvertrag"
    Locator ist ('catalog', 'groups', 6, 'groups', 2, 'controls', 0, 'parts', 0, 'props', 1, 'value') und Wert ist "Arbeitsvertrag"
    
    Die Schlüssel (Locator) des neuen dict sind tuple. Wenn das neue dict als json-Datei
    gespeichert werden soll, müssen die tuple vorher in str konvertiert werden.
    '''    
    dict_locators_and_their_items = dict()
    
    def recursion_locators_and_their_items(catalog_segment, locator = []):   
        nonlocal dict_locators_and_their_items
        if isinstance(catalog_segment, dict):    
            for key, value in catalog_segment.items():            
                locator.append(key)
                recursion_locators_and_their_items(value, locator)
                del locator[-1]            
        elif isinstance(catalog_segment, (list, tuple)):     
            for index, item in enumerate(catalog_segment):            
                locator.append(index)
                recursion_locators_and_their_items(item, locator)
                del locator[-1]
        else:                        
            dict_locators_and_their_items[tuple(locator)] = catalog_segment
    
    recursion_locators_and_their_items(catalog_segment)    
    return dict_locators_and_their_items

def items_and_their_locators(catalog_segment: dict) -> dict:   
    '''
    Input ist der Output (dict) der Funktion locators_and_their_items. Kehrt die Schlüssel 
    und Werte um. In dem dict aus locators_and_their_items verweisen oft immer mehrere 
    Schlüssel (Locator) auf einen Wert (item). Die Locator zu einem Wert werden in einer Liste 
    zusammengefasst. Die Schlüssel in dem reversed dict sind die items und die Werte die jeweilige
    Liste mit den Locator zu dem item.
    '''    
    reversed_dict = defaultdict(list)
    for k, v in catalog_segment.items():
        reversed_dict[v].append(list(k)) #k ist ein tuple
    return reversed_dict
   
def get_locator_of_item(item: str, item_identifier = '') -> list:
    locator_list = CATALOG_ITEMS_AND_LOCATORS.get(item, '')
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

def get_container_of_item(locator_of_item: str):
    container = CATALOG
    for locator_part in locator_of_item[:-1]:
        container = container[locator_part]
    return container

def get_controls_in_container(container: dict) -> list:    
    controls_in_container = []
    container_locators_and_their_items = locators_and_their_items(container)    
    container_items_and_their_locators = items_and_their_locators(container_locators_and_their_items)
    for item in container_items_and_their_locators.keys():                
        if re.match(RE_CONTROL_ID, item) and \
        (container_items_and_their_locators.get(item,'')[0][-1] == 'id'):
            controls_in_container.append(item)
    return controls_in_container    

def get_attribute_of_control(control_id: str, attribute = ''):
    locator_of_control = get_locator_of_item(control_id, 'id')
    locator_of_control_stm = get_locator_of_item(control_id + '_stm', 'id')
    locator_of_control_gdn = get_locator_of_item(control_id + '_gdn', 'id')
    container_of_control = get_container_of_item(locator_of_control)
    container_of_control_stm = get_container_of_item(locator_of_control_stm)
    container_of_control_gdn = get_container_of_item(locator_of_control_gdn)
    
    def get_single_attribute_of_control(control_id, attribute):
        nonlocal container_of_control, container_of_control_stm, container_of_control_gdn
        
        if attribute in ('praktik'):
            praktik_id, praktik_id_title =  re.search(RE_PRAKTIK_ID, control_id).group(), ''
            locator_of_praktik = get_locator_of_item(praktik_id, 'id')
            container_of_praktik = get_container_of_item(locator_of_praktik)            
            if container_of_praktik and container_of_praktik['title']:
                praktik_id_title = praktik_id + ' ' + container_of_praktik['title']
            return praktik_id_title
        elif attribute in ('praktik_thema'):
            praktik_thema_id, praktik_thema_id_title =  re.search(RE_PRAKTIK_THEMA_ID, control_id).group(), ''
            locator_of_praktik = get_locator_of_item(praktik_thema_id, 'id')
            container_of_praktik = get_container_of_item(locator_of_praktik)            
            if container_of_praktik and container_of_praktik['title']:
                praktik_thema_id_title = praktik_thema_id + ' ' + container_of_praktik['title']
            return praktik_thema_id_title    
        elif attribute in ('praktik_typ'):
            praktik_id =  re.search(RE_PRAKTIK_ID, control_id).group()
            return PRAKTIK_TYPES_DICT.get(praktik_id, '')
        elif attribute in ('class', 'id', 'title'):                
            return container_of_control.get(attribute, '')
        elif attribute in ('params'):
            if container_of_control.get('params',''):
                return {param.get('id', ''): param.get('label', '') for param in container_of_control['params']}   
        elif attribute in ('related', 'required') and ('links' in container_of_control.keys()):        
            ergebnis = [item['href'] for item in container_of_control['links'] if item['rel'] == attribute]            
            return ', '.join(ergebnis)
        elif attribute in ('alt-identifier', 'effort_level', 'sec_level', 'tags'):        
            return next((item['value'] for item in container_of_control['props'] if item['name'] == attribute), '')     
        elif attribute in ('prose'):        
            return container_of_control_stm['prose']    
        elif attribute in ('documentation', 'result', 'action_word', 'modal_verb', 'result_specification', 'target_object_categories'):    
            return next((item["value"] for item in container_of_control_stm["props"] if item["name"] == attribute), '')       
        elif attribute in ('guidance'):                
            return container_of_control_gdn.get('prose', '') 
        elif attribute in ('verbesserung'):
            return ', '.join(get_controls_in_container(container_of_control)[1:])            
        return ''
        
    if attribute:
        return get_single_attribute_of_control(control_id, attribute)
    elif not attribute:
        dict_attributes = defaultdict(str)
        for attribute in CONTROL_ATTRIBUTES:
            dict_attributes[attribute] = get_single_attribute_of_control(control_id, attribute)
        return dict_attributes    
    
def main():
    dict_control_attributes = defaultdict(dict)

    for control_id in sort_list_naturally(get_controls_in_container(CATALOG)):
        dict_control_attributes[control_id]= get_attribute_of_control(control_id)
     
    #k ist type tuple (kein zulässiger dict key), deshalb str(k)
    write_json_file({str(k): v for k, v in CATALOG_LOCATORS_AND_ITEMS.items()}, PATH_CATALOG_FLATTENED) 
    write_json_file(CATALOG_ITEMS_AND_LOCATORS, PATH_CATALOG_FLATTENED_REVERSED) 
    write_json_file(dict_control_attributes, PATH_CONTROL_ATTRIBUTES)

if __name__ == "__main__":
    CATALOG = read_json_file(PATH_CATALOG)
    CATALOG_LOCATORS_AND_ITEMS = locators_and_their_items(CATALOG)
    CATALOG_ITEMS_AND_LOCATORS = items_and_their_locators(CATALOG_LOCATORS_AND_ITEMS)
    main()