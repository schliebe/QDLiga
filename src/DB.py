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

    def get_p_id(self, username):
        """Gibt die p_id eines Spielers anhand des Nutzernamen zurück.
        Gibt None zurück, wenn nicht vorhanden"""
        try:
            cursor = self.conn.cursor()
            command = '''
                SELECT P_ID
                FROM Player
                WHERE Username = ?
                '''
            cursor.execute(command, (username,))
            p_id = cursor.fetchone()
            if p_id:
                return p_id[0]  # p_id zurückgeben, falls forhanden
            else:
                return None  # None, sonst
        except BaseException as e:
            self.log.log_error('Fehler beim auslesen der p_id', e)
            raise e

    def get_p_id_from_input(self, input_method, value):
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

    def get_l_id(self, name, season):
        cursor = self.conn.cursor()
        command = '''
            SELECT L_ID
            FROM League
            WHERE Name = ? AND Season = ?
            '''
        cursor.execute(command, (name, season))
        l_id = cursor.fetchone()
        if l_id:
            return l_id[0]  # l_id zurückgeben, falls forhanden
        else:
            return None  # None, sonst

    def get_event_list(self):
        """Gibt eine Liste aller Einträge aus der Tabelle Events zurück.
        Die einzelnen Einträge sind Tupel der Form: (Timestamp, Event)."""
        try:
            event_list = []
            cursor = self.conn.cursor()
            command = '''
                SELECT *
                FROM Events
                '''
            cursor.execute(command)
            data = cursor.fetchall()
            for row in data:
                event_list.append(row)
            return event_list
        except BaseException as e:
            self.log.log_error('Fehler beim Auslesen der Events', e)

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
            self.conn.commit()

            # P_ID herausfinden und zurückgeben
            command = '''
            SELECT P_ID FROM Player WHERE Username = ?
            '''
            cursor.execute(command, (username,))
            result = cursor.fetchall()
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

    def is_in_queue(self, p_id):
        """Überprüft ob sich der Speiler mit der übergebenen ID in der
        Warteliste befindet (True), oder nicht (False).

        Die Warteliste wird als Liga mit L_ID 0 in der Datenbank gespeichert"""
        try:
            cursor = self.conn.cursor()
            command = '''
                SELECT *
                FROM InLeague
                WHERE Player = ? AND League = 0'''
            cursor.execute(command, (p_id,))
            if cursor.fetchone():  # Wenn Ergebnis nicht leer, Spieler auf Liste
                return True
            else:
                return False
        except BaseException as e:
            self.log.log_error('Fehler beim überprüfen der Warteliste', e)
            raise e

    def is_in_league(self, p_id, season):
        """Überprüft ob der Spieler mit der übergebenen ID in der angegebenen
        Saison in einer Liga gespielt hat"""
        try:
            cursor = self.conn.cursor()
            command = '''
                SELECT *
                FROM InLeague
                WHERE Player = ?
                 AND League IN (SELECT L_ID
                                FROM League
                                WHERE Season = ?)'''
            cursor.execute(command, (p_id, season))
            if cursor.fetchone():  # Wenn Ergebnis nicht leer, Spieler in Liga
                return True
            else:
                return False
        except BaseException as e:
            self.log.log_error('Fehler beim überprüfen der Ligazugehörigkeit',
                               e)
            raise e

    def add_to_league(self, l_id, p_id):
        """Fügt einen Spieler einer Liga hinzu.
        Erhöht den Spieler-Zähler der Liga"""
        try:
            cursor = self.conn.cursor()
            command = '''
                INSERT INTO InLeague (League, Player)
                VALUES (?, ?)
                '''
            cursor.execute(command, (l_id, p_id))
            command = '''
                UPDATE League
                SET Players = Players + 1
                WHERE L_ID = ?
                '''
            cursor.execute(command, (l_id,))
            self.conn.commit()
        except BaseException as e:
            self.log.log_error('Fehler beim hinzufügen zur Liga', e)
            raise e

    def add_to_queue(self, p_id):
        """Fügt einen Spieler der Warteliste hinzu.
        Die Warteliste ist eine Liga mit der L_ID 0"""
        try:
            self.add_to_league(0, p_id)
        except BaseException as e:
            self.log.log_error('Fehler beim hinzufügen zur Warteliste', e)
            raise e

    def remove_from_queue(self, p_id):
        """Entfernt einen Spieler von der Warteliste.
        Die Warteliste ist eine Liga mit der L_ID 0.
        Spieler-Zähler der Warteliste um 1 verringern"""
        try:
            cursor = self.conn.cursor()
            command = '''
                DELETE FROM InLeague
                WHERE League = 0 AND Player = ?
                '''
            cursor.execute(command, (p_id,))
            command = '''
                UPDATE League
                SET Players = Players - 1
                WHERE L_ID = 0
                '''
            cursor.execute(command)
            self.conn.commit()
        except BaseException as e:
            self.log.log_error('Fehler beim entfernen von Warteliste', e)
            raise e

    def create_league(self, name, season, level):
        """Legt eine neue Liga in der Datenbank an und gibt die L_ID zurück"""
        try:
            # Liga in Datenbank anlegen
            cursor = self.conn.cursor()
            command = '''
                INSERT INTO League (Name, Season, Level)
                VALUES (?, ?, ?)
                '''
            cursor.execute(command, (name, season, level))
            self.conn.commit()

            return self.get_l_id(name, season)
        except BaseException as e:
            self.log.log_error('Fehler beim anlegen der Liga', e)
            raise e

    def replace_event(self, old_time, event, new_time=None):
        """Löscht das übergebene Event aus der Datenbank und legt einen neuen
        Eintrag mit neuem Timestamp an, sofern ein Wert übergeben wird.
        Der alte, sowie der neue Timestamp müssen bereits korrekt formatiert
        und in utc umgerechnet sein"""
        try:
            # Eintrag aus der BD entfernen, sofern vorhanden
            cursor = self.conn.cursor()
            command = '''
                DELETE FROM Events
                WHERE Timestamp = ? AND Event = ?
                '''
            cursor.execute(command, (old_time, event))
            if new_time:
                command = '''
                    INSERT INTO Events (Timestamp, Event)
                    VALUES (?, ?)'''
                cursor.execute(command, (new_time, event))
            self.conn.commit()
        except BaseException as e:
            self.log.log_error('Fehler beim erneuern eines Events in der DB', e)

    def get_league_table(self, l_id):
        """Gibt die aktuelle Tabelle der angegebenen Liga zurück.
        Es werden nur Spiele betrachtet, die bereits abgeschlossen sind.
        Das Ergebnis ist eine sortierte Liste von Tupeln der Form:
            (Platz, P_ID, Spiele, Siege, Unentschieden, Nicht gespielt, Richtig,
            Perfekt, Punkte)"""
        try:
            cursor = self.conn.cursor()
            command = '''
                SELECT Players.P_ID AS P_ID, IFNULL(Matches, 0) AS Matches,
                    IFNULL(Win, 0) AS Win, IFNULL(Draw, 0) AS Draw,
                    IFNULL(Lose, 0) AS Lose, IFNULL(NotPlayed, 0) AS NotPlayed,
                    IFNULL(Correct, 0) AS Correct,
                    IFNULL(Perfect, 0) AS Perfect, IFNULL(Points, 0) AS Points
                FROM (
                    SELECT Player AS P_ID
                    FROM InLeague
                    WHERE League = ?
                ) AS Players
                LEFT JOIN (
                    SELECT P_ID, COUNT(P_ID) AS Matches, SUM(Win) AS Win,
                        SUM(Draw) AS Draw, SUM(Lose) AS Lose,
                        SUM(NotPlayed) AS NotPlayed, SUM(Res) AS Correct,
                        SUM(Perfect) AS Perfect, SUM(Pts) AS Points
                    FROM (
                        SELECT P_ID, Res, Pts,
                            CASE
                                WHEN Res > Enemy THEN 1
                                ELSE 0
                            END AS Win,
                            CASE
                                WHEN Res = Enemy THEN 1
                                ELSE 0
                            END AS Draw,
                            CASE
                                WHEN Res = 0 THEN 0
                                WHEN Res < Enemy THEN 1
                                ELSE 0
                            END AS Lose,
                            CASE
                                WHEN Pts = 0 THEN 1
                                ELSE 0
                            END AS NotPlayed,
                            CASE
                                WHEN Res = 18 THEN 1
                                ELSE 0
                            END AS Perfect
                        FROM (
                            SELECT P1 AS P_ID, Res1 AS Res, Res2 AS Enemy,
                                Pts1 AS Pts
                            FROM Match
                            WHERE League = ? AND Verified = 3
                            UNION ALL
                            SELECT P2 AS P_ID, Res2 AS Res, Res1 AS Enemy,
                                Pts2 AS Pts
                            FROM Match
                            WHERE League = ? AND Verified = 3)
                        )
                    GROUP BY P_ID
                    ) AS Stat
                ON Players.P_ID = Stat.P_ID
                ORDER BY Points DESC, Correct DESC, Win DESC, Perfect DESC,
                    NotPlayed ASC'''
            cursor.execute(command, (l_id, l_id, l_id))
            table = []
            for row in cursor.fetchall():
                table.append(row)
            return table
        except BaseException as e:
            self.log.log_error('Fehler beim laden der Tabelle', e)
            raise e
