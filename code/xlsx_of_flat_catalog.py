#Stand 11.07.2026
import math, re, xlsxwriter #https://xlsxwriter.readthedocs.io/
from helper_functions import decode_config_escapes, read_json_file, sort_list_naturally, today, ymd2dmy
from collections import defaultdict
from configparser import ConfigParser, ExtendedInterpolation

# Regulaere Ausdruecke, https://regex101.com/
RE_PREFIX_PARAMETER = r'{{\s*insert\s*:\s*param,\s*'
RE_SUFFIX_PARAMETER = r'\s*}}'

# Format Excel-Tabellen
HEADER_FORMAT = {"text_wrap":True, "align":"left", "valign":"top", "bold":True, "border":1, 'locked':True}      
CELL_FORMAT = {"text_wrap":True, "align":"left", "valign":"top", "border":1}
KOMMENTAR_GROESSE = {'width': 420, 'height': 320}

config = ConfigParser(interpolation = ExtendedInterpolation())
config.read('config.ini')

DATUM_CATALOG_GITHUB_COMMIT = config['DEFAULT']['commit']

try:
    KONTAKT = config['DEFAULT']['kontakt']
except:
    KONTAKT = ''
PATH_CONTROL_ATTRIBUTES = config['orte']['path_CONTROL_ATTRIBUTES']
PATH_CATALOG_XLSX = config['orte']['path_catalog_xlsx']
PATH_IMPLEMENTATIONS = config['orte']['path_catalog_implementations']
PATH_GITHUB_BSI_GSPP_CATALOG = config['orte']['path_github_bsi_gspp_catalog']
PATH_GITHUB_BSI_GSPP_IMPLEMENTIERUNGEN = config['orte']['path_github_bsi_gspp_implementierungen']
PATH_GITHUB_BSI_GSPP_NAMESPACE_DEFINITIONEN = config['orte']['path_github_bsi_gspp_namespace_definitionen']
PATH_GITHUB_VORGEBIRGE_GSPP = config['orte']['path_github_vorgebirge_gspp']
try:
    PATH_LOGO = config['orte']['path_logo']
except:
    PATH_LOGO = ''

CONTROL_ATTRIBUTES = read_json_file(PATH_CONTROL_ATTRIBUTES)
IMPLEMENTATIONS = read_json_file(PATH_IMPLEMENTATIONS)

CATALOG_COLUMN = defaultdict(dict)
IMPLEMENTATION_COLUMN = defaultdict(dict)

for section in config.sections():    
    if (config[section].get('section_type', '') == 'xlsx') and (config[section].get('sheet', '') == 'katalog'):            
        function = config[section].get('function', '')        
        CATALOG_COLUMN[function]['cell_value_type'] = config[section].get('cell_value_type', '')
        CATALOG_COLUMN[function]['comment'] = decode_config_escapes(config[section].get('comment', ''))        
        CATALOG_COLUMN[function]['headline'] = decode_config_escapes(config[section].get('headline', ''))
        CATALOG_COLUMN[function]['hidden'] = config.getboolean(section, 'hidden')
        CATALOG_COLUMN[function]['is_in_sheet'] = config.getboolean(section, 'is_in_sheet')
        CATALOG_COLUMN[function]['level'] = config.getint(section, 'level')
        CATALOG_COLUMN[function]['sheet'] = config[section].get('sheet', '')
        CATALOG_COLUMN[function]['width'] = config.getint(section, 'width')
    elif (config[section].get('section_type', '') == 'xlsx') and (config[section].get('sheet', '') == 'implementierung'):            
        function = config[section].get('function', '')        
        IMPLEMENTATION_COLUMN[function]['cell_value_type'] = config[section].get('cell_value_type', '')
        IMPLEMENTATION_COLUMN[function]['comment'] = decode_config_escapes(config[section].get('comment', ''))        
        IMPLEMENTATION_COLUMN[function]['headline'] = decode_config_escapes(config[section].get('headline', ''))
        IMPLEMENTATION_COLUMN[function]['hidden'] = config.getboolean(section, 'hidden')
        IMPLEMENTATION_COLUMN[function]['is_in_sheet'] = config.getboolean(section, 'is_in_sheet')
        IMPLEMENTATION_COLUMN[function]['level'] = config.getint(section, 'level')
        IMPLEMENTATION_COLUMN[function]['sheet'] = config[section].get('sheet', '')
        IMPLEMENTATION_COLUMN[function]['width'] = config.getint(section, 'width')

