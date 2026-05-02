#Stand 02.05.2026
import math, re, xlsxwriter #https://xlsxwriter.readthedocs.io/
from helper_functions import read_json_file, ymd2dmy
from collections import defaultdict
from configparser import ConfigParser

# Regulaere Ausdruecke, https://regex101.com/
RE_PREFIX_PARAMETER = r'{{\s*insert\s*:\s*param,\s*'
RE_SUFFIX_PARAMETER = r'\s*}}'

# Format Excel-Tabellen
HEADER_FORMAT = {"text_wrap":True, "align":"left", "valign":"top", "bold":True, "border":1, 'locked':True}      
CELL_FORMAT = {"text_wrap":True, "align":"left", "valign":"top", "border":1}
KOMMENTAR_GROESSE = {'width': 400, 'height': 300}

config = ConfigParser()
config.read('config.ini')
DATUM_ERSTELLUNG_XLSX = config['daten']['datum_erstellung_xlsx']
DATUM_CATALOG_GITHUB_COMMIT = config['orte']['commit']
try:
    KONTAKT = config['daten']['kontakt']
except:
    KONTAKT = ''
PATH_CONTROL_ATTRIBUTES = config['orte']['path_CONTROL_ATTRIBUTES']
PATH_CATALOG_XLSX = config['orte']['path_catalog_xlsx']
try:
    PATH_LOGO = config['orte']['path_logo']
except:
    PATH_LOGO = ''

CONTROL_ATTRIBUTES = read_json_file(PATH_CONTROL_ATTRIBUTES)

CATALOG_COLUMN = defaultdict(dict)

CATALOG_COLUMN['praktik']['headline'] = 'Praktik'
CATALOG_COLUMN['praktik']['is_in_sheet'] = True
CATALOG_COLUMN['praktik']['width'] = 20
CATALOG_COLUMN['praktik']['hidden'] = False
CATALOG_COLUMN['praktik']['level'] = 3
CATALOG_COLUMN['praktik']['comment'] = 'Praktiken (OSCAL Groups) sind die “Überschriften”, in die ein Katalog gegliedert ist. Gleichzeitig sind die Praktiken als Vorschläge für (Teil-)Prozesse des ISMS zu betrachten. Jede Praktik kann als eigenständiger, abgrenzbarer (Teil-)Prozess von größerem Umfang angesehen werden, der in einem ISMS zwingend erforderlich ist zur Erreichung der Schutzziele nach ISO/IEC 27001. Die Praktiken sind jedoch nicht gleichzusetzen mit inhaltlichen Geschäftsprozessen wie Finanzwesen oder Vertrieb.'

CATALOG_COLUMN['thema']['headline'] = 'Praktik\nThema'
CATALOG_COLUMN['thema']['is_in_sheet'] = True
CATALOG_COLUMN['thema']['width'] = 23
CATALOG_COLUMN['thema']['hidden'] = False
CATALOG_COLUMN['thema']['level'] = 3
CATALOG_COLUMN['thema']['comment'] = 'Themen (OSCAL Group in Group)sind die Untergruppen (“Unterüberschriften”) innerhalb einer Praktik und dienen der thematischen Zusammenfassung von Anforderungen, z.B. zum Management von Schwachstellen.'

CATALOG_COLUMN['praktik_typ']['headline'] = 'Praktik\nTyp'
CATALOG_COLUMN['praktik_typ']['is_in_sheet'] = True
CATALOG_COLUMN['praktik_typ']['width'] = 16
CATALOG_COLUMN['praktik_typ']['hidden'] = False
CATALOG_COLUMN['praktik_typ']['level'] = 3
CATALOG_COLUMN['praktik_typ']['comment'] = 'Praktiken lassen sich unterteilen in:\n- ISMS-Praktiken\n- Organisatorische Praktiken\n- Technische Praktiken\n\nDie ISMS-Praktiken sind übergreifend. Sie bauen einen Plan-Do-Check-Act-Zyklus (PDCA-Zyklus) des Managementsystems auf, der die fortlaufende Kontrolle und Verbesserung über alle Bereiche hinweg gewährleistet.\n\nDie Anforderungen der ISMS-Praktiken sind übergreifend und keiner einzelne Zielobjektkategorie zugewiesen. Sie bauen auf den PDCA-Zyklus des Managementsystems auf und gelten deshalb einmalig für den gesamten Informationsverbund.'

