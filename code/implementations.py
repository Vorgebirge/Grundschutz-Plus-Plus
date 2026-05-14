# Stand: 14.05.2026
from flatten_catalog import locators_and_their_items
from helper_functions import read_json_file, write_json_file, ymd2dmy
from collections import defaultdict
from configparser import ConfigParser
from datetime import datetime

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

PATH_IMPLEMENTATIONS = config['orte']['path_implementations'] + datetime.today().strftime("%y%m%d") + '.json'

dict_implementations = defaultdict(list)

for component in COMPONENT:    
    mydict = read_json_file(COMPONENT[component]['path'])
    mydict_flattened = locators_and_their_items(mydict)
    
    for locator in mydict_flattened:        
        implementation = dict()
        if locator[-1] == 'control-id':
            control_id = mydict_flattened[locator] 
            implementation['source'] = COMPONENT[component]['source']
            implementation['commit'] = ymd2dmy(COMPONENT[component]['commit'])
            
            if (locator_of_description := locator[:-1] + ('description',)) in mydict_flattened:
                implementation['description'] = mydict_flattened[locator_of_description]
                                
            if (locator_of_remarks := locator[:-1] + ('remarks',)) in mydict_flattened:
                implementation['remarks'] = mydict_flattened[locator_of_remarks]
        
            dict_implementations[control_id].append(implementation) 

write_json_file(dict_implementations, PATH_IMPLEMENTATIONS)
            
        
   