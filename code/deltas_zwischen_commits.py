# Stand 17.03.2026
import re
from helper_functions import inline_diff, kosinus_aehnlichkeit, read_json_file, replace_odd, sort_list_naturally, strings_broadly_similar, string_in_list_of_strings, teilstrings, ymd2dmy
from collections import defaultdict, OrderedDict
from configparser import ConfigParser
from itertools import product

# Regulaere Ausdruecke, https://regex101.com/
# Markdown https://www.markdownguide.org

config = ConfigParser()
config.read('config.ini')

CONTROL_ATTRIBUTES_DICT_OSCAL = dict(([key, config['control_attributes'][key]]) for key in config['control_attributes'])
CONTROL_ATTRIBUTES_DICT_XLSX = {v: k for k, v in CONTROL_ATTRIBUTES_DICT_OSCAL.items()}
    
PATH_CONTROL_ATTRIBUTES_A = config['orte']['path_control_attributes_a']
PATH_CONTROL_ATTRIBUTES_B = config['orte']['path_control_attributes_b']
PATH_DIFF_REPORT = config['orte']['path_diff_report']

CA_A = read_json_file(PATH_CONTROL_ATTRIBUTES_A)
CA_B = read_json_file(PATH_CONTROL_ATTRIBUTES_B)
COMMIT_A = config['orte']['COMMIT_A']
COMMIT_DATE_A = ymd2dmy(COMMIT_A)
COMMIT_B = config['orte']['COMMIT_B']
COMMIT_DATE_B = ymd2dmy(COMMIT_B)
RE_PREFIX_PARAMETER = r'{{\s*insert\s*:\s*param,\s*'
RE_SUFFIX_PARAMETER = r'\s*}}'

CA_A_OHNE_CA_B = sort_list_naturally(list(set(CA_A) - set(CA_B))) # entfernte Anforderungen
CA_B_OHNE_CA_A = sort_list_naturally(list(set(CA_B) - set(CA_A))) # neue Anforderungen
CA_A_UND_CA_B = sort_list_naturally(list(set(CA_A) & set(CA_B))) # beibehaltene Anforderungen

SCHWELLE_AEHNLICHKEIT = 0.5

def control_prose_mit_parameter(prose, parameter):
    if parameter:
        mystr = re.sub(RE_PREFIX_PARAMETER, '', prose)
        mystr = re.sub(RE_SUFFIX_PARAMETER, '', mystr)        
        for parameter_id, parameter_wert in parameter:
            mystr = re.sub(parameter_id.strip(), '{' + parameter_wert.strip() + '}', mystr)
        return mystr
    else:
        return prose

report = []
report.append('# GS++ control deltas github ' + COMMIT_DATE_A + ' & ' + COMMIT_DATE_B)
report.append('## Inhalte')
report.append('- [Entfernte Anforderungen](#entfernte-anforderungen)')
report.append('- [Neue Anforderungen](#neue-anforderungen)')
report.append('- [Veränderte Anforderungsattribute](#veränderte-anforderungsattribute)')
if CA_A_OHNE_CA_B and CA_B_OHNE_CA_A: #es gibt entfernte und neue Anforderungen
    report.append('\nZu jeder entfernten Anforderungen wird die neue Anforderung mit der höchsten [Kosinus-Ähnlichkeit](https://de.wikipedia.org/wiki/Kosinus-%C3%84hnlichkeit) (cos-sim) genannt, wenn diese ≥ ' + str(SCHWELLE_AEHNLICHKEIT) + ' ist. Unberücksichtigt bleiben bei der cos-sim-Berechnung Interpunktion, einige [Stoppwörter](https://de.wikipedia.org/wiki/Stoppwort), Wortreihenfolge sowie Groß- und Kleinschreibung.')