CATALOG_COLUMN['sicherheitsniveau']['headline'] = 'Anforderung\nSicherheitsniveau'
CATALOG_COLUMN['sicherheitsniveau']['is_in_sheet'] = True
CATALOG_COLUMN['sicherheitsniveau']['width'] = 18
CATALOG_COLUMN['sicherheitsniveau']['hidden'] = False
CATALOG_COLUMN['sicherheitsniveau']['level'] = 3
CATALOG_COLUMN['sicherheitsniveau']['comment'] = 'Klassifiziert das Sicherheitsniveau bei dem eine Anforderung relevant ist. Mögliche Werte sind normal-SdT für den normalen Stand der Technik oder erhöht für Anforderungen, für die eine individuelle Risikoanalyse erforderlich ist.'

CATALOG_COLUMN['modalverb']['headline'] = 'Anforderung\nModalverb'
CATALOG_COLUMN['modalverb']['is_in_sheet'] = True
CATALOG_COLUMN['modalverb']['width'] = 14
CATALOG_COLUMN['modalverb']['hidden'] = False
CATALOG_COLUMN['modalverb']['level'] = 3
CATALOG_COLUMN['modalverb']['comment'] = 'Das Modalverb einer Anforderung gibt an, welchen Pflichtcharakter sie hat, d.h. ob es sich um eine MUSS-, SOLLTE- oder KANN-Anforderung handelt. Für die Anforderungen gelten folgende Definitionen:\n\n- MUSS → verpflichtend, keine Abweichung erlaubt (entspricht „MUST“1).\n\n- SOLLTE → in der Regel verpflichtend, Abweichung in begründeten Ausnahmefällen möglich (entspricht „SHOULD“).\n\n- KANN → optional, je nach Situation sinnvoll, aber nicht notwendig (entspricht „MAY“).'

CATALOG_COLUMN['alt_identifier']['headline'] = 'Anforderung\nUUID'
CATALOG_COLUMN['alt_identifier']['is_in_sheet'] = True
CATALOG_COLUMN['alt_identifier']['width'] = 40
CATALOG_COLUMN['alt_identifier']['hidden'] = True
CATALOG_COLUMN['alt_identifier']['level'] = 3
CATALOG_COLUMN['alt_identifier']['comment'] = 'UUID: Über alle Kataloge und Katalogversionen hinweg eindeutige Identifikationsnummer der Anforderung. Diese folgt der Bedeutung der Anforderung, bleibt also auch bei bedeutungserhaltenden Umformulierungen oder Verschiebungen von Anforderungen gleich. Andererseits wird sie ersetzt, wenn sich die Bedeutung der Anforderung wesentlich verändert, selbst wenn ihre Stellung in der Struktur bleibt.'

CATALOG_COLUMN['anforderung_id']['headline'] = 'Anforderung\nID'
CATALOG_COLUMN['anforderung_id']['is_in_sheet'] = True
CATALOG_COLUMN['anforderung_id']['width'] = 14
CATALOG_COLUMN['anforderung_id']['hidden'] = False
CATALOG_COLUMN['anforderung_id']['level'] = 0
CATALOG_COLUMN['anforderung_id']['comment'] = 'ID: Eindeutiger Identifikator der Anforderung innerhalb der Praktik und des Themas im Format {Kürzel der Praktik}.{Nummerierung des Themas}.{Nummerierung der Anforderung}. Die ID ergibt sich also aus der Stellung der Anforderung innerhalb des Dokumentes.'

CATALOG_COLUMN['anforderung_titel_ohne_id']['headline'] = 'Anforderung\nTitel'
CATALOG_COLUMN['anforderung_titel_ohne_id']['is_in_sheet'] = True
CATALOG_COLUMN['anforderung_titel_ohne_id']['width'] = 20
CATALOG_COLUMN['anforderung_titel_ohne_id']['hidden'] = False
CATALOG_COLUMN['anforderung_titel_ohne_id']['level'] = 0
CATALOG_COLUMN['anforderung_titel_ohne_id']['comment'] = 'Titel: Titel der einzelnen Anforderung. Der Titel beschreibt eine Anforderung kurz und prägnant, so dass sie ohne Blick auf den vollständigen Anforderungsinhalt wiederzuerkennen ist. Titel sind nicht normativ.'

