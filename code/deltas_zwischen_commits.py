'''
deltas_zwischen_commits.py - Unterschiede zwischen zwei GSpp-Anwenderkatalog-commits 

Erzeugt die Datei diff-report-gs++-<datum a>-<datum b>.md im Markdown-Format mit:

1) Anforderungen-IDs in commit A, die es in commit B nicht mehr gibt
   - Auch Nennung der commit B Anforderungen UUID, die identisch zu den entfernten commit A Anforderungen UUID sind
   - Auch Nennung der commit B Anforderungen, die den entfernten
     commit A Anforderungen inhaltlich ählich sind (wenn das Maß [Kosinus-Ähnlichkeit](https://de.wikipedia.org/wiki/Kosinus-%C3%84hnlichkeit) > 0,5)
   Dies sind Indikatoren, dass die Inhalte zu entfernten commit A Anforderungen-IDs in commit B Anforderungen weiter vorliegen.

2) Anforderungen-IDs in commit B, die es in commit A noch nicht gegeben hat  
   - Auch Nennung der commit A Anforderungen UUID, die identisch zu den neuen commit B Anforderungen UUID sind
   - Auch Nennung der commit A Anforderungen, die den neuen
     commit B Anforderungen inhaltlich ähnlich sind (wenn das Maß  Kosinus-Ähnlichkeit > 0,5)
   Dies sind Indikatoren, dass die Inhalte zu neuen commit B Anforderungen-IDs bereits in A Anforderungen vorlagen.

3) Veränderte Anforderungsattribute als Übersicht und im Detail. Beim Attribut "guidance" werden entfernte und ergänzte Textanteile hervorgehoben.  

Die Datumsangaben für commit A und commit B müssen in der config.ini Datei gesetzt werden.
'''

# Stand 08.06.2026
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
PATH_DIFF_REPORT = config['orte']['path_diff_report']

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


SCHWELLE_AEHNLICHKEIT = 0.5

# str_a = CA_A[c_id]['title'] + control_prose_mit_parameter(CA_A[c_id]['prose'], CA_A[c_id]['params'].items())

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

def aehnliche_control(control_id_a, control_attributes_a, control_attributes_b):
    '''
    '''
    str_a = control_titel_prose_params(control_attributes_a, control_id_a)    
    aehnlichkeit = 0
    for c_id_b in control_attributes_b:
        str_b = control_titel_prose_params(control_attributes_b, c_id_b)        
        #if (neuer_wert := round(kosinus_aehnlichkeit(str_a, str_b),2)) > aehnlichkeit:
        if (neuer_wert := kosinus_aehnlichkeit(str_a, str_b)) > aehnlichkeit:
            c_id_aehnlich = c_id_b
            aehnlichkeit = neuer_wert
    return c_id_aehnlich, round(aehnlichkeit,2)

report = []
report.append('# GS++ control deltas github ' + COMMIT_DATE_A + ' & ' + COMMIT_DATE_B)
report.append('## Inhalte')
report.append('- [Entfernte Anforderungen](#entfernte-anforderungen)')
report.append('- [Neue Anforderungen](#neue-anforderungen)')
report.append('- [Veränderte Anforderungsattribute](#veraenderte-anforderungsattribute)')
if (CA_A_OHNE_CA_B or CA_B_OHNE_CA_A): #es gibt entfernte oder neue Anforderungen
    zeile = '\nAls Maß für die Ähnlichkeit zwischen Anforderungen wird die  [Kosinus-Aehnlichkeit](https://de.wikipedia.org/wiki/Kosinus-%C3%84hnlichkeit) (cos-sim) verwendet.' 
    report.append(zeile)
    #report.append('\nÄhnlichkeiten zwischen Anforderungen werden mit dem Maß der [Kosinus-Aehnlichkeit](https://de.wikipedia.org/wiki/Kosinus-%C3%84hnlichkeit) ausgedrückt, wenn diese ≥ ' + str(SCHWELLE_AEHNLICHKEIT) + ' ist. Der maximal mögliche Wert von 1 steht für Gleichheit. Unberücksichtigt bleiben dabei Interpunktion, einige [Stoppwoerter](https://de.wikipedia.org/wiki/Stoppwort), Wortreihenfolge sowie Groß- und Kleinschreibung.')
    

