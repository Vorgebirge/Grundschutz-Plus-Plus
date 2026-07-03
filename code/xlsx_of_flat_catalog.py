#Stand 03.07.2026
import math, re, xlsxwriter #https://xlsxwriter.readthedocs.io/
from helper_functions import read_json_file, sort_list_naturally, today, ymd2dmy
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

CATALOG_COLUMN['klasse']['cell_value_type'] = 'string'
CATALOG_COLUMN['klasse']['headline'] = 'Klasse'
CATALOG_COLUMN['klasse']['is_in_sheet'] = True
CATALOG_COLUMN['klasse']['width'] = 20
CATALOG_COLUMN['klasse']['hidden'] = False
CATALOG_COLUMN['klasse']['level'] = 3
CATALOG_COLUMN['klasse']['comment'] = ''


CATALOG_COLUMN['praktik']['cell_value_type'] = 'string'
CATALOG_COLUMN['praktik']['headline'] = 'Praktik'
CATALOG_COLUMN['praktik']['is_in_sheet'] = True
CATALOG_COLUMN['praktik']['width'] = 20
CATALOG_COLUMN['praktik']['hidden'] = False
CATALOG_COLUMN['praktik']['level'] = 3
CATALOG_COLUMN['praktik']['comment'] = 'Praktiken (OSCAL Groups) sind die “Überschriften”, in die ein Katalog gegliedert ist. Gleichzeitig sind die Praktiken als Vorschläge für (Teil-)Prozesse des ISMS zu betrachten. Jede Praktik kann als eigenständiger, abgrenzbarer (Teil-)Prozess von größerem Umfang angesehen werden, der in einem ISMS zwingend erforderlich ist zur Erreichung der Schutzziele nach ISO/IEC 27001. Die Praktiken sind jedoch nicht gleichzusetzen mit inhaltlichen Geschäftsprozessen wie Finanzwesen oder Vertrieb.'

CATALOG_COLUMN['thema']['cell_value_type'] = 'string'
CATALOG_COLUMN['thema']['headline'] = 'Praktik\nThema'
CATALOG_COLUMN['thema']['is_in_sheet'] = True
CATALOG_COLUMN['thema']['width'] = 23
CATALOG_COLUMN['thema']['hidden'] = False
CATALOG_COLUMN['thema']['level'] = 3
CATALOG_COLUMN['thema']['comment'] = 'Themen (OSCAL Group in Group)sind die Untergruppen (“Unterüberschriften”) innerhalb einer Praktik und dienen der thematischen Zusammenfassung von Anforderungen, z.B. zum Management von Schwachstellen.'

CATALOG_COLUMN['praktik_typ']['cell_value_type'] = 'string'
CATALOG_COLUMN['praktik_typ']['headline'] = 'Praktik\nTyp'
CATALOG_COLUMN['praktik_typ']['is_in_sheet'] = True
CATALOG_COLUMN['praktik_typ']['width'] = 16
CATALOG_COLUMN['praktik_typ']['hidden'] = False
CATALOG_COLUMN['praktik_typ']['level'] = 3
CATALOG_COLUMN['praktik_typ']['comment'] = 'Praktiken lassen sich unterteilen in:\n- ISMS-Praktiken\n- Organisatorische Praktiken\n- Technische Praktiken\n\nDie ISMS-Praktiken sind übergreifend. Sie bauen einen Plan-Do-Check-Act-Zyklus (PDCA-Zyklus) des Managementsystems auf, der die fortlaufende Kontrolle und Verbesserung über alle Bereiche hinweg gewährleistet.\n\nDie Anforderungen der ISMS-Praktiken sind übergreifend und keiner einzelne Zielobjektkategorie zugewiesen. Sie bauen auf den PDCA-Zyklus des Managementsystems auf und gelten deshalb einmalig für den gesamten Informationsverbund.'

CATALOG_COLUMN['sicherheitsniveau']['cell_value_type'] = 'string'
CATALOG_COLUMN['sicherheitsniveau']['headline'] = 'Anforderung\nSicherheitsniveau'
CATALOG_COLUMN['sicherheitsniveau']['is_in_sheet'] = True
CATALOG_COLUMN['sicherheitsniveau']['width'] = 18
CATALOG_COLUMN['sicherheitsniveau']['hidden'] = False
CATALOG_COLUMN['sicherheitsniveau']['level'] = 3
CATALOG_COLUMN['sicherheitsniveau']['comment'] = 'Klassifiziert das Sicherheitsniveau bei dem eine Anforderung relevant ist. Mögliche Werte sind normal-SdT für den normalen Stand der Technik oder erhöht für Anforderungen, für die eine individuelle Risikoanalyse erforderlich ist.'

CATALOG_COLUMN['modalverb']['cell_value_type'] = 'string'
CATALOG_COLUMN['modalverb']['headline'] = 'Anforderung\nModalverb'
CATALOG_COLUMN['modalverb']['is_in_sheet'] = True
CATALOG_COLUMN['modalverb']['width'] = 14
CATALOG_COLUMN['modalverb']['hidden'] = False
CATALOG_COLUMN['modalverb']['level'] = 3
CATALOG_COLUMN['modalverb']['comment'] = 'Das Modalverb einer Anforderung gibt an, welchen Pflichtcharakter sie hat, d.h. ob es sich um eine MUSS-, SOLLTE- oder KANN-Anforderung handelt. Für die Anforderungen gelten folgende Definitionen:\n\n- MUSS → verpflichtend, keine Abweichung erlaubt (entspricht „MUST“1).\n\n- SOLLTE → in der Regel verpflichtend, Abweichung in begründeten Ausnahmefällen möglich (entspricht „SHOULD“).\n\n- KANN → optional, je nach Situation sinnvoll, aber nicht notwendig (entspricht „MAY“).'

