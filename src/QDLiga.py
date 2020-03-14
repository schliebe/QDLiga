#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Logger import Logger
from DB import DB
from TelegramBot import TelegramBot


class QDLiga:
    def __init__(self):
        def load_token():
            # Lade Tokens aus Token.txt
            tokens = {'Telegram_Bot_Token': ''}  # Default Werte
            file = open('..\\Token.txt', 'r')
            for line in file:
                key, value = line.split('=', 1)
                tokens[key] = value
            file.close()
            return tokens

        # Logger erstellen
        self.log = Logger()

        # Tokens laden
        token = load_token()

        # Alle Module mit entsprechenden Referenzen laden
        self.log.log_info('Starte QDLiga...')

        self.log.log_info('Verbindung zur Datenbank herstellen...')
        self.db = DB(self.log)
        self.log.log_info('Verbindung zur Datenbank hergestellt!')

        # Aktuelle Saison und Runde laden
        self.season, self.round = self.db.load_time_settings()
        self.log.log_info('Saison: {}, Runde {}'
                          .format(self.season, self.round))

        self.log.log_info('Starte Telegram Bot...')
        self.telegramBot = TelegramBot(self, self.log,
                                       token['Telegram_Bot_Token'])
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

        self.log.log_info('Bitte warten, bis alle Threads beendet wurden...')

        self.log.stop()
        import sys
        sys.exit()

    def console_input(self, text):
        """Überprüft Konsoleneingabe auf bekannte Befehle"""
        if text == '/stop':  # Beendet die QDLiga und alle dazugehörigen Module
            self.stop()

    def get_p_id(self, username):
        """Lädt die ID eines Spielers anhand des Nutzernamens aus der
        Datenbank"""
        try:
            p_id = self.db.get_p_id(username)
            return p_id
        except BaseException as e:
            raise e

    def get_p_id_from_input(self, input_method, value):
        """Lädt die ID eines Spielers anhand einer Eingabemethode aus der
        Datenbank"""
        try:
            p_id = self.db.get_p_id_from_input(input_method, value)
            return p_id
        except BaseException as e:
            raise e

    def get_status(self, p_id):
        """Lädt den Status eines Spielers aus der Datenbank"""
        try:
            status = self.db.get_status(p_id)
            return status
        except BaseException as e:
            raise e

    def set_status(self, p_id, status):
        """Setzt den Status eines Spielers in der Datenbank.

        status: 0 = Inaktiv, 1 = Aktiv

        1) Wird der Status auf Aktiv gesetzt, wird der Spieler der Warteliste
        hinzugefügt, wenn er aktuell in keiner Liga spielt.
        2) Wird der Status auf Inaktiv gesetzt, wird der Spieler von der
        Warteliste entfernt, sofern er sich auf dieser befindet. Spielt er
        aktuell in einer Liga, wird er am Ende der aktuellen Saison nicht mehr
        neu eingeteilt.

        Das ändern des Status kann ohne Konsequenzen geändert werden, sofern der
        Spieler gerade in einer Liga spielt. Befindet er sich auf der
        Warteliste, verliert er seine aktuelle Position, wenn er den Status auf
        Inaktiv ändert."""
        try:
            in_queue = self.db.is_in_queue(p_id)
            in_league = self.db.is_in_league(p_id, self.season)
            self.db.set_status(p_id, status)
            if status == 0:
                if in_queue:
                    self.db.remove_from_queue(p_id)
            elif status == 1:
                if not in_league:
                    if not in_queue:
                        self.db.add_to_queue(p_id)
        except BaseException as e:
            raise e

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
