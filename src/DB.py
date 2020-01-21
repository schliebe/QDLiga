#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3


class DB:
    def __init__(self, log):
        # Logger setzen
        self.log = log

        # Verbindung zur Datenbank
        self.conn = sqlite3.connect('../QDLiga.db', check_same_thread=False)

    def stop(self):
        try:
            self.conn.close()
        except BaseException as e:
            self.log.log_error(
                'Fehler beim schließen der Datenbankverbindung!', e)
            raise e

    def insert_player(self, username):
        """Erstellt einen neuen DB-Eintrag mit dem Username und gibt die P_ID
        zurück."""
        try:
            # Eintrag in DB anlegen
            cursor = self.conn.cursor()
            command = '''
            INSERT INTO Player (Username, Status) 
            VALUES (?, 0)
            '''
            cursor.execute(command, (username,))

            # P_ID herausfinden und zurückgeben
            command = '''
            SELECT P_ID FROM Player WHERE Username = ?
            '''
            cursor.execute(command, (username,))
            result = cursor.fetchall()
            self.conn.commit()
            return result[0][0]
        except BaseException as e:
            self.log.log_error('Fehler beim Einfügen eines neuen Spielers', e)
            raise e

    def add_input_method_to_player(self, p_id, input_method, value):
        """Fügt vorhandenem Eintrag eine neue Eingabemethode hinzu."""
        try:
            # Eintrag in DB erweitern
            cursor = self.conn.cursor()
            command = '''
                UPDATE Player
                SET {} = ?
                WHERE P_ID = ?
                '''.format(input_method)
            cursor.execute(command, (value, p_id))
            self.conn.commit()
        except BaseException as e:
            self.log.log_error('Fehler beim hinzufügen einer Eingabemethode', e)
            raise e

    def check_input_method_used(self, input_method, value):
        """Überprüft, ob der Wert einer Eingabemethode bereits in der Datenbank
        vergeben ist"""
        try:
            cursor = self.conn.cursor()
            command = '''
                SELECT *
                FROM Player
                WHERE {} = ?
                '''.format(input_method)
            cursor.execute(command, (value,))
            if cursor.fetchone():  # Ist Ergebnis der Query None?
                return True  # Eintrag vorhanden, Wert bereits verwendet
            else:
                return False  # Kein Eintrag, Wert also noch frei
        except BaseException as e:
            self.log.log_error('Fehler beim überprüfen der Eingabemethode', e)
            raise e
