# Stand 05.07.2026
import re
from helper_functions import inline_diff, kosinus_aehnlichkeit, read_json_file, replace_odd, sort_list_naturally, strings_broadly_similar, string_in_list_of_strings, teilstrings, ymd2dmy
from collections import defaultdict, OrderedDict
from configparser import ConfigParser, ExtendedInterpolation
from itertools import product

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

CA_A_OHNE_CA_B = sort_list_naturally(list(set(CA_A) - set(CA_B))) # entfernte Anforderungen
CA_B_OHNE_CA_A = sort_list_naturally(list(set(CA_B) - set(CA_A))) # neue Anforderungen
CA_A_UND_CA_B = sort_list_naturally(list(set(CA_A) & set(CA_B))) # beibehaltene Anforderungen

MAP_UUID_CONTROL_ID_A = {CA_A[k]['alt-identifier']: k for k in CA_A}
MAP_UUID_CONTROL_ID_B = {CA_B[k]['alt-identifier']: k for k in CA_B}



UUID_A_OHNE_B = set(MAP_UUID_CONTROL_ID_A.keys()) - set(MAP_UUID_CONTROL_ID_B.keys())
UUID_B_OHNE_A = set(MAP_UUID_CONTROL_ID_B.keys()) - set(MAP_UUID_CONTROL_ID_A.keys())
UUID_A_UND_B = set(MAP_UUID_CONTROL_ID_A.keys()) & set(MAP_UUID_CONTROL_ID_B.keys())

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


def deltas(ca_a, ca_b, c_id_a, c_id_b):    
    ca_a_ohne_b_keys = {key for key in (set(ca_a[c_id_a].keys()) -\
    set(ca_b[c_id_b].keys())) if ca_a[c_id_a][key]}
    
    ca_b_ohne_a_keys = {key for key in (set(ca_b[c_id_b].keys()) -\
    set(ca_a[c_id_a].keys())) if ca_b[c_id_b][key]}
    
    ca_a_und_b_keys = {key for key in (set(ca_a[c_id_a].keys()) & \
    set(ca_b[c_id_b].keys())) if (ca_a[c_id_a][key] != ca_b[c_id_b][key])}    
    
    return  list(ca_a_ohne_b_keys | ca_b_ohne_a_keys | ca_a_und_b_keys)


# ----------- Ermittle Anzahl von Anforderungen mit geänderten Attributen
anzahl_anf_mit_delta_attr, anzahl_delta_attr = 0, 0
for c_id_a in CA_A: 
    if ((uuid := CA_A[c_id_a].get('alt-identifier', '')) in UUID_A_UND_B) and \
    (c_id_b := MAP_UUID_CONTROL_ID_B[uuid]) and (CA_A[c_id_a] != CA_B[c_id_b]):   
        anzahl_anf_mit_delta_attr += 1
        anzahl_delta_attr += len(deltas(CA_A, CA_B, c_id_a, c_id_b))


# ---------- Inhaltsverzeichnis
report = []
report.append('# GS++ control deltas github ' + COMMIT_DATE_A + ' & ' + COMMIT_DATE_B)
report.append('## Inhalte')

report.append('- [' + str(len(UUID_A_OHNE_B)) + ' entfernte Anforderungen-UUID](#entfernte-anforderungen-uuid)    ')
report.append('- [' + str(len(UUID_B_OHNE_A)) + ' neue Anforderungen-UUID](#neue-anforderungen-uuid)    ')
report.append('- [' + str(anzahl_anf_mit_delta_attr) + ' Anforderungen-UUID mit ' + str(anzahl_delta_attr) + ' geaenderten Attributen](#geaenderte-anforderungen-uuid)    ')
report.append('    - [Geaenderte Anforderungen-UUID Übersicht](#geaenderte-anforderungen-uuid---uebersicht)    ')
report.append('    - [Geaenderte Anforderungen-UUID Details](#geaenderte-anforderungen-uuid---details)    ')

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
        