# --------------- Entfernte Anforderungen --------------------------------
report.append('## Entfernte Anforderungen')
report.append('[Zurück zu Inhalte](#inhalte)')
report.append('Anzahl entfernter Anforderungen: ' + str(len(CA_A_OHNE_CA_B)))
for c_id in CA_A_OHNE_CA_B:        
    zeile = '#### 🗑 ' + c_id + ' ' + CA_A[c_id]['title']
    if CA_A[c_id]['sec_level']: 
        zeile += ' (' + CA_A[c_id]['sec_level'] + ')'    
    report.append(zeile)   
    report.append(control_titel_prose_params(CA_A, c_id, False))
        
    if (c_id_uuid := CA_A[c_id]['alt-identifier']) in MAP_UUID_CONTROL_ID_B:     
        c_id_b = MAP_UUID_CONTROL_ID_B[c_id_uuid]
        
        zeile = '\n' + c_id + ' UUID vom ' + COMMIT_DATE_A + ' ist gleich ' + c_id_b + ' UUID vom ' + COMMIT_DATE_B       
        str_a, str_b = control_titel_prose_params(CA_A, c_id), control_titel_prose_params(CA_B, c_id_b)
        zeile += '; cos-sim = ' + str(round(kosinus_aehnlichkeit(str_a,str_b),2))
        report.append(zeile)
        
        zeile = '\n *' + c_id_b + ' ' + CA_B[c_id_b].get('title', '') + ' (' + CA_B[c_id_b].get('sec_level', '') + ')*' ' vom ' + COMMIT_DATE_B 
        report.append(zeile)
        
        zeile = '*' + control_titel_prose_params(CA_B, c_id_b, False) + '*'        
        report.append(zeile)        
    
    
# --------------- Neue Anforderungen --------------------------------
report.append('## Neue Anforderungen')
report.append('[Zurück zu Inhalte](#inhalte)')
report.append('Anzahl neuer Anforderungen: ' + str(len(CA_B_OHNE_CA_A)))
for c_id in CA_B_OHNE_CA_A:        
    zeile = '#### ✨ ' + c_id + ' ' + CA_B[c_id]['title']
    if CA_B[c_id]['sec_level']: 
        zeile += ' (' + CA_B[c_id]['sec_level'] + ')'
    report.append(zeile) 
    report.append(control_titel_prose_params(CA_B, c_id, False))
        
    if (c_id_uuid := CA_B[c_id]['alt-identifier']) in MAP_UUID_CONTROL_ID_A:     
        c_id_a = MAP_UUID_CONTROL_ID_A[c_id_uuid]
        zeile = '\n' + c_id + ' UUID vom ' + COMMIT_DATE_B + ' ist gleich ' + c_id_a + ' UUID vom ' + COMMIT_DATE_A
        str_a, str_b = control_titel_prose_params(CA_A, c_id_a), control_titel_prose_params(CA_B, c_id)    
        zeile += '; cos-sim = ' + str(round(kosinus_aehnlichkeit(str_a,str_b),2))
        report.append(zeile)     

        zeile = '\n *' + c_id_a + ' ' + CA_A[c_id_a].get('title', '') + ' (' + CA_A[c_id_a].get('sec_level', '') + ')*' ' vom ' + COMMIT_DATE_A 
        report.append(zeile)     

        zeile = '*' + control_titel_prose_params(CA_A, c_id_a, False) + '*'        
        report.append(zeile) 
              
    

# --------------- Übersicht Veränderte Anforderungsattribute --------------------------------    
report.append('## Veraenderte Anforderungsattribute')
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
            if attr_oscal == 'alt-identifier' and (str_a in MAP_UUID_CONTROL_ID_B):
                str_a += '<br>(gleicht ' + MAP_UUID_CONTROL_ID_B[str_a] + ' UUID vom ' + COMMIT_DATE_B + ')'                
            if attr_oscal == 'alt-identifier' and (str_b in MAP_UUID_CONTROL_ID_A):                
                str_b += '<br>(gleicht ' + MAP_UUID_CONTROL_ID_A[str_b] + ' UUID vom ' + COMMIT_DATE_A + ')'                   
            report.append('|' + attr_xlsx + '|' + str_a + '|' + str_b + '|')    

# --------------- Scheibe Datei -----------------------------------------        
with open(PATH_DIFF_REPORT, "w", encoding='utf-8') as f:
    f.write('    \n'.join(report))



    
