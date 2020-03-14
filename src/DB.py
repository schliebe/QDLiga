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

    def load_time_settings(self):
        """Gibt die aktuelle Saison und Runde aus der Datebank zurück"""
        try:
            cursor = self.conn.cursor()
            command = '''
                SELECT Season, Round
                FROM Settings
                '''
            cursor.execute(command)
            season, round = cursor.fetchone()
            return season, round
        except BaseException as e:
            self.log.log_error('Fehler beim laden der Saison und Runde', e)
            raise e

    def set_time_settings(self, season, round):
        """Schreibt die aktuelle Saison und Runde in die Datenbank.
        Verändert den einzigen Eintrag der Einstellungs-Tabelle"""
        try:
            cursor = self.conn.cursor()
            command = '''
                UPDATE Settings
                SET Season = ?, Round = ?'''
            cursor.execute(command, (season, round))
            self.conn.commit()
        except BaseException as e:
            self.log.log_error('Fehler beim speichern der Saison und Runde', e)
            raise e

    def get_p_id(self, input_method, value):
        """Gibt die p_id eines Spielers anhand einer Eingabemethode zurück.
        Gibt None zurück, wenn nicht vorhanden"""
        try:
            cursor = self.conn.cursor()
            command = '''
                SELECT P_ID
                FROM Player
                WHERE {} = ?
                '''.format(input_method)
            cursor.execute(command, (value,))
            p_id = cursor.fetchone()
            if p_id:
                return p_id[0]  # p_id zurückgeben, falls forhanden
            else:
                return None  # None, sonst
        except BaseException as e:
            self.log.log_error('Fehler beim auslesen der p_id', e)
            raise e

    def get_status(self, p_id):
        """Gibt den Status eines Spielers zurück"""
        try:
            cursor = self.conn.cursor()
            command = '''
                SELECT Status
                FROM Player
                WHERE P_ID = ?
                '''
            cursor.execute(command, (p_id,))
            status = cursor.fetchone()
            if status:
                return status[0]
            else:
                raise BaseException('Status konnte nicht ausgelesen werden.')
        except BaseException as e:
            self.log.log_error('Fehler beim auslesen des Status', e)

    def set_status(self, p_id, status):
        """Setzt den Status eines Spielers"""
        try:
            cursor = self.conn.cursor()
            command = '''
                UPDATE Player
                SET Status = ?
                WHERE P_ID = ?
                '''
            cursor.execute(command, (status, p_id))
            self.conn.commit()
        except BaseException as e:
            self.log.log_error('Fehler beim setzen des Status', e)
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