CATALOG_COLUMN['alt_identifier']['cell_value_type'] = 'string'
CATALOG_COLUMN['alt_identifier']['headline'] = 'Anforderung\nUUID'
CATALOG_COLUMN['alt_identifier']['is_in_sheet'] = True
CATALOG_COLUMN['alt_identifier']['width'] = 14
CATALOG_COLUMN['alt_identifier']['hidden'] = True
CATALOG_COLUMN['alt_identifier']['level'] = 3
CATALOG_COLUMN['alt_identifier']['comment'] = 'UUID: Über alle Kataloge und Katalogversionen hinweg eindeutige Identifikationsnummer der Anforderung. Diese folgt der Bedeutung der Anforderung, bleibt also auch bei bedeutungserhaltenden Umformulierungen oder Verschiebungen von Anforderungen gleich. Andererseits wird sie ersetzt, wenn sich die Bedeutung der Anforderung wesentlich verändert, selbst wenn ihre Stellung in der Struktur bleibt.'

CATALOG_COLUMN['anforderung_id']['cell_value_type'] = 'string'
CATALOG_COLUMN['anforderung_id']['headline'] = 'Anforderung\nID'
CATALOG_COLUMN['anforderung_id']['is_in_sheet'] = True
CATALOG_COLUMN['anforderung_id']['width'] = 14
CATALOG_COLUMN['anforderung_id']['hidden'] = False
CATALOG_COLUMN['anforderung_id']['level'] = 0
CATALOG_COLUMN['anforderung_id']['comment'] = 'ID: Eindeutiger Identifikator der Anforderung innerhalb der Praktik und des Themas im Format {Kürzel der Praktik}.{Nummerierung des Themas}.{Nummerierung der Anforderung}. Die ID ergibt sich also aus der Stellung der Anforderung innerhalb des Dokumentes.'

CATALOG_COLUMN['anforderung_titel_ohne_id']['cell_value_type'] = 'string'
CATALOG_COLUMN['anforderung_titel_ohne_id']['headline'] = 'Anforderung\nTitel'
CATALOG_COLUMN['anforderung_titel_ohne_id']['is_in_sheet'] = True
CATALOG_COLUMN['anforderung_titel_ohne_id']['width'] = 20
CATALOG_COLUMN['anforderung_titel_ohne_id']['hidden'] = False
CATALOG_COLUMN['anforderung_titel_ohne_id']['level'] = 0
CATALOG_COLUMN['anforderung_titel_ohne_id']['comment'] = 'Titel: Titel der einzelnen Anforderung. Der Titel beschreibt eine Anforderung kurz und prägnant, so dass sie ohne Blick auf den vollständigen Anforderungsinhalt wiederzuerkennen ist. Titel sind nicht normativ.'

CATALOG_COLUMN['anforderung']['cell_value_type'] = 'string'
CATALOG_COLUMN['anforderung']['headline'] = 'Anforderung\nID und Titel'
CATALOG_COLUMN['anforderung']['is_in_sheet'] = False
CATALOG_COLUMN['anforderung']['width'] = 30
CATALOG_COLUMN['anforderung']['hidden'] = False
CATALOG_COLUMN['anforderung']['level'] = 0
CATALOG_COLUMN['anforderung']['comment'] = 'ID: Eindeutiger Identifikator der Anforderung innerhalb der Praktik und des Themas im Format {Kürzel der Praktik}.{Nummerierung des Themas}.{Nummerierung der Anforderung}. Die ID ergibt sich also aus der Stellung der Anforderung innerhalb des Dokumentes.\n\nTitel: Titel der einzelnen Anforderung. Der Titel beschreibt eine Anforderung kurz und prägnant, so dass sie ohne Blick auf den vollständigen Anforderungsinhalt wiederzuerkennen ist. Titel sind nicht normativ.'

CATALOG_COLUMN['text']['cell_value_type'] = 'string'
CATALOG_COLUMN['text']['headline'] = 'Anforderung\nText & {Parameter}'
CATALOG_COLUMN['text']['is_in_sheet'] = True
CATALOG_COLUMN['text']['width'] = 40
CATALOG_COLUMN['text']['hidden'] = False
CATALOG_COLUMN['text']['level'] = 0
CATALOG_COLUMN['text']['comment'] = 'Anforderungen (Controls): Anforderungen sind die zentralen Sicherheitsregeln und werden in OSCAL durch control-Elemente dargestellt. Sie beschreiben Zielzustände oder Grundprinzipien, die erreicht sein müssen, wenn die Anforderung als erfüllt gelten soll. Anforderungen werden durch ihren Titel und den dazugehörigen Anforderungstext beschrieben. Zu einer Anforderung können verschiedene Metadaten zugeordnet sein, z.B. Tags oder Verweise auf andere Anforderungen. Im Grundschutz++ folgt der Text der Anforderungen zudem einem bestimmten Format, der Satzschablone.\n\n{Parameter} zeigen Gestaltungsentscheidungen innerhalb einer Anforderung auf. Das ermöglicht es Katalogautoren und Anwendern auf einen Blick zu sehen wo steuernde Entscheidungen zu treffen sind. Bei einem Audit können die für den Parameter gesetzten Werte automatisiert geprüft werden. Parameter ermöglichen es außerdem Autoren, Anforderungen an spezifischere Kontexte anzupassen. Beispielsweise kann ein Parameter die maximale Anzahl von Fehlversuchen bei der Anmeldung definieren. Verwendet der Anwender hier einen Wert von 10, so kann er für alle Kataloge, die einen Wert von 10 erlauben, eine automatische Dokumentenprüfung bestehen. Diese strukturierte Darstellung unterstützt sowohl die menschliche Lesbarkeit als auch die maschinelle Verarbeitung von Sicherheitsanforderungen und fördert die Wiederverwendbarkeit und Vergleichbarkeit von Sicherheitsanforderungen und -prüfungen. In xlsx-Dokumenten sind Parameter an {geschweiften Klammern} innerhalb des Anforderungstextes zu erkennen.'