CATALOG_COLUMN['anforderung']['headline'] = 'Anforderung\nID und Titel'
CATALOG_COLUMN['anforderung']['is_in_sheet'] = False
CATALOG_COLUMN['anforderung']['width'] = 30
CATALOG_COLUMN['anforderung']['hidden'] = False
CATALOG_COLUMN['anforderung']['level'] = 0
CATALOG_COLUMN['anforderung']['comment'] = 'ID: Eindeutiger Identifikator der Anforderung innerhalb der Praktik und des Themas im Format {Kürzel der Praktik}.{Nummerierung des Themas}.{Nummerierung der Anforderung}. Die ID ergibt sich also aus der Stellung der Anforderung innerhalb des Dokumentes.\n\nTitel: Titel der einzelnen Anforderung. Der Titel beschreibt eine Anforderung kurz und prägnant, so dass sie ohne Blick auf den vollständigen Anforderungsinhalt wiederzuerkennen ist. Titel sind nicht normativ.'

CATALOG_COLUMN['text']['headline'] = 'Anforderung\nText & {Parameter}'
CATALOG_COLUMN['text']['is_in_sheet'] = True
CATALOG_COLUMN['text']['width'] = 40
CATALOG_COLUMN['text']['hidden'] = False
CATALOG_COLUMN['text']['level'] = 0
CATALOG_COLUMN['text']['comment'] = 'Anforderungen (Controls): Anforderungen sind die zentralen Sicherheitsregeln und werden in OSCAL durch control-Elemente dargestellt. Sie beschreiben Zielzustände oder Grundprinzipien, die erreicht sein müssen, wenn die Anforderung als erfüllt gelten soll. Anforderungen werden durch ihren Titel und den dazugehörigen Anforderungstext beschrieben. Zu einer Anforderung können verschiedene Metadaten zugeordnet sein, z.B. Tags oder Verweise auf andere Anforderungen. Im Grundschutz++ folgt der Text der Anforderungen zudem einem bestimmten Format, der Satzschablone.\n\n{Parameter} zeigen Gestaltungsentscheidungen innerhalb einer Anforderung auf. Das ermöglicht es Katalogautoren und Anwendern auf einen Blick zu sehen wo steuernde Entscheidungen zu treffen sind. Bei einem Audit können die für den Parameter gesetzten Werte automatisiert geprüft werden. Parameter ermöglichen es außerdem Autoren, Anforderungen an spezifischere Kontexte anzupassen. Beispielsweise kann ein Parameter die maximale Anzahl von Fehlversuchen bei der Anmeldung definieren. Verwendet der Anwender hier einen Wert von 10, so kann er für alle Kataloge, die einen Wert von 10 erlauben, eine automatische Dokumentenprüfung bestehen. Diese strukturierte Darstellung unterstützt sowohl die menschliche Lesbarkeit als auch die maschinelle Verarbeitung von Sicherheitsanforderungen und fördert die Wiederverwendbarkeit und Vergleichbarkeit von Sicherheitsanforderungen und -prüfungen. In xlsx-Dokumenten sind Parameter an {geschweiften Klammern} innerhalb des Anforderungstextes zu erkennen.'

CATALOG_COLUMN['praezisierung']['headline'] = 'Anforderung\nPräzisierung'
CATALOG_COLUMN['praezisierung']['is_in_sheet'] = True
CATALOG_COLUMN['praezisierung']['width'] = 25
CATALOG_COLUMN['praezisierung']['hidden'] = False
CATALOG_COLUMN['praezisierung']['level'] = 2
CATALOG_COLUMN['praezisierung']['comment'] = 'Präzisierung: Führt Zeit, Ort oder Inhalt der Anforderung näher aus.'

CATALOG_COLUMN['verbesserung']['headline'] = 'Anforderung\nVerbesserung'
CATALOG_COLUMN['verbesserung']['is_in_sheet'] = True
CATALOG_COLUMN['verbesserung']['width'] = 15
CATALOG_COLUMN['verbesserung']['hidden'] = False
CATALOG_COLUMN['verbesserung']['level'] = 2
CATALOG_COLUMN['verbesserung']['comment'] = 'Verbesserung liegt vor, wenn die Anforderung eine generelle Anforderung erweitert und so die Schutzwirkung erhöht, z.B. die Ende-zu-Ende-Verschlüsselung als Verbesserung der Verschlüsselung beim Transport.\nEine Verbesserung fügt einer übergeordneten Anforderung Details oder mehr Tiefe hinzu.'