def control_text_with_parameter(control_id: str) -> str:
    result = CONTROL_ATTRIBUTES[control_id].get('prose', '')
    if CONTROL_ATTRIBUTES[control_id].get('params', ''):        
        result = re.sub(RE_PREFIX_PARAMETER, '', result)
        result = re.sub(RE_SUFFIX_PARAMETER, '', result)        
        for parameter_id, parameter_content in CONTROL_ATTRIBUTES[control_id]['params'].items():
            result = re.sub(parameter_id.strip(), '{' + parameter_content.strip() + '}', result)
    return result
    
def abhaengigkeit(control_id: str) -> str:    
    return CONTROL_ATTRIBUTES[control_id]['required']

def alt_identifier(control_id: str) -> str:    
    return CONTROL_ATTRIBUTES[control_id]['alt-identifier']

def anforderung(control_id: str) -> str:
    return control_id + ' ' + CONTROL_ATTRIBUTES[control_id]['title']
    
def anforderung_id(control_id: str) -> str:
    return control_id

def anforderung_status(control_id: str) -> str:
    return ''

def anforderung_titel_ohne_id(control_id: str) -> str:
    return CONTROL_ATTRIBUTES[control_id]['title']

def anforderung_titel_und_text(control_id: str) -> str:    
    ergebnis = CONTROL_ATTRIBUTES[control_id]['title']
    ergebnis += '\n\n' + control_text_with_parameter(control_id)    
    return ergebnis

def anmerkungen(control_id: str) -> str:
    return ''    

def aufwand(control_id: str) -> str:    
    return CONTROL_ATTRIBUTES[control_id]['effort_level']

def dokumentation(control_id: str) -> str:
    return CONTROL_ATTRIBUTES[control_id]['documentation']
  
def elementare_gefaehrdung(control_id: str) -> str:
    mystr, mylist = CONTROL_ATTRIBUTES[control_id]['threats'], []        
    mylist.extend(item.strip() for item in mystr.split(',') if item.strip())
    return ', '.join(sort_list_naturally(mylist))    
  
def ergebnis(control_id: str) -> str:
    return CONTROL_ATTRIBUTES[control_id]['result']

def guidance(control_id: str) -> str:
    return CONTROL_ATTRIBUTES[control_id]['guidance']

def handlung(control_id: str) -> str:
    return CONTROL_ATTRIBUTES[control_id]['action_word'] 

def implementierung_commit_source(control_id: str) -> str:
    global list_index    
    return IMPLEMENTATIONS[control_id][list_index].get('commit_source', '-')

def implementierung_description(control_id: str) -> str:
    global list_index    
    return IMPLEMENTATIONS[control_id][list_index].get('description', '-')
    
def implementierung_remarks(control_id: str) -> str:
    global list_index    
    return IMPLEMENTATIONS[control_id][list_index].get('remarks', '-')

def implementierung_source(control_id: str) -> str:
    global list_index    
    return IMPLEMENTATIONS[control_id][list_index].get('source', '-')

def implementierung_uuid(control_id: str) -> str:
    global list_index    
    return IMPLEMENTATIONS[control_id][list_index].get('uuid', '-')

def klasse(control_id: str) -> str:
    return CONTROL_ATTRIBUTES[control_id]['class']

def link_anforderung_id(control_id: str) -> str:
    global sheet_catalog_name    
    destination, string = '', ''
    destination_row = list(CONTROL_ATTRIBUTES).index(control_id) + 2                
    destination = 'internal:' + sheet_catalog_name + '!A' + str(destination_row)
    string = control_id
    return destination, string

def link_implementierung(control_id: str) -> str:    
    global sheet_implementation_name
    destination, string = '', ''
    if control_id in IMPLEMENTATIONS: 
        destination = 'internal:' + sheet_implementation_name + '!A' + str(IMPLEMENTATIONS[control_id][0]['excel_row']) 
        string = '→Impl. Zeile ' + str(IMPLEMENTATIONS[control_id][0]['excel_row'])  
        if len(IMPLEMENTATIONS[control_id]) > 1:
            string += '-' + str(IMPLEMENTATIONS[control_id][0]['excel_row'] + len(IMPLEMENTATIONS[control_id]) -1)
    return destination, string