CATALOG_COLUMN['link_implementierung']['cell_value_type'] = 'url'
CATALOG_COLUMN['link_implementierung']['headline'] = 'Anforderung\nImplementierung?'
CATALOG_COLUMN['link_implementierung']['is_in_sheet'] = True
CATALOG_COLUMN['link_implementierung']['width'] = 20
CATALOG_COLUMN['link_implementierung']['hidden'] = False
CATALOG_COLUMN['link_implementierung']['level'] = 2
CATALOG_COLUMN['link_implementierung']['comment'] = '-'

CATALOG_COLUMN['praezisierung']['cell_value_type'] = 'string'
CATALOG_COLUMN['praezisierung']['headline'] = 'Anforderung\nPräzisierung'
CATALOG_COLUMN['praezisierung']['is_in_sheet'] = True
CATALOG_COLUMN['praezisierung']['width'] = 25
CATALOG_COLUMN['praezisierung']['hidden'] = False
CATALOG_COLUMN['praezisierung']['level'] = 2
CATALOG_COLUMN['praezisierung']['comment'] = 'Präzisierung: Führt Zeit, Ort oder Inhalt der Anforderung näher aus.'

CATALOG_COLUMN['verbesserung']['cell_value_type'] = 'string'
CATALOG_COLUMN['verbesserung']['headline'] = 'Anforderung\nVerbesserung'
CATALOG_COLUMN['verbesserung']['is_in_sheet'] = True
CATALOG_COLUMN['verbesserung']['width'] = 15
CATALOG_COLUMN['verbesserung']['hidden'] = False
CATALOG_COLUMN['verbesserung']['level'] = 2
CATALOG_COLUMN['verbesserung']['comment'] = 'Verbesserung liegt vor, wenn die Anforderung eine generelle Anforderung erweitert und so die Schutzwirkung erhöht, z.B. die Ende-zu-Ende-Verschlüsselung als Verbesserung der Verschlüsselung beim Transport.\nEine Verbesserung fügt einer übergeordneten Anforderung Details oder mehr Tiefe hinzu.'

CATALOG_COLUMN['tags']['cell_value_type'] = 'string'
CATALOG_COLUMN['tags']['headline'] = 'Anforderung\nTags'
CATALOG_COLUMN['tags']['is_in_sheet'] = True
CATALOG_COLUMN['tags']['width'] = 15
CATALOG_COLUMN['tags']['hidden'] = False
CATALOG_COLUMN['tags']['level'] = 2
CATALOG_COLUMN['tags']['comment'] = 'Tags sind definierte, in Fachkreisen bekannte Themen der Cyber- oder Informationssicherheit, deren Filterung bei der Umsetzung des Themas in einem ISMS unterstützen soll. Begriffe die bereits als Thema vorhanden sind, dürfen nicht auch als Tag verwendet werden. Ziel von Tags ist es nicht, das jeweilige Thema umfassend abzudecken, sondern vielmehr eine gezielte Suche nach den Anforderungen zu ermöglichen, die in besonderem Maße zu dem benannten Thema passen (“Top 10”).'

CATALOG_COLUMN['handlung']['cell_value_type'] = 'string'
CATALOG_COLUMN['handlung']['headline'] = 'Anforderung\nHandlungswort'
CATALOG_COLUMN['handlung']['is_in_sheet'] = True
CATALOG_COLUMN['handlung']['width'] = 17
CATALOG_COLUMN['handlung']['hidden'] = False
CATALOG_COLUMN['handlung']['level'] = 2
CATALOG_COLUMN['handlung']['comment'] = 'Handlungsworte sind definierte Tätigkeitsarten. Sie ermöglichen z.B. die Filterung nach Automatismen, Dokumentationsanforderungen oder regelmäßigen Überprüfungen.'

CATALOG_COLUMN['zielobjekte']['cell_value_type'] = 'string'
CATALOG_COLUMN['zielobjekte']['headline'] = 'Anforderung\nZielobjekte'
CATALOG_COLUMN['zielobjekte']['is_in_sheet'] = True
CATALOG_COLUMN['zielobjekte']['width'] = 20
CATALOG_COLUMN['zielobjekte']['hidden'] = False
CATALOG_COLUMN['zielobjekte']['level'] = 2
CATALOG_COLUMN['zielobjekte']['comment'] = 'Zielobjekte sind von einer Menge an Anforderungen betroffene IT-Produkte, Verträge oder Adressatengruppen. Sie bilden eine Hierarchie von Zielobjekten und können anhand ihrer Definition klar bestimmt und voneinander abgegrenzt werden. Sind hier mehrere Zielobjekte angegeben, so handelt es sich um eine UND-Verknüpfung (“Hostsysteme von TK-Anwendungen”).'

CATALOG_COLUMN['ergebnis']['cell_value_type'] = 'string'
CATALOG_COLUMN['ergebnis']['headline'] = 'Anforderung\nErgebnis'
CATALOG_COLUMN['ergebnis']['is_in_sheet'] = True
CATALOG_COLUMN['ergebnis']['width'] = 20
CATALOG_COLUMN['ergebnis']['hidden'] = False
CATALOG_COLUMN['ergebnis']['level'] = 2
CATALOG_COLUMN['ergebnis']['comment'] = 'Ergebnis: Enthält das zu erreichende Schutzziel oder den Zielzustand, also den eigentlichen Inhalt der Anforderung.'

