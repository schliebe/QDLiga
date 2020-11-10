#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Logger import Logger
import datetime
import pytz
import time
import sched
from threading import Thread


class EventTimer:
    def __init__(self, parent, log, db):
        # Logger setzen
        self.log = log

        # Verbindung zur QDLiga
        self.parent = parent

        # Verbindung zur Datenbank
        self.db = db

        # Zeitzone festlegen
        self.timezone = pytz.timezone('Europe/Berlin')

        # Zeit nach der sich Events wiederholen
        self.REPEAT_TIME = datetime.timedelta(days=21)  # 21 Tage bzw. 3 Wochen

        # Zeitpunkt an dem tägliche Events stattfinden sollen
        self.daily_timestamp = datetime.time(hour=12)  # 12 Uhr mittags

        # Liste aller Events laden
        self.event_list = []
        self.load_event_list()

        # Scheduler für Events
        self.scheduler = sched.scheduler(time.time, time.sleep)
        # Scheduler für tägliche Events
        self.scheduler_daily = sched.scheduler(time.time, time.sleep)

        # Nächstes anstehendes Event
        self.current = None

        # Startet den EventTimer
        self.thread = Thread(target=self.start)  # Events aus DB
        self.thread.daemon = True  # Beendet den Thread mit dem Programm
        self.thread_daily = Thread(target=self.start_daily)  # Tägliches Event
        self.thread_daily.daemon = True
        self.running = True
        self.thread.start()
        self.thread_daily.start()

    def start(self):
        """Nimmt das Event mit dem nächstliegenden Timestamp und startet
        einen Scheduler, der zu diesem Zeitpunkt ein Event auslöst"""
        while self.running:
            # Scheduler mit neustem Event starten
            next = self.get_next_event()
            if not next:
                # Wenn kein nächstes Event gefunden werden kann, wird eine
                # festgelegte Zeitspanne gewartet, bevor es erneut versucht wird
                self.log.log_notification(
                    'Keine weiteren Events in der Event-Liste. '
                    'Unerwünschter Zustand!')
                # Versuchen die Event-Liste erneut zu laden
                self.load_event_list()
                WAIT_TIME = 60  # 1 Minute warten
                time.sleep(WAIT_TIME)
            else:
                # Das nächste Event wird dem Scheduler hinzugefügt.
                # Ein Event löst die execute_event Methode aus, die sowohl den
                # Timestamp, als auch das Event enthält, dass ausgelöst werden
                # soll. Anschließend wird das nächste Event gesucht
                self.current = self.scheduler.enterabs(
                    next[0].timestamp(), 0,
                    self.execute_event, argument=(next[0], next[1]))
                self.log.log_info('Nächstes Event: {}; Timestamp: {}'
                                  .format(next[1], next[0]))
                self.scheduler.run()

    def stop(self):
        self.running = False

    def load_event_list(self):
        """Lädt die gesamte Event-Liste aus der Datenbank.
        Jedes Event ist in einem Tupel gespeichert: (Timestamp, Event)"""
        data = self.db.get_event_list()
        self.event_list.clear()
        for row in data:
            self.add_event(row, utc=True)  # UTC weil aus Datenbank

    def add_event(self, event, utc=False):
        """Fügt ein Event der Event-Liste hinzu.
        Events sind Tupel der Form: (Timestamp, Event).
        Der Timestamp ist im Format YYYY-MM-DD HH:MM:SS
            (z.B. 2020-03-20 12:51:44).
        Der Timestamp in der Datenbank wird in UTC gespeichert und vor dem
        hinzufügen in CET oder CEST umgerechnet (Zeitzone Europe/Berlin),
        sofern dieser nicht bereits Informationen zur Zeitzone enthält"""
        # Zeit-String in Datetime konvertieren
        timestamp = datetime.datetime.strptime(event[0], '%Y-%m-%d %H:%M:%S')
        if utc:
            # Timestamp ist in UTC und muss umgerechnet werden
            # Timestamp in CET bzw. CEST umrechnen
            timestamp = pytz.utc.localize(timestamp).astimezone(self.timezone)
        else:
            # Timestamp ist nicht in UTC und muss nur mit der richtigen
            # Zeitzone versehen werden
            timestamp = self.timezone.localize()

        self.event_list.append((timestamp, event[1]))

    def add_time_offset(self, start_time, offset):
        """Fügt dem übergebenen Zeitpunkt ein gewisses Zeitintervall hinzu.
        Findet in dieser Zeit eine Zeitumstellung statt, wird das Ergebnis
        automatisch so verändert, dass keine Verschiebung der Uhrzeit entsteht.

        Bsp: Tag 1 - 0:00 Uhr (CET) + 1 Tag = Tag 2 - 0:00 Uhr (CEST)
            Die Addition von einem Tag wird so angepasst, dass trotz der
            Zeitverschiebung die selbe Uhrzeit bestehen bleibt."""
        # Zeit in Zeitzone des Zieldatums
        result = self.timezone.normalize(start_time + offset)
        if start_time.dst() != result.dst():
            # Verschiebung der DST (-1h wenn Wechsel auf CET, +1h wenn auf CEST)
            delta = result.dst() - start_time.dst()
            result = result - delta
        return result

    def get_next_event(self):
        """Gibt das Event aus der Event-Liste mit dem am nächsten liegenden
        Timestamp zurück."""
        if len(self.event_list) < 1:
            return None
        next = self.event_list[0]
        for event in self.event_list:
            if event[0] < next[0]:
                next = event
        return next

    def execute_event(self, timestamp, event):
        """Führt je nach ausgelöstem Event verschiedene Funktionen aus.
        Löscht den alten Datenbankeintrag, verschiebt den Timestamp um einen
        festgelegten Wert in die Zukunft und spichert den erneuerten Wert wieder
        in die DB"""
        if self.running:  # Nur ausführen, wenn Thread nicht gestoppt
            # Altes Event aus Event-Liste löschen
            self.event_list.remove((timestamp, event))
            # Je nach Event, andere Funktion ausführen:
            if event == 'HR':
                # Start der Hinrunde
                self.parent.week1()
            elif event == 'RR':
                # Start der Rückrunde
                self.parent.week2()
            elif event == 'P':
                # Pause-Woche
                self.parent.week3()
            elif event == 'RGRP':
                # Regroup
                self.parent.regroup()
            else:
                # Unbekanntes Event
                self.log.log_notification('Unbekanntes Event ausgelöst!')

            # Neuen Zeitpunkt nach Hinzufügen der Wiederholungszeit errechnen
            new_time = self.add_time_offset(timestamp, self.REPEAT_TIME)
            # Neues Event zu Event-Liste hinzufügen
            self.event_list.append((new_time, event))
            # Alten und neuen Timestamp in UTC umrechnen und in String umwandeln
            old_time = datetime.datetime.strftime(
                pytz.utc.normalize(timestamp), '%Y-%m-%d %H:%M:%S')
            new_time = datetime.datetime.strftime(
                pytz.utc.normalize(new_time), '%Y-%m-%d %H:%M:%S')
            # Datenbankeintrag erneuern
            self.db.replace_event(old_time, event, new_time)

    def start_daily(self):
        """Startet einen Scheduler, der täglich zum selben Zeitpunkt ein Event
        auslöst"""
        # Ersten Timestamp aus aktuellem Datum und Ziel-Zeit berechnen
        daily_timestamp = self.timezone.localize(datetime.datetime.combine(
            datetime.date.today(), self.daily_timestamp))
        # Ist dieser bereits vergangen, Timestamp für den nächsten Tag setzen
        if daily_timestamp < self.timezone.localize(datetime.datetime.now()):
            daily_timestamp = self.add_time_offset(
                daily_timestamp, datetime.timedelta(days=1))
        while self.running:
            # Löse das tägliche Event jeden Tag zum selben Zeitpunkt aus
            self.current_daily = self.scheduler_daily.enterabs(
                daily_timestamp.timestamp(), 0, self.parent.daily_reminder)
            self.scheduler_daily.run()
            # Setze neuen Timestamp auf die gleiche Zeit am folgenden Tag
            daily_timestamp = self.add_time_offset(
                daily_timestamp, datetime.timedelta(days=1))
