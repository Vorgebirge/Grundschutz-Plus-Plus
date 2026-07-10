'''
Erzeugt eine Markup-Datei zu zwei commits A und B des GS++ Anwenderkatalogs.
Steuerung der Auswahl zu A und B über die Datei commit.ini
'''
# Stand 10.07.2026
import re
from helper_functions import inline_diff, read_json_file, sort_dict_naturally, sort_list_naturally, ymd2dmy
from collections import defaultdict
from configparser import ConfigParser, ExtendedInterpolation

# Regulaere Ausdruecke, https://regex101.com/
# Markdown https://www.markdownguide.org

config = ConfigParser(interpolation = ExtendedInterpolation())
config.read('config.ini')

CONTROL_ATTRIBUTES_DICT_OSCAL = dict(([key, config['control_attributes'][key]]) for key in config['control_attributes'])
CONTROL_ATTRIBUTES_DICT_XLSX = {v: k for k, v in CONTROL_ATTRIBUTES_DICT_OSCAL.items()}
  
PATH_CONTROL_ATTRIBUTES_A = config['orte']['path_control_attributes_a']
PATH_CONTROL_ATTRIBUTES_B = config['orte']['path_control_attributes_b']
PATH_DIFF_REPORT_UUID_CENTRIC = config['orte']['path_diff_report_uuid_centric']

CA_A = read_json_file(PATH_CONTROL_ATTRIBUTES_A)
CA_B = read_json_file(PATH_CONTROL_ATTRIBUTES_B)
COMMIT_A = config['DEFAULT']['commit_a']
COMMIT_DATE_A = ymd2dmy(COMMIT_A)
COMMIT_B = config['DEFAULT']['commit_b']
COMMIT_DATE_B = ymd2dmy(COMMIT_B)
RE_PREFIX_PARAMETER = r'{{\s*insert\s*:\s*param,\s*'
RE_SUFFIX_PARAMETER = r'\s*}}'

# Unterschiedliche Listen von Anforderungen
CA_A_OHNE_CA_B = sort_list_naturally(list(set(CA_A) - set(CA_B))) # entfernte Anforderungen
CA_B_OHNE_CA_A = sort_list_naturally(list(set(CA_B) - set(CA_A))) # neue Anforderungen
CA_A_UND_CA_B = sort_list_naturally(list(set(CA_A) & set(CA_B))) # beibehaltene Anforderungen

# Zu einer gegebenen UUID die zugehörige Anforderung ID
GET_C_ID_A_OF_UUID = {CA_A[c_id_a]['alt-identifier']: c_id_a for c_id_a in CA_A}
GET_C_ID_B_OF_UUID = {CA_B[c_id_b]['alt-identifier']: c_id_b for c_id_b in CA_B}

# Unterschiedliche Listen von UUID
UUID_A_OHNE_B = set(GET_C_ID_A_OF_UUID.keys()) - set(GET_C_ID_B_OF_UUID.keys())
UUID_B_OHNE_A = set(GET_C_ID_B_OF_UUID.keys()) - set(GET_C_ID_A_OF_UUID.keys())
UUID_A_UND_B = set(GET_C_ID_A_OF_UUID.keys()) & set(GET_C_ID_B_OF_UUID.keys())

# Unterschiedliche Mengen von Anforderung-Attributen
ATTRIBUTE_CA_A = {CONTROL_ATTRIBUTES_DICT_OSCAL[k] for d in CA_A.values() for k in d}
ATTRIBUTE_CA_B = {CONTROL_ATTRIBUTES_DICT_OSCAL[k] for d in CA_B.values() for k in d}
# Gelöschte Attribute bei Wechsel von commit A zu commit B des Anwenderkatalogs
ATTRIBUTE_CA_A_OHNE_CA_B = sort_list_naturally(ATTRIBUTE_CA_A - ATTRIBUTE_CA_B)
# Neue Attribute bei Wechsel von commit A zu commit B des Anwenderkatalogs
ATTRIBUTE_CA_B_OHNE_CA_A = sort_list_naturally(ATTRIBUTE_CA_B - ATTRIBUTE_CA_A)
# Gemeinsame Attribute bei Wechsel von commit A zu commit B des Anwenderkatalogs
ATTRIBUTE_CA_B_UND_CA_A = sort_list_naturally(ATTRIBUTE_CA_A & ATTRIBUTE_CA_B)