CATALOG_COLUMN['dokumentation']['cell_value_type'] = 'string'
CATALOG_COLUMN['dokumentation']['headline'] = 'Anforderung\nDokumentation'
CATALOG_COLUMN['dokumentation']['is_in_sheet'] = True
CATALOG_COLUMN['dokumentation']['width'] = 20
CATALOG_COLUMN['dokumentation']['hidden'] = False
CATALOG_COLUMN['dokumentation']['level'] = 2
CATALOG_COLUMN['dokumentation']['comment'] = 'Dokumentation: Dokumentationsempfehlungen sind definierte Arten von Dokumenten, die zum konsolidierten Nachweis der Erfüllung der Anforderungen genutzt werden können. Sie sind weder normativ noch bei der Auslegung zu beachten, d.h. nur als Vorschlag zur Umsetzung und nicht als inhaltliche Anforderung zu verstehen.'

CATALOG_COLUMN['abhaengigkeit']['cell_value_type'] = 'string'
CATALOG_COLUMN['abhaengigkeit']['headline'] = 'Abhängigkeit'
CATALOG_COLUMN['abhaengigkeit']['is_in_sheet'] = True
CATALOG_COLUMN['abhaengigkeit']['width'] = 14
CATALOG_COLUMN['abhaengigkeit']['hidden'] = False
CATALOG_COLUMN['abhaengigkeit']['level'] = 2
CATALOG_COLUMN['abhaengigkeit']['comment'] = 'Abhängigkeit einer Anforderung von einer anderen ist gegeben, wenn die abhängige Anforderung ihr Schutzziel nicht erreichen kann, ohne dass die vorausgesetzte Anforderung zuerst erfüllt ist. Hierbei sind ausschließlich zwingende Reihenfolgen berücksichtigt. In OSCAL wird dies über das links Array mit der Beziehung "required" abgebildet.'

CATALOG_COLUMN['verwandte']['cell_value_type'] = 'string'
CATALOG_COLUMN['verwandte']['headline'] = 'Verwandte'
CATALOG_COLUMN['verwandte']['is_in_sheet'] = True
CATALOG_COLUMN['verwandte']['width'] = 14
CATALOG_COLUMN['verwandte']['hidden'] = False
CATALOG_COLUMN['verwandte']['level'] = 2
CATALOG_COLUMN['verwandte']['comment'] = 'Verwandte: Andere Anforderungen, die thematisch oder funktional mit der aktuellen Anforderung verbunden sind. Diese Verweise dienen dazu, die Zusammenhänge und Abhängigkeiten zwischen verschiedenen Anforderungen aufzuzeigen und zu verdeutlichen, wie sie gemeinsam zur Erreichung umfassender Sicherheitsmaßnahmen beitragen. In OSCAL werden sie über das links Array mit der Beziehung "related" abgebildet.'

CATALOG_COLUMN['aufwand']['cell_value_type'] = 'string'
CATALOG_COLUMN['aufwand']['headline'] = 'Anforderung\nAufwand'
CATALOG_COLUMN['aufwand']['is_in_sheet'] = True
CATALOG_COLUMN['aufwand']['width'] = 14
CATALOG_COLUMN['aufwand']['hidden'] = False
CATALOG_COLUMN['aufwand']['level'] = 2
CATALOG_COLUMN['aufwand']['comment'] = 'Aufwand klassifiziert den ungefähren Ressourcenbedarf, der zur Realisierung einer Anforderung erforderlich ist. Da Aufwand und Schutzwirkung verschiedene Perspektiven sind, ist der Aufwand nicht mit dem Reifegrad oder dem Sicherheitsniveau zu verwechseln. Der Aufwand ist einschließlich der Voraussetzungen angegeben, daher darf eine Anforderung keine geringere Aufwandsklasse haben als die Anforderungen, von denen sie abhängig ist oder die sie verbessert.'

#Authentizität, Integrität, Verfügbarkeit, Vertraulichkeit, Elementare Gefährdung(en)

CATALOG_COLUMN['sicherheitsziel_authentizitaet']['cell_value_type'] = 'string'
CATALOG_COLUMN['sicherheitsziel_authentizitaet']['headline'] = 'Anforderung\nAuthentizität'
CATALOG_COLUMN['sicherheitsziel_authentizitaet']['is_in_sheet'] = True
CATALOG_COLUMN['sicherheitsziel_authentizitaet']['width'] = 14
CATALOG_COLUMN['sicherheitsziel_authentizitaet']['hidden'] = False
CATALOG_COLUMN['sicherheitsziel_authentizitaet']['level'] = 2
CATALOG_COLUMN['sicherheitsziel_authentizitaet']['comment'] = 'Mit dem Begriff Authentizität (Authenticity) wird die Eigenschaft bezeichnet, die gewährleistet, dass eine Kommunikationsstelle tatsächlich diejenige ist, der sie vorgibt zu sein. Bei authentischen Informationen ist sichergestellt, dass sie von der angegebenen Quelle erstellt wurden. Der Begriff wird nicht nur verwendet, wenn die Identität von Personen geprüft wird, sondern auch bei IT-Komponenten oder Anwendungen. D.h. Die Echtheit einer Person, eines Systems oder von Daten muss nachweisbar sein.'

