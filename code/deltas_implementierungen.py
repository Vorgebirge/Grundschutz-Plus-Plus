# Stand: 13.06.2026
from flatten_catalog import locators_and_their_items
from helper_functions import load_json, section_only_options, sort_dict_naturally, today, write_json_file, ymd2dmy
from collections import defaultdict
from configparser import ConfigParser, ExtendedInterpolation

config = ConfigParser(interpolation = ExtendedInterpolation())
config.read('config.ini')

PATH_CATALOG_CONTROL_ATTRIBUTES = config['orte']['path_control_attributes']
CATALOG_CONTROL_ATTRIBUTES = load_json(PATH_CATALOG_CONTROL_ATTRIBUTES)
CATALOG_CONTROL_ATTRIBUTES_COMMIT_DATUM = config['DEFAULT']['commit']
    
def get_last_string(tuple_or_list):
    for element in reversed(tuple_or_list):
        if isinstance(element, str):
            return element
    return None        


def get_implementierung_details(flat_json_implementierung, catalog_control_attributes):
    
    # Ermittle zu jeder control uuid die zugehörige control id (im Kontext des catalog commits aus config.ini)
    map_control_uuid_auf_control_id = dict()
    for control_id in catalog_control_attributes:    
        map_control_uuid_auf_control_id['_' + catalog_control_attributes[control_id]['alt-identifier']] = control_id
      
    # Ermittle zu jeder control uuid aus der Implemntierung ausgewählte Details
    implementierung = defaultdict(dict)
    for locator in flat_json_implementierung:
        if locator[-1] == 'control-id': # gemeint ist die uuid einer control
            control_uuid = flat_json_implementierung.get(locator,'') 
            
            implementierung[control_uuid]['control_id'] = map_control_uuid_auf_control_id[control_uuid]
            
            value = flat_json_implementierung.get(locator[:-1] + ('description',),'') 
            implementierung[control_uuid]['description'] = value
                        
            value = flat_json_implementierung.get(locator[:-1] + ('remarks',),'') 
            implementierung[control_uuid]['remarks'] = value
            
            # Ermittle alle zugehörigen uuid der zugehörigen bzw. übergeordneten 'implemented 
            # requirements', 'control implementations', 'components, component.definition'
            for i in range(1, len(locator) + 1):                
                prefix = locator[:i-1] + ('uuid',)
                if uuid := FLAT_JSON_IMPLEMENTIERUNG_B.get(prefix,''):                    
                    implementierung[control_uuid]['uuid_' + get_last_string(prefix[:-1])] = uuid
        
    return implementierung                

    

# Lese die Metadaten pro Komponente aus config.ini
KOMPONENTE = defaultdict(dict)
for section in config.sections():    
    if (typ := config[section].get('typ')) and \
    (typ == 'implementierungen_komponente'):    
        for option in section_only_options(config, section):       
            if option in ('commit', 'commit_a', 'commit_b', 'name', \
            'path', 'path_a', 'path_b', 'source'):                                
                KOMPONENTE[section][option] = config.get(section, option)                    

# Iteriere über alle Komponenten mit Werten zu commit_a und commit_b, um die
# Differenzen zwischen beiden commits zu ermitteln
for komponente in KOMPONENTE:
    # Ignoriere Komponenten ohne Werte zu commit_a und commit_b
    # Die liegen in config.ini nicht vor oder sind auskommentiert, weil
    # keine Differenzen ermittelt werden sollen
    if not(KOMPONENTE[komponente].get('commit_a', '') and \
    KOMPONENTE[komponente].get('commit_b', '')):
        continue
    
    OSCAL_JSON_IMPLEMENTIERUNG_A = load_json(KOMPONENTE[komponente].get('path_a', ''))
    OSCAL_JSON_IMPLEMENTIERUNG_B = load_json(KOMPONENTE[komponente].get('path_b', ''))
    
    FLAT_JSON_IMPLEMENTIERUNG_A = locators_and_their_items(OSCAL_JSON_IMPLEMENTIERUNG_A)
    FLAT_JSON_IMPLEMENTIERUNG_B = locators_and_their_items(OSCAL_JSON_IMPLEMENTIERUNG_B)
    
    details_implemtierung_a = get_implementierung_details(FLAT_JSON_IMPLEMENTIERUNG_A, CATALOG_CONTROL_ATTRIBUTES)
    details_implemtierung_b = get_implementierung_details(FLAT_JSON_IMPLEMENTIERUNG_B, CATALOG_CONTROL_ATTRIBUTES)
    

    

    
    
    