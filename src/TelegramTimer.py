#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from threading import Thread


class TelegramTimer:
    def __init__(self, bot):
        self.bot = bot
        self.timeout_list = []  # Liste der aktiven Nutzer (geordnet nach Zeit)
        self.timeout_timestamp = {}  # Timestamps der Nutzer
        self.TIMEOUT_INTERVAL = 600  # Timeout-Zeit in Sekunden
        self.CHECK_INTERVAL = 30  # Überprüfungs-Interval in Sekunden
        self.running = True
        t = Thread(target=self.check_loop)
        t.start()

    def check_loop(self):
        while self.running:  # Endlosschleife
            time.sleep(self.CHECK_INTERVAL)  # Abstand zwischen Überprüfungen
            if len(self.timeout_list) == 0:
                continue  # Überspringen, wenn Liste leer
            elem = self.timeout_list[0]
            if self.timeout_timestamp[elem] < time.time():
                self.timeout(elem)  # Timeout auslösen wenn Timestamp abgelaufen

    def stop(self):
        self.running = False

    def update(self, chat_id):
        # Erneuert/erstellt den Timestamp des Nutzers und setzt ihn ans Ende
        # der Timeout-Liste
        if chat_id in self.timeout_list:
            self.timeout_list.remove(chat_id)
        self.timeout_timestamp[chat_id] = time.time() + self.TIMEOUT_INTERVAL
        self.timeout_list.append(chat_id)

    def timeout(self, chat_id):
        # Entfernt den Nutzer aus den Listen und löst im TelegramBot einen
        # Timeout aus
        self.timeout_list.remove(chat_id)
        self.timeout_timestamp.pop(chat_id, None)
        self.bot.timeout(chat_id)