def control_titel_prose_params(control_attributes, control_id, mit_titel = True):
    '''Gibt zu einer Anforderung-ID (control_id) einen String zurück: Titel der 
    Anforderung (nur wenn mit_titel == True), Text der Anforderung. Wenn der Text
    Parameter-Platzhalter enthält, werden diese durch die vorliegenden Parameter-Werte ersetzt.   
    '''    
    control_title = ''
    if mit_titel and (control_title := control_attributes[control_id].get('title', '')):
        control_title += ' '
    control_prose = control_attributes[control_id].get('prose', '')
    control_parameter = control_attributes[control_id].get('params', '')
        
    if control_prose and control_parameter: # Prüfung auf Parameter-Platzhalter    
        # Ersetzung Parameter-Platzhalter durch vorliegende Parameter-Werte
        mystr = re.sub(RE_PREFIX_PARAMETER, '', control_prose)
        mystr = re.sub(RE_SUFFIX_PARAMETER, '', mystr)        
        for parameter_id, parameter_wert in control_parameter.items():
            mystr = re.sub(parameter_id.strip(), '{' + parameter_wert.strip() + '}', mystr)
        return control_title + mystr
    else:
        return control_title + control_prose 

# ----------- Ermittle Attribute mit Werteänderungen, Anzahl von Anforderungen mit Werte-Änderungen gemeinsamer Attributen
delta_attribute = defaultdict(dict)
for uuid in UUID_A_UND_B:    
    c_id_a, c_id_b = GET_C_ID_A_OF_UUID[uuid], GET_C_ID_B_OF_UUID[uuid]    
    delta_attribute[c_id_a]['deltas'] = []
    for attr_xlsx in ATTRIBUTE_CA_B_UND_CA_A:
        attr_oscal = CONTROL_ATTRIBUTES_DICT_XLSX[attr_xlsx]    
        if CA_A[c_id_a][attr_oscal] != CA_B[c_id_b][attr_oscal]:
            delta_attribute[c_id_a]['deltas'].append(attr_xlsx) 
    if delta_attribute[c_id_a]['deltas']:
        delta_attribute[c_id_a]['uuid'] = uuid
        delta_attribute[c_id_a]['c_id_b'] = c_id_b
        delta_attribute[c_id_a]['deltas'] = sort_list_naturally(delta_attribute[c_id_a]['deltas'])
    else:
        del delta_attribute[c_id_a]
    
delta_attribute = sort_dict_naturally(delta_attribute)
anforderungen_mit_deltas = len(delta_attribute.keys())
attribute_mit_deltas = sum(len(delta_attribute[c_id_a]['deltas']) for c_id_a in delta_attribute.keys())
    
# ---------- Inhaltsverzeichnis -----------------------------------------
report = []
report.append('# GS++ control deltas github ' + COMMIT_DATE_A + ' & ' + COMMIT_DATE_B)
report.append('## Inhalte')

report.append('- [' + str(len(UUID_A_OHNE_B)) + ' entfernte Anforderungen-UUID](#entfernte-anforderungen-uuid)    ')
report.append('- [' + str(len(UUID_B_OHNE_A)) + ' neue Anforderungen-UUID](#neue-anforderungen-uuid)    ')
report.append('- [' + str(len(ATTRIBUTE_CA_A_OHNE_CA_B)) + ' entfallene und ' + str(len(ATTRIBUTE_CA_B_OHNE_CA_A)) + ' neue Attribute der Anforderungen](#entfallene-und-neue-attribute-der-anforderungen)')
report.append('- [' + str(anforderungen_mit_deltas) + ' Anforderungen-UUID mit ' + str(attribute_mit_deltas) + ' geaenderten Attributen](#anforderungen-uuid-mit-geaenderten-attributen)    ')
report.append('    - [Übersicht](#anforderungen-uuid-mit-geaenderten-attributen---uebersicht)    ')
report.append('    - [Details](#anforderungen-uuid-mit-geaenderten-attributen---details)    ')

# --------------- Entfernte Anforderungen-UUID ---------------------
report.append('## Entfernte Anforderungen-UUID')
report.append('[Zurück zu Inhalte](#inhalte)')

report.append(str(len(UUID_A_OHNE_B)) + ' entfernte Anforderungen-UUID aus Anwenderkatalog vom '\
 + COMMIT_DATE_A + ' gegenüber ' + COMMIT_DATE_B)
for c_id in CA_A:
    if (uuid := CA_A[c_id].get('alt-identifier', '')) in UUID_A_OHNE_B:
        report.append('#### 🗑 ' + uuid)
        report.append(c_id + ' ' + CA_A[c_id].get('title', '') + ' (' + CA_A[c_id].get('sec_level', '') + ')')
        report.append(control_titel_prose_params(CA_A, c_id, False))

# --------------- Neue Anforderungen-UUID ---------------------
report.append('## Neue Anforderungen-UUID')
report.append('[Zurück zu Inhalte](#inhalte)')