CATALOG_COLUMN['sicherheitsziel_integritaet']['cell_value_type'] = 'string'
CATALOG_COLUMN['sicherheitsziel_integritaet']['headline'] = 'Anforderung\nIntegrität'
CATALOG_COLUMN['sicherheitsziel_integritaet']['is_in_sheet'] = True
CATALOG_COLUMN['sicherheitsziel_integritaet']['width'] = 14
CATALOG_COLUMN['sicherheitsziel_integritaet']['hidden'] = False
CATALOG_COLUMN['sicherheitsziel_integritaet']['level'] = 2
CATALOG_COLUMN['sicherheitsziel_integritaet']['comment'] = 'Integrität (Integrity) bezeichnet die Sicherstellung der Korrektheit (Unversehrtheit) von Daten und der korrekten Funktionsweise von Systemen. Wenn der Begriff Integrität auf "Daten" angewendet wird, drückt er aus, dass die Daten vollständig und unverändert sind. In der Informationstechnik wird er in der Regel aber weiter gefasst und auf "Informationen" angewendet. Der Begriff "Information" wird dabei für "Daten" verwendet, denen je nach Zusammenhang bestimmte Attribute wie z. B. Autorenschaft oder Zeitpunkt der Erstellung zugeordnet werden können. Der Verlust der Integrität von Informationen kann daher bedeuten, dass diese unerlaubt verändert, Angaben zur verfassenden Person verfälscht oder Zeitangaben zur Erstellung manipuliert wurden. D.h. Daten und Systeme müssen korrekt und unverändert sein. Unbefugte Änderungen dürfen nicht erfolgen.'

CATALOG_COLUMN['sicherheitsziel_verfuegbarkeit']['cell_value_type'] = 'string'
CATALOG_COLUMN['sicherheitsziel_verfuegbarkeit']['headline'] = 'Anforderung\nVerfügbarkeit'
CATALOG_COLUMN['sicherheitsziel_verfuegbarkeit']['is_in_sheet'] = True
CATALOG_COLUMN['sicherheitsziel_verfuegbarkeit']['width'] = 15
CATALOG_COLUMN['sicherheitsziel_verfuegbarkeit']['hidden'] = False
CATALOG_COLUMN['sicherheitsziel_verfuegbarkeit']['level'] = 2
CATALOG_COLUMN['sicherheitsziel_verfuegbarkeit']['comment'] = 'Die Verfügbarkeit (Availability) von Dienstleistungen, Funktionen eines IT-Systems, IT-Anwendungen oder IT-Netzen oder auch von Informationen ist vorhanden, wenn diese von den Anwendenden stets wie vorgesehen genutzt werden können.D.h. Informationen, Anwendungen und IT-Systeme müssen bei Bedarf nutzbar und erreichbar sein.'

CATALOG_COLUMN['sicherheitsziel_vertraulichkeit']['cell_value_type'] = 'string'
CATALOG_COLUMN['sicherheitsziel_vertraulichkeit']['headline'] = 'Anforderung\nVertraulichkeit'
CATALOG_COLUMN['sicherheitsziel_vertraulichkeit']['is_in_sheet'] = True
CATALOG_COLUMN['sicherheitsziel_vertraulichkeit']['width'] = 17
CATALOG_COLUMN['sicherheitsziel_vertraulichkeit']['hidden'] = False
CATALOG_COLUMN['sicherheitsziel_vertraulichkeit']['level'] = 2
CATALOG_COLUMN['sicherheitsziel_vertraulichkeit']['comment'] = 'Vertraulichkeit (Confidentiality) ist der Schutz vor unbefugter Preisgabe von Informationen. Vertrauliche Daten und Informationen dürfen ausschließlich Befugten in der zulässigen Weise zugänglich sein d.h. Informationen dürfen nur von berechtigten Personen oder Systemen eingesehen werden.'

CATALOG_COLUMN['elementare_gefaehrdung']['cell_value_type'] = 'string'
CATALOG_COLUMN['elementare_gefaehrdung']['headline'] = 'Anforderung\nElem. Gefährdung'
CATALOG_COLUMN['elementare_gefaehrdung']['is_in_sheet'] = True
CATALOG_COLUMN['elementare_gefaehrdung']['width'] = 20
CATALOG_COLUMN['elementare_gefaehrdung']['hidden'] = False
CATALOG_COLUMN['elementare_gefaehrdung']['level'] = 2
CATALOG_COLUMN['elementare_gefaehrdung']['comment'] = 'Elementare Gefährdungen\n\nG 0.1	Feuer\nG 0.2	Ungünstige klimatische Bedingungen\nG 0.3	Wasser\nG 0.4	Verschmutzung, Staub, Korrosion\nG 0.5	Naturkatastrophen\nG 0.6	Katastrophen im Umfeld\nG 0.7	Großereignisse im Umfeld\nG 0.8	Ausfall oder Störung der Stromversorgung\nG 0.9	Ausfall oder Störung von Kommunikationsnetzen\nG 0.10	Ausfall oder Störung von Versorgungsnetzen\nG 0.11	Ausfall oder Störung von Dienstleistern\nG 0.12	Elektromagnetische Störstrahlung\nG 0.13	Abfangen kompromittierender Strahlung\nG 0.14	Ausspähen von Informationen (Spionage)\nG 0.15	Abhören\nG 0.16	Diebstahl von Geräten, Datenträgern oder Dokumenten\nG 0.17	Verlust von Geräten, Datenträgern oder Dokumenten\nG 0.18	Fehlplanung oder fehlende Anpassung\nG 0.19	Offenlegung schützenswerter Informationen\nG 0.20	Informationen oder Produkte aus unzuverlässiger Quelle\nG 0.21	Manipulation von Hard- oder Software\nG 0.22	Manipulation von Informationen\nG 0.23	Unbefugtes Eindringen in IT-Systeme\nG 0.24	Zerstörung von Geräten oder Datenträgern\nG 0.25	Ausfall von Geräten oder Systemen\nG 0.26	Fehlfunktion von Geräten oder Systemen\nG 0.27	Ressourcenmangel\nG 0.28	Software-Schwachstellen oder -Fehler\nG 0.29	Verstoß gegen Gesetze oder Regelungen\nG 0.30	Unberechtigte Nutzung oder Administration von Geräten und Systemen\nG 0.31	Fehlerhafte Nutzung oder Administration von Geräten und Systemen\nG 0.32	Missbrauch von Berechtigungen\nG 0.33	Personalausfall\nG 0.34	Anschlag\nG 0.35	Nötigung, Erpressung oder Korruption\nG 0.36	Identitätsdiebstahl\nG 0.37	Abstreiten von Handlungen\nG 0.38	Missbrauch personenbezogener Daten\nG 0.39	Schadprogramme\nG 0.40	Verhinderung von Diensten (Denial of Service)\nG 0.41	Sabotage\nG 0.42	Social Engineering\nG 0.43	Einspielen von Nachrichten\nG 0.44	Unbefugtes Eindringen in Räumlichkeiten\nG 0.45	Datenverlust\nG 0.46	Integritätsverlust schützenswerter Informationen\nG 0.47	Schädliche Seiteneffekte\nIT-gestützter Angriffe'