CATALOG_COLUMN['tags']['headline'] = 'Anforderung\nTags'
CATALOG_COLUMN['tags']['is_in_sheet'] = True
CATALOG_COLUMN['tags']['width'] = 15
CATALOG_COLUMN['tags']['hidden'] = False
CATALOG_COLUMN['tags']['level'] = 2
CATALOG_COLUMN['tags']['comment'] = 'Tags sind definierte, in Fachkreisen bekannte Themen der Cyber- oder Informationssicherheit, deren Filterung bei der Umsetzung des Themas in einem ISMS unterstützen soll. Begriffe die bereits als Thema vorhanden sind, dürfen nicht auch als Tag verwendet werden. Ziel von Tags ist es nicht, das jeweilige Thema umfassend abzudecken, sondern vielmehr eine gezielte Suche nach den Anforderungen zu ermöglichen, die in besonderem Maße zu dem benannten Thema passen (“Top 10”).'

CATALOG_COLUMN['handlung']['headline'] = 'Anforderung\nHandlungswort'
CATALOG_COLUMN['handlung']['is_in_sheet'] = True
CATALOG_COLUMN['handlung']['width'] = 17
CATALOG_COLUMN['handlung']['hidden'] = False
CATALOG_COLUMN['handlung']['level'] = 2
CATALOG_COLUMN['handlung']['comment'] = 'Handlungsworte sind definierte Tätigkeitsarten. Sie ermöglichen z.B. die Filterung nach Automatismen, Dokumentationsanforderungen oder regelmäßigen Überprüfungen.'

CATALOG_COLUMN['zielobjekte']['headline'] = 'Anforderung\nZielobjekte'
CATALOG_COLUMN['zielobjekte']['is_in_sheet'] = True
CATALOG_COLUMN['zielobjekte']['width'] = 20
CATALOG_COLUMN['zielobjekte']['hidden'] = False
CATALOG_COLUMN['zielobjekte']['level'] = 2
CATALOG_COLUMN['zielobjekte']['comment'] = 'Zielobjekte sind von einer Menge an Anforderungen betroffene IT-Produkte, Verträge oder Adressatengruppen. Sie bilden eine Hierarchie von Zielobjekten und können anhand ihrer Definition klar bestimmt und voneinander abgegrenzt werden. Sind hier mehrere Zielobjekte angegeben, so handelt es sich um eine UND-Verknüpfung (“Hostsysteme von TK-Anwendungen”).'

CATALOG_COLUMN['ergebnis']['headline'] = 'Anforderung\nErgebnis'
CATALOG_COLUMN['ergebnis']['is_in_sheet'] = True
CATALOG_COLUMN['ergebnis']['width'] = 20
CATALOG_COLUMN['ergebnis']['hidden'] = False
CATALOG_COLUMN['ergebnis']['level'] = 2
CATALOG_COLUMN['ergebnis']['comment'] = 'Ergebnis: Enthält das zu erreichende Schutzziel oder den Zielzustand, also den eigentlichen Inhalt der Anforderung.'

CATALOG_COLUMN['dokumentation']['headline'] = 'Anforderung\nDokumentation'
CATALOG_COLUMN['dokumentation']['is_in_sheet'] = True
CATALOG_COLUMN['dokumentation']['width'] = 20
CATALOG_COLUMN['dokumentation']['hidden'] = False
CATALOG_COLUMN['dokumentation']['level'] = 2
CATALOG_COLUMN['dokumentation']['comment'] = 'Dokumentation: Dokumentationsempfehlungen sind definierte Arten von Dokumenten, die zum konsolidierten Nachweis der Erfüllung der Anforderungen genutzt werden können. Sie sind weder normativ noch bei der Auslegung zu beachten, d.h. nur als Vorschlag zur Umsetzung und nicht als inhaltliche Anforderung zu verstehen.'

