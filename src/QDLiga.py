#!/usr/bin/env python
# -*- coding: utf-8 -*-

from DB import DB
from TelegramBot import TelegramBot


class QDLiga:
    def __init__(self):
        # Alle Module mit entsprechenden Referenzen laden
        print('Starte QDLiga...')

        print('Verbindung zur Datenbank herstellen...')
        self.db = DB()
        print('Verbindung zur Datenbank hergestellt!')

        print('Starte Telegram Bot...')
        self.telegramBot = TelegramBot(self)
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

    def test(self, input):
        return self.db.insert_player(input)


if __name__ == "__main__":
    QDLiga()
