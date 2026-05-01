# Stand: 16.03.2026
# Änderungen Attribute vor 16.03.2026 -> ab 16.03.2026
# ergebnis          -> result
# handlungsworte    -> action_word
# modalverb         -> modal_verb
# präzisierung      -> result_specification
# target_objects    -> target_object_categories

from helper_functions import read_json_file, sort_dict_naturally, write_json_file
from collections import defaultdict
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

PATH_CONTROL_ATTRIBUTES = config['orte']['path_control_attributes']
PATH_CONTROL_ATTRIBUTES_UPDATE = config['orte']['path_control_attributes_update']

catalog = read_json_file(PATH_CONTROL_ATTRIBUTES)
catalog_update = defaultdict(dict)

update = {'ergebnis': 'result', 'handlungsworte': 'action_word', 'modalverb': 'modal_verb', 'präzisierung': 'result_specification', 'target_objects': 'target_object_categories'}

for control_id in catalog.keys():
    for attribute in catalog[control_id].keys():        
        if attribute in ('ergebnis', 'handlungsworte', 'modalverb', 'präzisierung', 'target_objects'):
            catalog_update[control_id][update[attribute]] = catalog[control_id][attribute]
        else:    
            catalog_update[control_id][attribute] = catalog[control_id][attribute]
    catalog_update[control_id] = sort_dict_naturally(catalog_update[control_id])   

write_json_file(catalog_update, PATH_CONTROL_ATTRIBUTES_UPDATE)