# --------------- Entfernte Anforderungen --------------------------------
report.append('## Entfernte Anforderungen')
report.append('[Zurück zu Inhalte](#inhalte)')
report.append('Anzahl entfernter Anforderungen: ' + str(len(CA_A_OHNE_CA_B)))
for c_id in CA_A_OHNE_CA_B:        
    zeile = '#### - ' + c_id + ' ' + CA_A[c_id]['title']
    if CA_A[c_id]['sec_level']: 
        zeile += ' (' + CA_A[c_id]['sec_level'] + ')'    
    report.append(zeile)
    if CA_A[c_id]['params']: 
        report.append(control_prose_mit_parameter(CA_A[c_id]['prose'], CA_A[c_id]['params'].items()))
    else: 
        report.append(CA_A[c_id]['prose'])
        
    if CA_A_OHNE_CA_B and CA_B_OHNE_CA_A: 
        zeile = '\nÄhnlich zu neuer Anforderung: '
        str_a = CA_A[c_id]['title'] + CA_A[c_id]['prose']         
        aehnlichkeit = 0
        for c_id_neu in CA_B_OHNE_CA_A:
            str_b = CA_B[c_id_neu]['title'] + CA_B[c_id_neu]['prose'] 
            if (neuer_wert := round(kosinus_aehnlichkeit(str_a, str_b),2)) > aehnlichkeit:
                c_id_aehnlich = c_id_neu
                aehnlichkeit = neuer_wert            
        if aehnlichkeit >= SCHWELLE_AEHNLICHKEIT:
            report.append('\n cos-sim ' + str(aehnlichkeit) + ' zu *+' + c_id_aehnlich + ' ' + CA_B[c_id_aehnlich]['title'] + '*')
            report.append('*' + CA_B[c_id_aehnlich]['prose'] + '*')

# --------------- Neue Anforderungen --------------------------------
report.append('## Neue Anforderungen')
report.append('[Zurück zu Inhalte](#inhalte)')
report.append('Anzahl neuer Anforderungen: ' + str(len(CA_B_OHNE_CA_A)))
for c_id in CA_B_OHNE_CA_A:        
    zeile = '#### + ' + c_id + ' ' + CA_B[c_id]['title']
    if CA_B[c_id]['sec_level']: 
        zeile += ' (' + CA_B[c_id]['sec_level'] + ')'
    report.append(zeile) 
    if CA_B[c_id]['params']: 
        report.append(control_prose_mit_parameter(CA_B[c_id]['prose'], CA_B[c_id]['params'].items()))
    else: 
        report.append(CA_B[c_id]['prose'])

# --------------- Übersicht Veränderte Anforderungsattribute --------------------------------    
report.append('## Veränderte Anforderungsattribute')
report.append('[Zurück zu Inhalt](#inhalte)')
diff_attr = defaultdict(dict)
veraenderte_anforderungsattribute = False
veraenderte_anforderungsattribute_anzahl = 0

for c_id in CA_A_UND_CA_B:
    diff_attr[c_id]['oscal_name'], diff_attr[c_id]['xlsx_name'] = [], []     
    for c_at in  CONTROL_ATTRIBUTES_DICT_OSCAL.keys():                    
        str_a = str(CA_A.get(c_id, {}).get(c_at, ''))
        str_b = str(CA_B.get(c_id, {}).get(c_at, ''))
        if not strings_broadly_similar(str_a, str_b, r'[-_:;,\.\s]+'):    
            diff_attr[c_id]['xlsx_name'].append(CONTROL_ATTRIBUTES_DICT_OSCAL[c_at])          
            diff_attr[c_id]['oscal_name'].append(c_at)
            veraenderte_anforderungsattribute = True
            veraenderte_anforderungsattribute_anzahl += 1
if veraenderte_anforderungsattribute:
    report.append('Anzahl geänderter Anforderungsattribute: ' + str(veraenderte_anforderungsattribute_anzahl) )
    report.append('|Anforderung|Geänderte Attribute|\n|---|---|')    
    for c_id in diff_attr: 
        if diff_attr[c_id]['xlsx_name']: 
            report.append('|' + c_id + '|' + ', '.join(sort_list_naturally(diff_attr[c_id]['xlsx_name'])) + '|')
else:
    report.append('Keine')

# --------------- Im Detail Veränderte Anforderungsattribute -------------------------------- 
for c_id in diff_attr:        
    if diff_attr[c_id]['xlsx_name']:
        report.append('#### ' + c_id + ' ' + CA_B[c_id]['title'] + ' (' + CA_B[c_id]['sec_level'] + ')') 
        report.append('|Attribut|' + COMMIT_DATE_A + '|' + COMMIT_DATE_B + '|\n|---|---|---|')
        for attr_xlsx in sort_list_naturally(diff_attr[c_id]['xlsx_name']):
            attr_oscal = CONTROL_ATTRIBUTES_DICT_XLSX[attr_xlsx]
            str_a, str_b = str(CA_A[c_id][attr_oscal]), str(CA_B[c_id][attr_oscal])
            if attr_oscal == 'guidance':
                str_a, str_b = inline_diff(str_a, str_b)            
            report.append('|' + attr_xlsx + '|' + str_a + '|' + str_b + '|')    

# --------------- Scheibe Datei -----------------------------------------        
with open(PATH_DIFF_REPORT, "w", encoding='utf-8') as f:
    f.write('    \n'.join(report))



    
