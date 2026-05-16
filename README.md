# Grundschutz++ (GSpp) - elementare Hilfsmittel

Das Bundesamt für Sicherheit in der Informationstechnik (BSI) veröffentlicht und aktualisiert (via commits) in GitHub die GSpp-Anwenderkataloge als [OSCAL](https://pages.nist.gov/OSCAL/learn/)-Datei im [JSON](https://de.wikipedia.org/wiki/JSON)-Format: [grundschutz++-catalog.json](https://github.com/BSI-Bund/Stand-der-Technik-Bibliothek/tree/main/Anwenderkataloge/Grundschutz%2B%2B) 

BSI-Materialien im Kontext GSpp: 
- [Grundschutz in der Informationssicherheit](https://www.bsi.bund.de/DE/Themen/Unternehmen-und-Organisationen/Standards-und-Zertifizierung/Grundschutz-in-der-Informationssicherheit/isms_node.html)
- [Grundschutz++](https://www.bsi.bund.de/DE/Themen/Unternehmen-und-Organisationen/Standards-und-Zertifizierung/Grundschutz-in-der-Informationssicherheit/Grundschutz-Plus-Plus/grundschutz-plus-plus_node.html) mit Meilensteinplan
- [Mindeststandards Bund](https://www.bsi.bund.de/dok/MST)
- [Leitfaden - Methodik Grundschutz++](https://www.bsi.bund.de/SharedDocs/Downloads/DE/BSI/Grundschutz/sonstiges/Methodik_Grundschutz_PlusPlus.pdf)   
- [Stand der Technik (SdT)](https://www.bsi.bund.de/dok/Stand-der-Technik)   
- [OSCAL](https://www.bsi.bund.de/dok/oscal) und [OSCAL FAQ](https://github.com/BSI-Bund/Stand-der-Technik-Bibliothek/blob/main/Dokumentation/OSCAL.md)
- [Handbuch für Autoren der SdT-Bibliothek](https://www.bsi.bund.de/SharedDocs/Downloads/DE/BSI/Stand_der_Technik/Handb%C3%BCcher/Handbuch_f%C3%BCr_Autoren.html)  

## GSpp-Anwenderkatalog als flache json-Datei
Im Ordner `daten/catalog_github_commit_<datum>/ergebnisse/` die Dateien `catalog_<datum>_flattened.json` und `catalog_<datum>_reversed.json`

## GSpp-Anwenderkatalog als control orientierte json-Datei
Im Ordner `daten/catalog_github_commit_<datum>/ergebnisse/` die Datei `control_<datum>_attributes.json`

## GSpp-Anwenderkatalog als Excel-Datei
Im Ordner `daten/catalog_github_commit_<datum>/ergebnisse/` die Datei `catalog_<datum>.xlsx`

Integration der BSI-Implementierungsbeschreibungen (ab Anwenderkatalog commit 20.04.26)

## Änderungen zwischen zwei GSpp-Anwenderkatalog-commits
Im Ordner `daten/diff_reports/` die Datei `diff-report-gs++-<datum a>-<datum b>.md` im Markdown-Format und mit den gleichen Inhalten auch im PDF-Format.

Mit Änderungen ist gemeint:
- Enfernte Anforderungen
- Neue Anforderungen
- Wenn es entfernte und neue Anforderungen geben sollte, mögliche Ähnlichkeiten zwischen beiden
- Veränderte Anforderungsattribute als Übersicht und im Detail 