CATALOG_COLUMN['guidance']['cell_value_type'] = 'string'
CATALOG_COLUMN['guidance']['headline'] = 'Anforderung\nHinweis'
CATALOG_COLUMN['guidance']['is_in_sheet'] = True
CATALOG_COLUMN['guidance']['width'] = 100
CATALOG_COLUMN['guidance']['hidden'] = False
CATALOG_COLUMN['guidance']['level'] = 1
CATALOG_COLUMN['guidance']['comment'] = 'Hinweise (Guidance) sind Erläuterungen zu der Anforderung, die dem besseren Verständnis der Vorschrift dienen (sog. Erwägungsgründe). Aus ihnen können keine unmittelbaren Rechtsfolgen abgeleitet werden, sie sind jedoch bei der Auslegung der Anforderung zu beachten und können dadurch deren Wirkung wesentlich beeinflussen. Insbesondere können folgende Inhalte als Hinweis aufgenommen werden: Ziele und Zweck (Telos) der Anforderung, Verweise auf technische oder rechtliche Normen, Definitionen von Begriffen oder Konzepten, sowie konkrete, herstellerneutrale Beispiele.'

CATALOG_COLUMN['anforderung_status']['cell_value_type'] = 'string'
CATALOG_COLUMN['anforderung_status']['headline'] = 'Anforderung\nReifegrad?'
CATALOG_COLUMN['anforderung_status']['is_in_sheet'] = True
CATALOG_COLUMN['anforderung_status']['width'] = 14
CATALOG_COLUMN['anforderung_status']['hidden'] = False
CATALOG_COLUMN['anforderung_status']['level'] = 0
CATALOG_COLUMN['anforderung_status']['comment'] = 'Der Leitfaden zur Methodik Grundschutz++ vom März 2026: "Der Umsetzungsstatus einer Anforderung kann grundsätzlich nur „umgesetzt“ („ja“) oder „nicht umgesetzt“ („nein“) sein."\n\nIn diesem Sinn nicht Grundschutz++ konform aber für eine differenzierte Darstellung möglicherweise geeignet: Der Reifegrad der Erfüllung der Anforderung wird in einer von fünf möglichen Stufen ausgedrückt.\n\nStufe 0: Die Anforderung ist nicht erfüllt oder der Erfüllungsstaus ist unbekannt.\n\nStufe 1: Die Erfüllung der Anforderung ist initiiert (mindestens Phase Plan)\n\nStufe 2: Stufe 1 und die Erfüllung der Anforderung ist in großen Anteilen bereits gelebte Praxis (vollständige Phase Plan und Phase Do in Umsetzung)\n\nStufe 3: Stufe 2 und mögliche noch fehlende unterstützende und formale Aspekte sind auch erfüllt (wie z. B. zu Schulung und Dokumentation; vollständige Phasen Plan und Do)\n\nStufe 4: Stufe 3 und regelmäßige Überprüfung & Korrektur der Erfüllung (Phasen Check und Act wurden mindestens einmal durchlaufen)\n\n\nLeitfaden zur Methodik Grundschutz++: https://www.bsi.bund.de/SharedDocs/Downloads/DE/BSI/Grundschutz/sonstiges/Methodik_Grundschutz_PlusPlus.html'
# CATALOG_COLUMN['anforderung_status']['comment'] = 'Status der Erfüllung der Anforderung:\n\n- ja = Anforderung ist vollständig erfüllt.\n\n- nein = Anforderung ist nicht erfüllt.\n\n- teilweise = Es wurden bereits einige (nicht alle) Maßnahmen zur Erfüllung der Anforderung umgesetzt.'

CATALOG_COLUMN['massnahmen_umgesetzt']['cell_value_type'] = 'string'
CATALOG_COLUMN['massnahmen_umgesetzt']['headline'] = 'Maßnahmen\nBereits umgesetzt'
CATALOG_COLUMN['massnahmen_umgesetzt']['is_in_sheet'] = True
CATALOG_COLUMN['massnahmen_umgesetzt']['width'] = 55
CATALOG_COLUMN['massnahmen_umgesetzt']['hidden'] = False
CATALOG_COLUMN['massnahmen_umgesetzt']['level'] = 0
CATALOG_COLUMN['massnahmen_umgesetzt']['comment'] = 'Maßnahmen, die bereits zur Erfüllung der Anforderung umgesetzt worden sind.'

CATALOG_COLUMN['massnahmen_geplant']['cell_value_type'] = 'string'
CATALOG_COLUMN['massnahmen_geplant']['headline'] = 'Maßnahmen\nGeplant'
CATALOG_COLUMN['massnahmen_geplant']['is_in_sheet'] = True
CATALOG_COLUMN['massnahmen_geplant']['width'] = 55
CATALOG_COLUMN['massnahmen_geplant']['hidden'] = False
CATALOG_COLUMN['massnahmen_geplant']['level'] = 0
CATALOG_COLUMN['massnahmen_geplant']['comment'] = 'Maßnahmen, die zur Erfüllung der Anforderung geplant und noch nicht umgesetzt sind.'