def massnahmen_geplant(control_id: str) -> str:
    return ''

def massnahmen_umgesetzt(control_id: str) -> str:
    return ''

def modalverb(control_id: str) -> str:
    return CONTROL_ATTRIBUTES[control_id]['modal_verb']

def praezisierung(control_id: str) -> str:
    return CONTROL_ATTRIBUTES[control_id]['result_specification']

def praktik(control_id: str) -> str:    
    return CONTROL_ATTRIBUTES[control_id]['praktik']

def praktik_typ(control_id: str) -> str:
    return CONTROL_ATTRIBUTES[control_id]['praktik_typ']

def sicherheitsniveau(control_id: str) -> str:
    return CONTROL_ATTRIBUTES[control_id]['sec_level']

def sicherheitsziel_authentizitaet(control_id: str) -> str:
    return CONTROL_ATTRIBUTES[control_id]['authenticity']

def sicherheitsziel_integritaet(control_id: str) -> str:
    return CONTROL_ATTRIBUTES[control_id]['integrity']

def sicherheitsziel_verfuegbarkeit(control_id: str) -> str:
    return CONTROL_ATTRIBUTES[control_id]['availability']

def sicherheitsziel_vertraulichkeit(control_id: str) -> str:
    return CONTROL_ATTRIBUTES[control_id]['confidentiality']

def tags(control_id: str) -> str:
    return CONTROL_ATTRIBUTES[control_id]['tags']    

def text(control_id: str) -> str:        
    return control_text_with_parameter(control_id)

def thema(control_id: str) -> str:
    return CONTROL_ATTRIBUTES[control_id]['praktik_thema']

def verbesserung(control_id: str) -> str:
    return CONTROL_ATTRIBUTES[control_id]['verbesserung']

def verwandte(control_id: str) -> str:
    return CONTROL_ATTRIBUTES[control_id]['related']

def zielobjekte(control_id: str) -> str:
    return CONTROL_ATTRIBUTES[control_id]['target_object_categories']

def construct_sheet_rows(workbook, sheet_catalog, column_defintions):    
    header_format = workbook.add_format(HEADER_FORMAT)
           
    column = 0
    for key in column_defintions.keys():
        if not column_defintions[key]['is_in_sheet']: continue
        
        #setze die breite der spalten
        width  = column_defintions[key]['width']
        hidden  = column_defintions[key]['hidden']
        level = column_defintions[key]['level']              
        sheet_catalog.set_column(column, column, width, None, {'level': level,'hidden': hidden})            
        
        #schreibe Kopzzeile
        sheet_catalog.set_row(0, 30) 
        sheet_catalog.write_string(0, column, column_defintions[key]['headline'],header_format)
        
        #schreibe Kommentare    
        sheet_catalog.write_comment(0, column, column_defintions[key]['comment'], KOMMENTAR_GROESSE)
        
        column +=1

def construct_sheet_deckblatt(sheet_deckblatt):    
    if PATH_LOGO:
        sheet_deckblatt.insert_image(1, 0, PATH_LOGO)    
        row = 7
    else:
        row = 0
    
    cell_value = 'Stand: Erstellung Excel Datei ' + ymd2dmy(today()) + ' aus BSI GS++ Anwenderkatalog github commit ' +  ymd2dmy(DATUM_CATALOG_GITHUB_COMMIT)
    sheet_deckblatt.write_string(row,0, cell_value)
          
    sheet_deckblatt.write_string(row + 2,0, 'Vorliegende Excel-Datei:')
    sheet_deckblatt.write_url(row + 3,0, PATH_GITHUB_VORGEBIRGE_GSPP)
    
    sheet_deckblatt.write_string(row + 5,0, 'Zu Grunde liegender BSI GS++ Anwenderkatalog')
    sheet_deckblatt.write_url(row + 6,0, PATH_GITHUB_BSI_GSPP_CATALOG)
    
    sheet_deckblatt.write_string(row + 8,0, 'Zu Grunde liegende BSI GS++ Implementierungsbeschreibungen')
    sheet_deckblatt.write_url(row + 9,0, PATH_GITHUB_BSI_GSPP_IMPLEMENTIERUNGEN)

    sheet_deckblatt.write_string(row + 11,0, 'BSI Stand der Technik — Namespace-Definitionen / Vokabular')
    sheet_deckblatt.write_url(row + 12,0, PATH_GITHUB_BSI_GSPP_NAMESPACE_DEFINITIONEN)
    
    if KONTAKT:
        cell_value = 'Kontakt: ' + KONTAKT
        sheet_deckblatt.write_string(row + 11,0, cell_value)
   
            