# --------------- Geänderte Anforderungen UUID ---------------------
report.append('## Geaenderte Anforderungen-UUID')
report.append('[Zurück zu Inhalte](#inhalte)')  
report.append(str(anzahl_anf_mit_delta_attr) + ' Anforderungen-UUID mit ' + str(anzahl_delta_attr) + ' geänderten Attributen')

# --------------- Geänderte Anforderungen UUID Übersicht ---------------------
report.append('## Geaenderte Anforderungen-UUID - Uebersicht')
report.append('[Zurück zu Inhalte](#inhalte)') 
tabellenkopf = False
for c_id_a in CA_A: 
    if ((uuid := CA_A[c_id_a].get('alt-identifier', '')) in UUID_A_UND_B) and \
    (c_id_b := MAP_UUID_CONTROL_ID_B[uuid]) and (CA_A[c_id_a] != CA_B[c_id_b]):        
        if not tabellenkopf:
            report.append('|UUID | Anforderung-ID(s)|Geänderte Attribute ' + \
            COMMIT_DATE_A + ' → ' + COMMIT_DATE_B + '|\n|---|---|---|')  
            tabellenkopf = True     
        c_ids = c_id_a    
        if (c_id_a != c_id_b):
            c_ids += ', ' + c_id_b        
        deltas_attributes_oscal = deltas(CA_A, CA_B, c_id_a, c_id_b)
        deltas_attributes_xlsx = sort_list_naturally([CONTROL_ATTRIBUTES_DICT_OSCAL[entry] for entry in deltas_attributes_oscal])
        report.append('|' + uuid + '|' + c_ids + '|' + ', '.join(deltas_attributes_xlsx) + '|')
if not tabellenkopf:
    report.append('Keine')

# --------------- Geänderte Anforderungen UUID Details ---------------------
report.append('## Geaenderte Anforderungen-UUID - Details')
report.append('[Zurück zu Inhalte](#inhalte)') 

for c_id_a in CA_A: 
    if ((uuid := CA_A[c_id_a].get('alt-identifier', '')) in UUID_A_UND_B) and \
    (c_id_b := MAP_UUID_CONTROL_ID_B[uuid]) and (CA_A[c_id_a] != CA_B[c_id_b]):   
        text_kopfbereich = False
        deltas_attributes_oscal = deltas(CA_A, CA_B, c_id_a, c_id_b)
        deltas_attributes_xlsx = sort_list_naturally([CONTROL_ATTRIBUTES_DICT_OSCAL[entry] for entry in deltas_attributes_oscal])
        for attr_xlsx in deltas_attributes_xlsx:
            attr_oscal = CONTROL_ATTRIBUTES_DICT_XLSX[attr_xlsx]
            str_a, str_b = str(CA_A[c_id_a].get(attr_oscal, '-')), str(CA_B[c_id_b].get(attr_oscal, '-'))                    
                
            if not text_kopfbereich:
                if ((uuid := CA_A[c_id_a].get('alt-identifier', '')) in UUID_A_UND_B) and \
                (c_id_b := MAP_UUID_CONTROL_ID_B[uuid]) and (CA_A[c_id_a] != CA_B[c_id_b]):   
                    report.append('#### Δ ' + uuid)
                    report.append(COMMIT_DATE_A + ' ' + c_id_a + ' ' + CA_A[c_id_a].get('title', '')\
                    + ' (' + CA_A[c_id_a].get('sec_level', '') + ')')
                    report.append(COMMIT_DATE_B + ' ' + c_id_b + ' ' + CA_B[c_id_b].get('title', '')\
                    + ' (' + CA_B[c_id_b].get('sec_level', '') + ')')
                    report.append('|Attribut|' + COMMIT_DATE_A + '|' + COMMIT_DATE_B + '|\n|---|---|---|')
                text_kopfbereich = True

            if attr_oscal == 'guidance':
                str_a, str_b = inline_diff(str_a, str_b)
            report.append('|' + attr_xlsx + '|' + str_a + '|' + str_b + '|')

report.append('[Zurück zu Inhalte](#inhalte)') 

# --------------- Scheibe Datei -----------------------------------------        
with open(PATH_DIFF_REPORT_UUID_CENTRIC, "w", encoding='utf-8') as f:
    f.write('    \n'.join(report))