CATALOG_COLUMN['abhaengigkeit']['headline'] = 'Abhängigkeit'
CATALOG_COLUMN['abhaengigkeit']['is_in_sheet'] = True
CATALOG_COLUMN['abhaengigkeit']['width'] = 14
CATALOG_COLUMN['abhaengigkeit']['hidden'] = False
CATALOG_COLUMN['abhaengigkeit']['level'] = 2
CATALOG_COLUMN['abhaengigkeit']['comment'] = 'Abhängigkeit einer Anforderung von einer anderen ist gegeben, wenn die abhängige Anforderung ihr Schutzziel nicht erreichen kann, ohne dass die vorausgesetzte Anforderung zuerst erfüllt ist. Hierbei sind ausschließlich zwingende Reihenfolgen berücksichtigt. In OSCAL wird dies über das links Array mit der Beziehung "required" abgebildet.'

CATALOG_COLUMN['verwandte']['headline'] = 'Verwandte'
CATALOG_COLUMN['verwandte']['is_in_sheet'] = True
CATALOG_COLUMN['verwandte']['width'] = 14
CATALOG_COLUMN['verwandte']['hidden'] = False
CATALOG_COLUMN['verwandte']['level'] = 2
CATALOG_COLUMN['verwandte']['comment'] = 'Verwandte: Andere Anforderungen, die thematisch oder funktional mit der aktuellen Anforderung verbunden sind. Diese Verweise dienen dazu, die Zusammenhänge und Abhängigkeiten zwischen verschiedenen Anforderungen aufzuzeigen und zu verdeutlichen, wie sie gemeinsam zur Erreichung umfassender Sicherheitsmaßnahmen beitragen. In OSCAL werden sie über das links Array mit der Beziehung "related" abgebildet.'

CATALOG_COLUMN['aufwand']['headline'] = 'Anforderung\nAufwand'
CATALOG_COLUMN['aufwand']['is_in_sheet'] = True
CATALOG_COLUMN['aufwand']['width'] = 14
CATALOG_COLUMN['aufwand']['hidden'] = False
CATALOG_COLUMN['aufwand']['level'] = 2
CATALOG_COLUMN['aufwand']['comment'] = 'Aufwand klassifiziert den ungefähren Ressourcenbedarf, der zur Realisierung einer Anforderung erforderlich ist. Da Aufwand und Schutzwirkung verschiedene Perspektiven sind, ist der Aufwand nicht mit dem Reifegrad oder dem Sicherheitsniveau zu verwechseln. Der Aufwand ist einschließlich der Voraussetzungen angegeben, daher darf eine Anforderung keine geringere Aufwandsklasse haben als die Anforderungen, von denen sie abhängig ist oder die sie verbessert.'


CATALOG_COLUMN['guidance']['headline'] = 'Anforderung\nHinweis'
CATALOG_COLUMN['guidance']['is_in_sheet'] = True
CATALOG_COLUMN['guidance']['width'] = 100
CATALOG_COLUMN['guidance']['hidden'] = False
CATALOG_COLUMN['guidance']['level'] = 1
CATALOG_COLUMN['guidance']['comment'] = 'Hinweise (Guidance) sind Erläuterungen zu der Anforderung, die dem besseren Verständnis der Vorschrift dienen (sog. Erwägungsgründe). Aus ihnen können keine unmittelbaren Rechtsfolgen abgeleitet werden, sie sind jedoch bei der Auslegung der Anforderung zu beachten und können dadurch deren Wirkung wesentlich beeinflussen. Insbesondere können folgende Inhalte als Hinweis aufgenommen werden: Ziele und Zweck (Telos) der Anforderung, Verweise auf technische oder rechtliche Normen, Definitionen von Begriffen oder Konzepten, sowie konkrete, herstellerneutrale Beispiele.'

