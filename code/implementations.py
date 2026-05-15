# Stand: 15.05.2026
from flatten_catalog import locators_and_their_items
from helper_functions import read_json_file, sort_dict_naturally, today, write_json_file, ymd2dmy
from collections import defaultdict
from configparser import ConfigParser
#from datetime import datetime

config = ConfigParser()
config.read('config.ini')

COMPONENT = defaultdict(dict)

COMPONENT['aws_iam']['commit'] = config['orte']['commit_aws_iam']
COMPONENT['aws_iam']['source'] = config['orte']['source_aws_iam']
COMPONENT['aws_iam']['path'] = config['orte']['path_aws_iam']

COMPONENT['aws_security_hub']['commit'] = config['orte']['commit_aws_security_hub']
COMPONENT['aws_security_hub']['source'] = config['orte']['source_aws_security_hub']
COMPONENT['aws_security_hub']['path'] = config['orte']['path_aws_security_hub']

COMPONENT['netzarchitektur']['commit'] = config['orte']['commit_netzarchitektur']
COMPONENT['netzarchitektur']['source'] = config['orte']['source_netzarchitektur']
COMPONENT['netzarchitektur']['path'] = config['orte']['path_netzarchitektur']

COMPONENT['passwortrichtlinie']['commit'] = config['orte']['commit_passwortrichtlinie']
COMPONENT['passwortrichtlinie']['source'] = config['orte']['source_passwortrichtlinie']
COMPONENT['passwortrichtlinie']['path'] = config['orte']['path_passwortrichtlinie']

COMPONENT['wlan']['commit'] = config['orte']['commit_wlan']
COMPONENT['wlan']['source'] = config['orte']['source_wlan']
COMPONENT['wlan']['path'] = config['orte']['path_wlan']

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
            
        
   