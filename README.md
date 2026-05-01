# Werkzeuge für Grundschutz++ (GSpp)

Das Bundesamt für Sicherheit in der Informationstechnik (BSI) veröffentlicht und aktualisiert (via commits) in GitHub die GSpp-Anwenderkataloge im json-Format: [grundschutz++-catalog.json](https://github.com/BSI-Bund/Stand-der-Technik-Bibliothek/tree/main/Anwenderkataloge/Grundschutz%2B%2B) 

## GSpp-Anwenderkatalog als flache json-Datei
Im Ordner `daten/catalog_github_commit_<datum>/ergebnisse/` die Dateien `catalog_<datum>_flattened.json` und `catalog_<datum>_reversed.json`

## GSpp-Anwenderkatalog als Excel-Datei
Im Ordner `daten/catalog_github_commit_<datum>/ergebnisse/` die Datei `catalog_<datum>.xlsx`

## Änderungen zwischen zwei GSpp-Anwenderkatalog-commits
Im Ordner `daten/diff_reports/` die Datei `diff-report-gs++-<datum a>-<datum b>.md` im Markdown-Format und mit den gleichen Inhalten auch im PDF-Format.

Mit Änderungen ist gemeint:
- Enfernte Anforderungen
- Neue Anforderungen
- Wenn es entfernte und neue Anforderungen geben sollte, mögliche Ähnlichkeiten zwischen beiden
- Veränderte Anforderungsattribute als Übersicht und im Detail 