def construct_sheet_row(workbook, sheet, column_defintions, row, control_id):            
    # Lege Format der Zeile fest     
    cell_format =  workbook.add_format(CELL_FORMAT)
    
    # Trage Spalteninhalte in Zellen ein
    column, row_height = 0, 0
    for key in column_defintions.keys():
        if not column_defintions[key]['is_in_sheet']: continue
        
        if column_defintions[key].get('cell_value_type','') == 'string': 
            cell_value = globals()[key](control_id)                        
            sheet.write_string(row, column, cell_value, cell_format)
        elif column_defintions[key].get('cell_value_type','') == 'url': 
            destination, cell_value = globals()[key](control_id)            
            sheet.write_url(row, column, destination, cell_format, cell_value)                   
            
        row_height = max([row_height, math.ceil(len(cell_value) / column_defintions[key]['width'])])
        column += 1
            
    # Lege Zeilenhöhe fest
    sheet.set_row(row, row_height*15)


def set_sheet_autofilter(rows, sheet, column_defintions):      
    columns = 0
    for key in column_defintions.keys():        
        if not column_defintions[key]['is_in_sheet']: continue    
        columns += 1    
    sheet.autofilter(0,0,rows - 1,columns - 1) 


def main():     
    global list_index, sheet_catalog_name, sheet_implementation_name
    # Öffne xlsx-datei         
    workbook = xlsxwriter.Workbook(PATH_CATALOG_XLSX)
        
    # Erstelle Tabellenbätter zu Deckblatt und den controls
    sheet_deckblatt = workbook.add_worksheet("Deckblatt")        
    
    sheet_catalog_name = 'Anforderungen'
    sheet_catalog = workbook.add_worksheet(sheet_catalog_name)
    sheet_catalog.freeze_panes(1,0) 
    
    sheet_implementation_name = 'Implementierungen'
    sheet_implementation = workbook.add_worksheet(sheet_implementation_name)
    sheet_implementation.freeze_panes(1,0)
    
    # Gestalte Deckblatt
    construct_sheet_deckblatt(sheet_deckblatt)
        
    #Gestalte Spalten im Tabellenblatt mit den controls
    construct_sheet_rows(workbook, sheet_catalog, CATALOG_COLUMN)    
    
    #Gestalte Spalten im Tabellenblatt mit den Implementierungen
    construct_sheet_rows(workbook, sheet_implementation, IMPLEMENTATION_COLUMN)    
        
    #gestalte Zeilen im Tabellenblatt mit den controls
    row = 0
    for control_id in CONTROL_ATTRIBUTES.keys():
        row += 1        
        construct_sheet_row(workbook, sheet_catalog, CATALOG_COLUMN, row, control_id)           
    # setze in jeder Spalte Autofilter
    set_sheet_autofilter(row, sheet_catalog, CATALOG_COLUMN)  
    
    #gestalte Zeilen im Tabellenblatt mit den Implementierungen
    row = 0    
    for control_id in CONTROL_ATTRIBUTES.keys():        
        if control_id in IMPLEMENTATIONS:        
            list_index = 0
            for implementation in IMPLEMENTATIONS[control_id]:                
                row += 1                        
                construct_sheet_row(workbook, sheet_implementation, IMPLEMENTATION_COLUMN, row, control_id)                          
                list_index += 1                
    # setze in jeder Spalte Autofilter
    set_sheet_autofilter(row, sheet_implementation, IMPLEMENTATION_COLUMN)
    
    # Schließe Datei
    workbook.close()


if __name__ == "__main__":
    main()
