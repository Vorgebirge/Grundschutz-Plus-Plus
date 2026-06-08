# Grundschutz++ (GSpp) - elementare Hilfsmittel

Das Bundesamt für Sicherheit in der Informationstechnik (BSI) veröffentlicht und aktualisiert sukzessive (via commits) in GitHub die GSpp-Anwenderkataloge als OSCAL-Datei ([NIST](https://pages.nist.gov/OSCAL/learn/), [OSCAL Foundation](https://oscalfoundation.org/)) im [JSON](https://de.wikipedia.org/wiki/JSON)-Format: [grundschutz++-catalog.json](https://github.com/BSI-Bund/Stand-der-Technik-Bibliothek/tree/main/Anwenderkataloge/Grundschutz%2B%2B) 

BSI-Materialien im Kontext GSpp: 
- [Grundschutz in der Informationssicherheit](https://www.bsi.bund.de/DE/Themen/Unternehmen-und-Organisationen/Standards-und-Zertifizierung/Grundschutz-in-der-Informationssicherheit/isms_node.html)
- [Grundschutz++](https://www.bsi.bund.de/DE/Themen/Unternehmen-und-Organisationen/Standards-und-Zertifizierung/Grundschutz-in-der-Informationssicherheit/Grundschutz-Plus-Plus/grundschutz-plus-plus_node.html) mit Meilensteinplan
- [Mindeststandards Bund](https://www.bsi.bund.de/dok/MST)
- [Leitfaden - Methodik Grundschutz++](https://www.bsi.bund.de/SharedDocs/Downloads/DE/BSI/Grundschutz/sonstiges/Methodik_Grundschutz_PlusPlus.pdf)   
- [Stand der Technik (SdT)](https://www.bsi.bund.de/dok/Stand-der-Technik)   
- [OSCAL](https://www.bsi.bund.de/dok/oscal) und [OSCAL FAQ](https://github.com/BSI-Bund/Stand-der-Technik-Bibliothek/blob/main/Dokumentation/OSCAL.md)
- [Handbuch für Autoren der SdT-Bibliothek](https://www.bsi.bund.de/SharedDocs/Downloads/DE/BSI/Stand_der_Technik/Handb%C3%BCcher/Handbuch_f%C3%BCr_Autoren.html)  

## Aktueller GSpp-Anwenderkatalog als Excel-Datei und Diffs

Aktueller GSpp-Anwenderkatalog und Implementierungsbeschreibungen als Excel-Datei: `Grundschutz++-catalog.xlsx` 

Unterschiede zum vorigen GSpp-Anwenderkatalog: `Diff_Report_Grundschutz++-catalog.md` und `Diff_Report_Grundschutz++-catalog.pdf` Zu Details siehe unten unter *Unterschiede zwischen zwei GSpp-Anwenderkatalog-commits*

## GSpp-Anwenderkatalog als flache json-Datei
Im Ordner `daten/catalog_github_commit_<datum>/ergebnisse/` die Dateien `catalog_<datum>_flattened.json` und `catalog_<datum>_reversed.json`

## GSpp-Anwenderkatalog als control orientierte json-Datei
Im Ordner `daten/catalog_github_commit_<datum>/ergebnisse/` die Datei `control_<datum>_attributes.json`

## GSpp-Anwenderkatalog als Excel-Datei
Im Ordner `daten/catalog_github_commit_<datum>/ergebnisse/` die Datei `catalog_<datum>.xlsx`

Integration der BSI-Implementierungsbeschreibungen (ab Anwenderkatalog commit 20.04.26)

## Unterschiede zwischen zwei GSpp-Anwenderkatalog-commits
Im Ordner `daten/diff_reports/` die Datei `diff-report-gs++-<datum a>-<datum b>.md` im Markdown-Format und mit den gleichen Inhalten auch im PDF-Format.

- Anforderungen-IDs in commit A, die es in commit B nicht mehr gibt
   - Auch Nennung der commit B Anforderungen UUID, die identisch zu den entfernten commit A Anforderungen UUID sind
   - Auch Nennung der commit B Anforderungen, die den entfernten
     commit A Anforderungen inhaltlich ählich sind (wenn das Maß [Kosinus-Ähnlichkeit](https://de.wikipedia.org/wiki/Kosinus-%C3%84hnlichkeit) > 0,5)
   
   Dies sind Indikatoren, dass die Inhalte zu entfernten commit A Anforderungen-IDs in commit B Anforderungen weiter vorliegen.
- Anforderungen-IDs in commit B, die es in commit A noch nicht gegeben hat  
   - Auch Nennung der commit A Anforderungen UUID, die identisch zu den neuen commit B Anforderungen UUID sind
   - Auch Nennung der commit A Anforderungen, die den neuen
     commit B Anforderungen inhaltlich ähnlich sind (wenn das Maß  Kosinus-Ähnlichkeit > 0,5)
    
    Dies sind Indikatoren, dass die Inhalte zu neuen commit B Anforderungen-IDs bereits in A Anforderungen vorlagen.
- Veränderte Anforderungsattribute als Übersicht und im Detail. Beim oft inhaltlich umfangreichen Attribut `guidance` werden entfernte und ergänzte Textanteile hervorgehoben. 

