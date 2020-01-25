#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Logger import Logger
from DB import DB
from TelegramBot import TelegramBot


class QDLiga:
    def __init__(self):
        # Logger erstellen
        self.log = Logger()

        # Alle Module mit entsprechenden Referenzen laden
        self.log.log_info('Starte QDLiga...')

        self.log.log_info('Verbindung zur Datenbank herstellen...')
        self.db = DB(self.log)
        self.log.log_info('Verbindung zur Datenbank hergestellt!')

        self.log.log_info('Starte Telegram Bot...')
        self.telegramBot = TelegramBot(self, self.log)
        self.log.log_info('Telegram Bot gestartet!')

        self.log.log_info('QDLiga gestartet!')
        while True:
            text = input()
            self.console_input(text)

    def stop(self):
        self.log.log_info('QDLiga stoppen...')

        self.log.log_info('Schließe Verbindung zur Datenbank...')
        self.db.stop()
        self.log.log_info('Verbindung zur Datenbank geschlossen!')

        self.log.log_info('Beende Telegram Bot...')
        self.telegramBot.stop()
        self.log.log_info('Telegram Bot beendet!')

        self.log.log_info('QDLiga wurde gestoppt!')

        self.log.stop()
        import sys
        sys.exit()
        # TODO Skript läuft noch weiter?

    def console_input(self, text):
        # Überprüft Konsoleneingabe auf bekannte Befehle
        if text == '/stop':  # Beendet die QDLiga und alle dazugehörigen Module
            self.stop()

    def register_new_player(self, username):
        """Fügt einen neuen Spieler der Datenbank hinzu und gibt dessen P_ID
        zurück"""
        try:
            p_id = self.db.insert_player(username)
            return p_id
        except BaseException as e:
            raise e

    def add_input_method(self, p_id, input_method, value):
        """Fügt einem Spieler eine neue Eingabemethode hinzu"""
        try:
            self.db.add_input_method_to_player(p_id, input_method, value)
        except BaseException as e:
            raise e

    def check_input_method_used(self, input_method, value):
        """Überprüft, ob der Wert für die Eingabemethode schon verwendet wird"""
        try:
            return self.db.check_input_method_used(input_method, value)
        except BaseException as e:
            raise e


if __name__ == "__main__":
    QDLiga()
