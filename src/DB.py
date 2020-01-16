#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3


class DB:
    def __init__(self):
        # Verbindung zur Datenbank
        self.conn = sqlite3.connect('../QDLiga.db', check_same_thread=False)

    def stop(self):
        try:
            self.conn.close()
        except BaseException as e:
            print('Fehler beim schließen der Datenbankverbindung!')
            print(e)
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
            print('Fehler beim Einfügen eines neuen Spielers')
            print(e)
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
            print('Fehler beim hinzufügen einer Eingabemethode')
            print(e)
            raise e