CATALOG_COLUMN['anmerkungen']['cell_value_type'] = 'string'
CATALOG_COLUMN['anmerkungen']['headline'] = 'Anmerkungen'
CATALOG_COLUMN['anmerkungen']['is_in_sheet'] = True
CATALOG_COLUMN['anmerkungen']['width'] = 55
CATALOG_COLUMN['anmerkungen']['hidden'] = False
CATALOG_COLUMN['anmerkungen']['level'] = 0
CATALOG_COLUMN['anmerkungen']['comment'] = 'Freitextfeld für Anmerkungen wie z.B. zu:\n\n-Spezifizierung der Anforderung\n\n- Fristen der Umsetzung geplanter Maßnahmen\n\n- Verantwortliche der Umsetzung geplanter Maßnahmen'

IMPLEMENTATION_COLUMN['link_anforderung_id']['cell_value_type'] = 'url'
IMPLEMENTATION_COLUMN['link_anforderung_id']['headline'] = 'Anforderung\nID'
IMPLEMENTATION_COLUMN['link_anforderung_id']['is_in_sheet'] = True
IMPLEMENTATION_COLUMN['link_anforderung_id']['width'] = 14
IMPLEMENTATION_COLUMN['link_anforderung_id']['hidden'] = False
IMPLEMENTATION_COLUMN['link_anforderung_id']['level'] = 0
IMPLEMENTATION_COLUMN['link_anforderung_id']['comment'] = 'ID: Eindeutiger Identifikator der Anforderung innerhalb der Praktik und des Themas im Format {Kürzel der Praktik}.{Nummerierung des Themas}.{Nummerierung der Anforderung}. Die ID ergibt sich also aus der Stellung der Anforderung innerhalb des Dokumentes.'

IMPLEMENTATION_COLUMN['alt_identifier']['cell_value_type'] = 'string'
IMPLEMENTATION_COLUMN['alt_identifier']['headline'] = 'Anforderung\nUUID'
IMPLEMENTATION_COLUMN['alt_identifier']['is_in_sheet'] = True
IMPLEMENTATION_COLUMN['alt_identifier']['width'] = 14
IMPLEMENTATION_COLUMN['alt_identifier']['hidden'] = True
IMPLEMENTATION_COLUMN['alt_identifier']['level'] = 0
IMPLEMENTATION_COLUMN['alt_identifier']['comment'] = 'UUID: Über alle Kataloge und Katalogversionen hinweg eindeutige Identifikationsnummer der Anforderung. Diese folgt der Bedeutung der Anforderung, bleibt also auch bei bedeutungserhaltenden Umformulierungen oder Verschiebungen von Anforderungen gleich. Andererseits wird sie ersetzt, wenn sich die Bedeutung der Anforderung wesentlich verändert, selbst wenn ihre Stellung in der Struktur bleibt.'


IMPLEMENTATION_COLUMN['anforderung_titel_ohne_id']['cell_value_type'] = 'string'
IMPLEMENTATION_COLUMN['anforderung_titel_ohne_id']['headline'] = 'Anforderung\nTitel'
IMPLEMENTATION_COLUMN['anforderung_titel_ohne_id']['is_in_sheet'] = True
IMPLEMENTATION_COLUMN['anforderung_titel_ohne_id']['width'] = 30
IMPLEMENTATION_COLUMN['anforderung_titel_ohne_id']['hidden'] = False
IMPLEMENTATION_COLUMN['anforderung_titel_ohne_id']['level'] = 0
IMPLEMENTATION_COLUMN['anforderung_titel_ohne_id']['comment'] = 'Titel: Titel der einzelnen Anforderung. Der Titel beschreibt eine Anforderung kurz und prägnant, so dass sie ohne Blick auf den vollständigen Anforderungsinhalt wiederzuerkennen ist. Titel sind nicht normativ.'

IMPLEMENTATION_COLUMN['text']['cell_value_type'] = 'string'
IMPLEMENTATION_COLUMN['text']['headline'] = 'Anforderung\nText & {Parameter}'
IMPLEMENTATION_COLUMN['text']['is_in_sheet'] = True
IMPLEMENTATION_COLUMN['text']['width'] = 40
IMPLEMENTATION_COLUMN['text']['hidden'] = False
IMPLEMENTATION_COLUMN['text']['level'] = 0
IMPLEMENTATION_COLUMN['text']['comment'] = 'Anforderungen (Controls): Anforderungen sind die zentralen Sicherheitsregeln und werden in OSCAL durch control-Elemente dargestellt. Sie beschreiben Zielzustände oder Grundprinzipien, die erreicht sein müssen, wenn die Anforderung als erfüllt gelten soll. Anforderungen werden durch ihren Titel und den dazugehörigen Anforderungstext beschrieben. Zu einer Anforderung können verschiedene Metadaten zugeordnet sein, z.B. Tags oder Verweise auf andere Anforderungen. Im Grundschutz++ folgt der Text der Anforderungen zudem einem bestimmten Format, der Satzschablone.\n\n{Parameter} zeigen Gestaltungsentscheidungen innerhalb einer Anforderung auf. Das ermöglicht es Katalogautoren und Anwendern auf einen Blick zu sehen wo steuernde Entscheidungen zu treffen sind. Bei einem Audit können die für den Parameter gesetzten Werte automatisiert geprüft werden. Parameter ermöglichen es außerdem Autoren, Anforderungen an spezifischere Kontexte anzupassen. Beispielsweise kann ein Parameter die maximale Anzahl von Fehlversuchen bei der Anmeldung definieren. Verwendet der Anwender hier einen Wert von 10, so kann er für alle Kataloge, die einen Wert von 10 erlauben, eine automatische Dokumentenprüfung bestehen. Diese strukturierte Darstellung unterstützt sowohl die menschliche Lesbarkeit als auch die maschinelle Verarbeitung von Sicherheitsanforderungen und fördert die Wiederverwendbarkeit und Vergleichbarkeit von Sicherheitsanforderungen und -prüfungen. In xlsx-Dokumenten sind Parameter an {geschweiften Klammern} innerhalb des Anforderungstextes zu erkennen.'

