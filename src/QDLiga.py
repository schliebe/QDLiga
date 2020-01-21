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
        print('Starte QDLiga...')

        print('Verbindung zur Datenbank herstellen...')
        self.db = DB(self.log)
        print('Verbindung zur Datenbank hergestellt!')

        print('Starte Telegram Bot...')
        self.telegramBot = TelegramBot(self, self.log)
        print('Telegram Bot gestartet!')

        print('QDLiga gestartet!')

    def stop(self):
        print('QDLiga stoppen...')

        print('Schließe Verbindung zur Datenbank...')
        self.db.stop()
        print('Verbindung zur Datenbank geschlossen!')

        print('Beende Telegram Bot...')
        self.telegramBot.stop()
        print('Telegram Bot beendet!')

        print('QDLiga wurde gestoppt!')
        import sys
        sys.exit()
        # TODO Skript läuft noch weiter?

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
