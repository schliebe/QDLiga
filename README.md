# QDLiga
Liga-System für eine bekannte Quizapp mit verschiedenen Eingabemöglichkeiten

---
### Inhaltsverzeichnis:
- Info
- Changelog
- Dokumentation

---
### Info
Die QD-Liga ist ein automatisches Ligasystem für eine bekannte Quizapp. Die Spieler messen gegenseitig ihr Wissen und können je nach Leistung am Ende der Saison eine Liga auf- oder absteigen.

---
### Changelog
##### v.0.1.1 - Alpha Test 1 Update 1 (15.11.2020)
- Ergebnisliste zum Liga-Menü hinzugefügt
- Status wird bei Anmeldung direkt auf aktiv, statt inaktiv gesetzt
- EventTimer kann täglich zu einer bestimmten Uhrzeit Events auslösen
  - Täglich um 12 Uhr wird überprüft ob Duelle noch nicht bestätigt wurden
- Weitere Konsolenbefehle hinzugefügt
  - /message: Nachricht an einen Spieler senden
  - /setresult: Ergebnis eines Duells festlegen
- Weitere kleine Änderungen und Bugfixes

##### v0.1 - Alpha Test 1 (07.11.2020)
- 6 Module angelegt:
  - QDLiga
    - Verarbeiten aller wichtigen Informationen
    - Bindeglied zwischen Eingabe (TelegramBot) und Datenbank
  - Datenbank
    - Tabellen für alle wichtigen Daten
    - Automatische Statistik-Liste als View
  - TelegramBot
    - Account anlegen und Status ändern
    - Duelle anzeigen und eintragen
    - Liga-Tabelle generieren und ausgeben lassen
    - Statistik-Tabelle generieren und ausgeben lassen
    - Tutorial ausgeben lassen
  - Logger
  - EventTimer
    - Events aus Datenbank lesen und zum richtigen Zeitpunkt ausführen
  - MediaGenerator
    - Generieren von Liga-Tabellen
    - Generieren der Gesamtstatistik
- Umfangreiche Dokumentation erstellt

---
### Dokumentation
- [Notizen](doc/Notizen.md "Notizen")
- [Bibliotheken](doc/Bibliotheken.md "Bibliotheken")
##### Module:
- [QDLiga](doc/QDLiga.md "QDLiga")
- [Datenbank](doc/Datenbank.md "Datenbank")
- [Logger](doc/Logger.md "Logger")
- [TelegramBot](doc/TelegramBot.md "TelegramBot")
- [EventTimer](doc/EventTimer.md "EventTimer")
- [MediaGenerator](doc/MediaGenerator.md "MediaGenerator")

---