CATALOG_COLUMN['anforderung_status']['headline'] = 'Anforderung\nReifegrad?'
CATALOG_COLUMN['anforderung_status']['is_in_sheet'] = True
CATALOG_COLUMN['anforderung_status']['width'] = 14
CATALOG_COLUMN['anforderung_status']['hidden'] = False
CATALOG_COLUMN['anforderung_status']['level'] = 0
CATALOG_COLUMN['anforderung_status']['comment'] = 'Der Leitfaden zur Methodik Grundschutz++ vom März 2026: "Der Umsetzungsstatus einer Anforderung kann grundsätzlich nur „umgesetzt“ („ja“) oder „nicht umgesetzt“ („nein“) sein."\n\nIn diesem Sinn nicht Grundschutz++ konform aber für eine differenzierte Darstellung möglicherweise geeignet: Der Reifegrad der Erfüllung der Anforderung wird in einer von fünf möglichen Stufen ausgedrückt.\n\nStufe 0: Die Anforderung ist nicht erfüllt oder der Erfüllungsstaus ist unbekannt.\n\nStufe 1: Die Erfüllung der Anforderung ist initiiert (mindestens Phase Plan)\n\nStufe 2: Stufe 1 und die Erfüllung der Anforderung ist in großen Anteilen bereits gelebte Praxis (vollständige Phase Plan und Phase Do in Umsetzung)\n\nStufe 3: Stufe 2 und mögliche noch fehlende unterstützende und formale Aspekte sind auch erfüllt (wie z. B. zu Schulung und Dokumentation; vollständige Phasen Plan und Do)\n\nStufe 4: Stufe 3 und regelmäßige Überprüfung & Korrektur der Erfüllung (Phasen Check und Act wurden mindestens einmal durchlaufen)\n\n\nLeitfaden zur Methodik Grundschutz++: https://www.bsi.bund.de/SharedDocs/Downloads/DE/BSI/Grundschutz/sonstiges/Methodik_Grundschutz_PlusPlus.html'
# CATALOG_COLUMN['anforderung_status']['comment'] = 'Status der Erfüllung der Anforderung:\n\n- ja = Anforderung ist vollständig erfüllt.\n\n- nein = Anforderung ist nicht erfüllt.\n\n- teilweise = Es wurden bereits einige (nicht alle) Maßnahmen zur Erfüllung der Anforderung umgesetzt.'

CATALOG_COLUMN['massnahmen_umgesetzt']['headline'] = 'Maßnahmen\nBereits umgesetzt'
CATALOG_COLUMN['massnahmen_umgesetzt']['is_in_sheet'] = True
CATALOG_COLUMN['massnahmen_umgesetzt']['width'] = 55
CATALOG_COLUMN['massnahmen_umgesetzt']['hidden'] = False
CATALOG_COLUMN['massnahmen_umgesetzt']['level'] = 0
CATALOG_COLUMN['massnahmen_umgesetzt']['comment'] = 'Maßnahmen, die bereits zur Erfüllung der Anforderung umgesetzt worden sind.'

CATALOG_COLUMN['massnahmen_geplant']['headline'] = 'Maßnahmen\nGeplant'
CATALOG_COLUMN['massnahmen_geplant']['is_in_sheet'] = True
CATALOG_COLUMN['massnahmen_geplant']['width'] = 55
CATALOG_COLUMN['massnahmen_geplant']['hidden'] = False
CATALOG_COLUMN['massnahmen_geplant']['level'] = 0
CATALOG_COLUMN['massnahmen_geplant']['comment'] = 'Maßnahmen, die zur Erfüllung der Anforderung geplant und noch nicht umgesetzt sind.'

CATALOG_COLUMN['anmerkungen']['headline'] = 'Anmerkungen'
CATALOG_COLUMN['anmerkungen']['is_in_sheet'] = True
CATALOG_COLUMN['anmerkungen']['width'] = 55
CATALOG_COLUMN['anmerkungen']['hidden'] = False
CATALOG_COLUMN['anmerkungen']['level'] = 0
CATALOG_COLUMN['anmerkungen']['comment'] = 'Freitextfeld für Anmerkungen wie z.B. zu:\n\n-Spezifizierung der Anforderung\n\n- Fristen der Umsetzung geplanter Maßnahmen\n\n- Verantwortliche der Umsetzung geplanter Maßnahmen'

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

def anmerkungen(control_id: str) -> str:
    return ''    

def aufwand(control_id: str) -> str:    
    return CONTROL_ATTRIBUTES[control_id]['effort_level']

def dokumentation(control_id: str) -> str:
    return CONTROL_ATTRIBUTES[control_id]['documentation']
  
def ergebnis(control_id: str) -> str:
    return CONTROL_ATTRIBUTES[control_id]['result']

def guidance(control_id: str) -> str:
    return CONTROL_ATTRIBUTES[control_id]['guidance']

def handlung(control_id: str) -> str:
    return CONTROL_ATTRIBUTES[control_id]['action_word']

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

