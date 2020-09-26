# Datenbank
Für die Datenbank wird SQLite verwendet.\
Die Datenbank befindet sich im Hauptordner in der Datei 'QDLiga.db'

---
### Tabellen:
- [Player](#player "Player")
- [League](#league "League")
- [InLeague](#inleague "InLeague")
- [Match](#match "Match")
- [Settings](#settings "Settings")
- [Events](#events "Events")
- [sqlite_sequence](#sqlite_sequence "sqlite_sequence")

---
### Player
Diese Tabelle enthält alle Spieler und deren Daten\
`P_ID` Player_ID\
`Username` QD-Benutzername des Spielers\
`Status` Teilnahmestatus des Spielers (→ [Teilnahmestatus](#teilnahmestatus "Teilnahmestatus"))\
`TelegramID` chatID des Spielers bei Telegram
> Username, TelegramID sind einmalig\
> TelegramID darf NULL sein

---
### League
Diese Tabelle enthält die Ligen in denen gespielt wird\
`L_ID` League_ID\
`Name` Name der Liga\
`Season` Saison in der diese Liga gespielt wird\
`Players` Anzahl der Spieler in der Liga\
`Level` Höhe der Liga in der Rangliste, 1 entspricht 1. Liga, etc.
> Keines der Felder darf NULL sein

---
### InLeague
Diese Tabelle enthält welche Spieler sich in welcher Liga befinden\
`League` ID der [Liga](#league "League") in der sich der Spieler befindet\
`Player` ID des [Spielers](#player "Player") der in der Liga spielt
> League und Player sind Fremdschlüssel\
> Keines der Felder darf NULL sein

---
### Match
Diese Tabelle enthält alle Ergebnisse der einzelnen Spiele im Ligabetrieb\
`M_ID` Match_ID\
`League` ID der [Liga](#league "League") in der das Spiel stattfindet\
`Round` Runde in der das Spiel stattfindet (→ [Round](#round "Round"))\
`P1`,`P2` IDs der [Spieler](#player "Player") die gegeneinander spielen\
`Res1`,`Res2` Das Ergebnis des Spiels für den jeweiligen Spieler\
`Pts1`,`Pts2` Die erhaltenen Punkte des jeweiligen Spielers\
`Verified` Der aktuelle Verifizierungsstatus (→ [Verified](#verified "Verified"))
> League, Sp1 und Sp2 sind Fremdschlüssel\
> Nur die Felder Res1, Res2, Pts1 und Pts2 dürfen NULL sein

---
### Settings
Diese Tabelle enthält genau einen Eintrag mit den aktuellen Einstellungen des Bots\
`Season` Saison in der sich die QD-Liga momentan befindet\
`Round` Die Runde der Aktuellen Saison (→ [Round](#round "Round"))
> Keines der Felder darf NULL sein

---
### Events
Diese Tabelle enthält die Events, die zu einem bestimmten Zeitpunkt vom EventTimer ausgeführt werden sollen\
`Timestamp` Zeitstempel wann das Event stattfinden soll (in UTC)\
`Event` Das Event das stattfinden soll (→ [Event](#event "Event"))
> Keines der Felder darf NULL sein
> Jedes Event darf nur einmal vorhanden sein

---
### Stats
Diese Tabelle ist eine View, die die zusammengerechneten Ergebnisse aller Spieler enthält\
`P_ID` Player_ID\
`Matches` Anzahl gespielter Duelle\
`Win` Anzahl Siege\
`Draw` Anzahl Unentschieden\
`Lose` Anzahl Niederlagen\
`NotPlayed` Anzahl nicht angetretener Spiele\
`Correct` Anzahl richtig beantworteter Fragen\
`Perfect` Anzahl perfekte Spiele\
`Points` Anzahl erhaltene Punkte

---
### sqlite_sequence
Diese Tabelle wird nur von SQLite verwendet und enthält die jeweils letzte mit AUTO_INCREMENT vergebene ID

---
### Erklärungen
#### Teilnahmestatus
| Status | Bedeutung                                         |
| ------ | ------------------------------------------------- |
| 0      | Spieler nimmt nächste Saison nicht teil (Inaktiv) |
| 1      | Spieler nimmt nächste Saison teil (Aktiv)         |

#### Round
| Runde | Bedeutung |
| ----- | --------- |
| 0     | Pause     |
| 1     | Hinrunde  |
| 2     | Rückrunde |

#### Verified
| Verified | Bedeutung                                              |
| -------- | ------------------------------------------------------ |
| 0        | Keiner hat ein Ergebnis eingetragen                    |
| 1        | Sp1 hat ein Ergebnis eingetragen                       |
| 2        | Sp2 hat ein Ergebnis eingetragen                       |
| 3        | Beide haben das selbe Ergebnis eingetragen             |
| 4        | Sp2 hat ein anderes Ergebnis als zuvor Sp1 eingetragen |
| 5        | Sp1 hat ein anderes Ergebnis als zuvor Sp2 eingetragen |

#### Event
[Die verschiedenen Werte von Event können hier nachgelesen werden](/doc/EventTimer.md#Events "EventTimer/Events")

---