IMPLEMENTATION_COLUMN['implementierung_description']['cell_value_type'] = 'string'
IMPLEMENTATION_COLUMN['implementierung_description']['headline'] = 'Implementierung\nDarstellung'
IMPLEMENTATION_COLUMN['implementierung_description']['is_in_sheet'] = True
IMPLEMENTATION_COLUMN['implementierung_description']['width'] = 50
IMPLEMENTATION_COLUMN['implementierung_description']['hidden'] = False
IMPLEMENTATION_COLUMN['implementierung_description']['level'] = 0
IMPLEMENTATION_COLUMN['implementierung_description']['comment'] = 'Implementierung beinhaltet die Anteile description und remarks der Komponentendefinition zu einer Anforderung (sofern vorhanden).\n\nIn den Worten des BSI: Eine OSCAL-Komponentendefinition enthält eine Sammlung von Komponenten. Jede Komponente in einer Komponentendefinition beschreibt, wie eine bestimmte Implementierung einer Hardware, Software, eines Dienstes, einer Richtlinie, eines Prozesses oder einer Prozedur bestimmte Vorschriften aus einem oder mehreren OSCAL-Katalogen oder -Profilen unterstützen oder implementieren kann.\n\nDurch die Veröffentlichung eines Komponentensatzes in einer Komponentendefinition können Produkt- und Serviceanbieter, Richtlinien- und Prozessverantwortliche und andere Personen Informationen über die Implementierung von Anforderungen für ein von ihnen verwaltetes Zielobjekt austauschen. So können Lösungsbeschreibungen für das Thema in System-Sicherheitspläne (SSP) der Institution importiert werden. Diese Informationen können dann bei der technischen oder organisatorischen Implementierung verwendet werden. So muss sich nicht jede Institution die Lösungen "aus den Fingern saugen", die sie zur Umsetzung von Vorschriften einsetzen möchte, sondern kann auf Konzepte und Vorlagen aufbauen.\n\nEs ist wichtig zu beachten, dass Komponentendefinitionen keine tatsächlichen Implementierungen sind; vielmehr beschreiben Komponentendefinitionen eine Implementierung, die innerhalb eines Informationssystems eingesetzt werden kann. Beispielsweise könnte eine Komponente zur Transportverschlüsselung die Information "SSH über TLS 1.3 wird eingesetzt" enthalten. Somit dienen Komponentendefinitionen als Referenzen mit Inhalten, die (z. B. im SSP OSCAL-Modell) zur Entwicklung umfassender und konsistenter Implementierungen (wieder-)verwendet werden können. Sie ersetzen aber nicht das Handeln der für die Informationssicherheit verantwortlichen Stelle.\n\nQuelle: https://github.com/BSI-Bund/Stand-der-Technik-Bibliothek/tree/main/Implementierungsbeschreibungen/Komponenten'

IMPLEMENTATION_COLUMN['implementierung_remarks']['cell_value_type'] = 'string'
IMPLEMENTATION_COLUMN['implementierung_remarks']['headline'] = 'Implementierung\nAnmerkungen'
IMPLEMENTATION_COLUMN['implementierung_remarks']['is_in_sheet'] = True
IMPLEMENTATION_COLUMN['implementierung_remarks']['width'] = 50
IMPLEMENTATION_COLUMN['implementierung_remarks']['hidden'] = False
IMPLEMENTATION_COLUMN['implementierung_remarks']['level'] = 0
IMPLEMENTATION_COLUMN['implementierung_remarks']['comment'] = '-'

IMPLEMENTATION_COLUMN['implementierung_uuid']['cell_value_type'] = 'string'
IMPLEMENTATION_COLUMN['implementierung_uuid']['headline'] = 'Implementierung\nUUID'
IMPLEMENTATION_COLUMN['implementierung_uuid']['is_in_sheet'] = True
IMPLEMENTATION_COLUMN['implementierung_uuid']['width'] = 20
IMPLEMENTATION_COLUMN['implementierung_uuid']['hidden'] = True
IMPLEMENTATION_COLUMN['implementierung_uuid']['level'] = 1
IMPLEMENTATION_COLUMN['implementierung_uuid']['comment'] = '-'

IMPLEMENTATION_COLUMN['implementierung_source']['cell_value_type'] = 'string'
IMPLEMENTATION_COLUMN['implementierung_source']['headline'] = 'Implementierung\nQuelle'
IMPLEMENTATION_COLUMN['implementierung_source']['is_in_sheet'] = True
IMPLEMENTATION_COLUMN['implementierung_source']['width'] = 30
IMPLEMENTATION_COLUMN['implementierung_source']['hidden'] = True
IMPLEMENTATION_COLUMN['implementierung_source']['level'] = 1
IMPLEMENTATION_COLUMN['implementierung_source']['comment'] = '-'

IMPLEMENTATION_COLUMN['implementierung_commit_source']['cell_value_type'] = 'string'
IMPLEMENTATION_COLUMN['implementierung_commit_source']['headline'] = 'Implementierung\nCommit'
IMPLEMENTATION_COLUMN['implementierung_commit_source']['is_in_sheet'] = True
IMPLEMENTATION_COLUMN['implementierung_commit_source']['width'] = 18
IMPLEMENTATION_COLUMN['implementierung_commit_source']['hidden'] = True
IMPLEMENTATION_COLUMN['implementierung_commit_source']['level'] = 1
IMPLEMENTATION_COLUMN['implementierung_commit_source']['comment'] = '-'


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
