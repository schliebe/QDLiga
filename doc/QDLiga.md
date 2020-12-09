# QDLiga
QDLiga ist das Hauptmodul der QDLiga und dient als Schnittstelle zwischen allen anderen Modulen.\
QDLiga startet zu Beginn alle Module und sorgt beim beenden dafür, dass alle Module gestoppt werden.\
Es ist möglich in der Konsole Befehle einzugeben

---
### Verbundene Module:
- [Logger](Logger.md "Logger")
- [Datenbank](Datenbank.md "Datenbank")
- [TelegramBot](TelegramBot.md "TelegramBot")
- [EventTimer](EventTimer.md "EventTimer")
- [MediaGenerator](MediaGenerator.md "MediaGenerator")

---
### Befehle:
- /stop - Die QDLiga und alle zugehörigen Module beenden
- /message - Sendet eine Nachricht an einen Spieler
- /running - Gibt eine Liste aller noch nicht bestätigten Spiele aus
- /setresult - Das Ergebnis eines Duells festlegen
- /rename - Ändert den Nutzernamen eines Spielers
- /help - Die Befehlsliste aufrufen

---