# EventTimer

Der EventTimer verwaltet alle zeitlichen Events, die in der QDLiga passieren.

---
### Events
Die verschiedenen Events, die ausgelöst werden können sind:

| Abkürzung | Event               | Zeitpunkt           | Wiederholung  |
| --------- | ------------------- | ------------------- | ------------- |
| HR        | Start der Hinrunde  | W1, Montag, 0 Uhr   | Nach 3 Wochen |
| RR        | Start der Rückrunde | W2, Montag, 0 Uhr   | Nach 3 Wochen |
| P         | Pause               | W3, Montag, 0 Uhr   | Nach 3 Wochen |
| RGRP      | Regroup             | W3, Sonntag, 23 Uhr  | Nach 3 Wochen |

### Tägliche Events
Neben den normalen Events können auch jeden Tag weitere Events zu einem bestimmten Zeitpunkt (im Moment `12:00` mittags) ausgelöst werden

---