def construct_sheet_catalog_rows(workbook, sheet_catalog):    
    header_format = workbook.add_format(HEADER_FORMAT)
           
    column = 0
    for key in CATALOG_COLUMN.keys():
        if not CATALOG_COLUMN[key]['is_in_sheet']: continue
        
        #setze die breite der spalten
        width  = CATALOG_COLUMN[key]['width']
        hidden  = CATALOG_COLUMN[key]['hidden']
        level = CATALOG_COLUMN[key]['level']              
        sheet_catalog.set_column(column, column, width, None, {'level': level,'hidden': hidden})            
        
        #schreibe Kopzzeile
        sheet_catalog.set_row(0, 30) 
        sheet_catalog.write_string(0, column, CATALOG_COLUMN[key]['headline'],header_format)
        
        #schreibe Kommentare    
        sheet_catalog.write_comment(0, column, CATALOG_COLUMN[key]['comment'], KOMMENTAR_GROESSE)
        
        column +=1

def construct_sheet_deckblatt(sheet_deckblatt):    
    if PATH_LOGO:
        sheet_deckblatt.insert_image(1, 0, PATH_LOGO)    
        row = 7
    else:
        row = 0
    
    cell_value = 'Stand: Erstellung Excel Datei ' + ymd2dmy(DATUM_ERSTELLUNG_XLSX) + ' aus GS++ Katalog github commit ' +  ymd2dmy(DATUM_CATALOG_GITHUB_COMMIT)
    sheet_deckblatt.write_string(row,0, cell_value)
    
    cell_value = 'Quelle: json-Datei mit GS++ Katalog aus github : https://github.com/BSI-Bund/Stand-der-Technik-Bibliothek/tree/main/Anwenderkataloge/Grundschutz%2B%2B'
    sheet_deckblatt.write_string(row + 1,0, cell_value)
    
    cell_value = 'Kontakt: ' + KONTAKT
    sheet_deckblatt.write_string(row + 2,0, cell_value)
    
    
            
def construct_sheet_catalog_row(workbook, sheet_catalog, row, control_id):            
    # Lege Format der Zeile fest     
    cell_format =  workbook.add_format(CELL_FORMAT)
    
    # Trage Spalteninhalte in Zellen ein
    column, row_height = 0, 0
    for key in CATALOG_COLUMN.keys():
        if not CATALOG_COLUMN[key]['is_in_sheet']: continue
        try:
            cell_value = globals()[key](control_id)            
            row_height = max([row_height, math.ceil(len(cell_value) / CATALOG_COLUMN[key]['width'])])
        except:
            cell_value = ''
        sheet_catalog.write_string(row, column, cell_value, cell_format)
        column += 1
            
    # Lege Zeilenhöhe fest
    sheet_catalog.set_row(row, row_height*15)

def set_sheet_catalog_autofilter(rows, sheet_catalog):      
    columns = 0
    for key in CATALOG_COLUMN.keys():        
        if not CATALOG_COLUMN[key]['is_in_sheet']: continue    
        columns += 1    
    sheet_catalog.autofilter(0,0,rows - 1,columns - 1) 

def main():     
    # Öffne xlsx-datei         
    workbook = xlsxwriter.Workbook(PATH_CATALOG_XLSX)
        
    # Erstelle Tabellenbätter zu Deckblatt und den controls
    sheet_deckblatt = workbook.add_worksheet("Deckblatt")    
    sheet_catalog = workbook.add_worksheet('GS++ Catalog github ' + ymd2dmy(DATUM_CATALOG_GITHUB_COMMIT))
    sheet_catalog.freeze_panes(1,0) 
    
    # Gestalte Deckblatt
    construct_sheet_deckblatt(sheet_deckblatt)
        
    #Gestalte Spalten im Tabellenblatt mit den controls
    construct_sheet_catalog_rows(workbook, sheet_catalog)    
    
    #gestalte Zeilen im Tabellenblatt mit den controls
    row = 0
    for control_id in CONTROL_ATTRIBUTES.keys():
        row += 1        
        construct_sheet_catalog_row(workbook, sheet_catalog, row, control_id)
            
    # setze in jeder Spalte Autofilter
    set_sheet_catalog_autofilter(row, sheet_catalog)  
    
    # Schließe Datei
    workbook.close()

if __name__ == "__main__":
    main()
