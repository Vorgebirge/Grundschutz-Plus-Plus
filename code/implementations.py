# Stand: 25.05.2026
from flatten_catalog import locators_and_their_items
from helper_functions import read_json_file, sort_dict_naturally, today, write_json_file, ymd2dmy
from collections import defaultdict
from configparser import ConfigParser, ExtendedInterpolation

config = ConfigParser(interpolation = ExtendedInterpolation())
config.read('config.ini')

KOMPONENTEN = [str.strip() for str in config['implementierungen']['komponenten'].split(',') if str.strip()]
COMPONENT = defaultdict(dict)
for komponente in KOMPONENTEN:
    for attribut in ('name', 'commit', 'source', 'path'):
        COMPONENT[komponente][attribut] = config[komponente][attribut]

PATH_CONTROL_ATTRIBUTES = config['orte']['path_control_attributes']
#PATH_IMPLEMENTATIONS = config['orte']['path_implementations'] + today() + '.json'
PATH_IMPLEMENTATIONS = config['orte']['path_implementations']

dict_implementations = defaultdict(list)

CONTROL_ATTRIBUTES = read_json_file(PATH_CONTROL_ATTRIBUTES)

map_uuid_control_id = dict()
for control_id in CONTROL_ATTRIBUTES:    
    map_uuid_control_id['_' + CONTROL_ATTRIBUTES[control_id]['alt-identifier']] = control_id


for component in COMPONENT:    
    mydict = read_json_file(COMPONENT[component]['path'])
    mydict_flattened = locators_and_their_items(mydict)
    
    for locator in mydict_flattened:        
        implementation = dict()
        if locator[-1] == 'control-id':
            control_uuid = mydict_flattened[locator] 
            
            if (locator_of_uuid := locator[:-1] + ('uuid',)) in mydict_flattened:
                implementation['uuid'] = mydict_flattened[locator_of_uuid]
            
            implementation['control_alt-identifier'] = control_uuid[1:]
            implementation['source'] = COMPONENT[component]['source']
            implementation['commit_source'] = ymd2dmy(COMPONENT[component]['commit'])
            implementation['excel_row'] = 0
                        
            if (locator_of_description := locator[:-1] + ('description',)) in mydict_flattened:
                implementation['description'] = mydict_flattened[locator_of_description]
                                
            if (locator_of_remarks := locator[:-1] + ('remarks',)) in mydict_flattened:
                implementation['remarks'] = mydict_flattened[locator_of_remarks]
            
            control_id = map_uuid_control_id[control_uuid]
            dict_implementations[control_id].append(implementation) 
            #dict_implementations[control_uuid].append(implementation) 
dict_implementations = sort_dict_naturally(dict_implementations)

excel_row = 2
for control_id in dict_implementations:
    for implementation in dict_implementations[control_id]:
        implementation['excel_row'] = excel_row        
        excel_row += 1                 

write_json_file(dict_implementations, PATH_IMPLEMENTATIONS)
            
        
   