report.append(str(len(UUID_B_OHNE_A)) + ' neue Anforderungen-UUID in Anwenderkatalog vom '\
 + COMMIT_DATE_B + ' gegenüber ' + COMMIT_DATE_A)
for c_id in CA_B:
    if (uuid := CA_B[c_id].get('alt-identifier', '')) in UUID_B_OHNE_A:
        report.append('#### ✨ ' + uuid)
        report.append(c_id + ' ' + CA_B[c_id].get('title', '') + ' (' + CA_B[c_id].get('sec_level', '') + ')')
        report.append(control_titel_prose_params(CA_B, c_id, False))

#------------ Entfallene und neue Attribute jeder Anforderung ----------------
report.append('## Entfallene und neue Attribute der Anforderungen')
report.append('[Zurück zu Inhalte](#inhalte)')  

zeile = '\nEntfallene Attribute: '
if ATTRIBUTE_CA_A_OHNE_CA_B:
    zeile += ', '.join(ATTRIBUTE_CA_A_OHNE_CA_B)
else:
    zeile += '-'
report.append(zeile)

zeile = '\nNeue Attribute: '
if ATTRIBUTE_CA_B_OHNE_CA_A:
    zeile += ', '.join(ATTRIBUTE_CA_B_OHNE_CA_A)
else:
    zeile += '-'
report.append(zeile)
        
# --------------- Geänderte Anforderungen UUID ---------------------
report.append('## Anforderungen-UUID mit geaenderten Attributen')
report.append('[Zurück zu Inhalte](#inhalte)')  

# --------------- Übersicht: Anforderungen-UUID mit geänderten Attributen  ---------------------
report.append('### Anforderungen-UUID mit geaenderten Attributen - Uebersicht')
report.append('[Zurück zu Inhalte](#inhalte)') 

if delta_attribute:
    report.append('|Anforderung-UUID | Anforderung-ID(s)|Geänderte Attribute ' + \
    COMMIT_DATE_A + ' → ' + COMMIT_DATE_B + '|\n|---|---|---|')  
    for c_id_a in delta_attribute:                
        c_ids, uuid = c_id_a, delta_attribute[c_id_a]['uuid']
        if (c_id_a != (c_id_b := delta_attribute[c_id_a]['c_id_b'])):
            c_ids += ', ' + c_id_b
        report.append('|' + uuid + '|' + c_ids + '|' + \
        ', '.join(delta_attribute[c_id_a]['deltas']) + '|')
            
# --------------- Details: Anforderungen-UUID mit geänderten Attributen  ---------------------
report.append('### Anforderungen-UUID mit geaenderten Attributen - Details')
report.append('[Zurück zu Inhalte](#inhalte)') 

for c_id_a in delta_attribute:
    c_id_b, uuid = delta_attribute[c_id_a]['c_id_b'], delta_attribute[c_id_a]['uuid']    
    title_a, title_b = CA_A[c_id_a].get('title', ''), CA_B[c_id_b].get('title', '')
    sec_level_a, sec_level_b = CA_A[c_id_a].get('sec_level', ''), CA_B[c_id_b].get('sec_level', '')
    report.append('#### Δ ' + uuid)
    if ((c_id_a == c_id_b) and (title_a == title_b) and (sec_level_a == sec_level_b)): 
        report.append(COMMIT_DATE_A + ', ' + COMMIT_DATE_B + ': ' + c_id_a + ' ' + title_a + ' (' + sec_level_a + ')')        
    else:
        report.append(COMMIT_DATE_A + ': ' + c_id_a + ' ' + title_a + ' (' + sec_level_a + ')')
        report.append(COMMIT_DATE_B + ': ' + c_id_b + ' ' + title_b + ' (' + sec_level_b + ')')        
    report.append('||||')
    report.append('|---|---|---|')
    report.append('|*Attribut*|*' + COMMIT_DATE_A + '*|*' + COMMIT_DATE_B + '*|')    
    for attr_xlsx in delta_attribute[c_id_a]['deltas']:
        attr_oscal = CONTROL_ATTRIBUTES_DICT_XLSX[attr_xlsx]
        str_a, str_b = str(CA_A[c_id_a][attr_oscal]), str(CA_B[c_id_b][attr_oscal])
        if attr_oscal == 'guidance':
            str_a, str_b = inline_diff(str_a, str_b)
        report.append('|' + attr_xlsx + '|' + str_a + '|' + str_b + '|')

report.append('\n[Zurück zu Inhalte](#inhalte)')        

with open(PATH_DIFF_REPORT_UUID_CENTRIC, "w", encoding='utf-8') as f:
    f.write('    \n'.join(report))


