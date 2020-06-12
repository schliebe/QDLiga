#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Logger import Logger
from DB import DB
from TelegramBot import TelegramBot
from EventTimer import EventTimer


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

        self.log.log_info('Starte EventTimer...')
        self.eventTimer = EventTimer(self, self.log, self.db)
        self.log.log_info('EventTimer gestartet!')

        self.log.log_info('QDLiga gestartet!')
        while True:
            text = input()
            self.console_input(text)

    def stop(self):
        self.log.log_info('QDLiga stoppen...')

        self.log.log_info('Beende EventTimer...')
        self.eventTimer.stop()
        self.log.log_info('EventTimer beendet!')

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

    def week1(self):
        # Start der Hinrunde, Start der neuen Saison
        self.season = self.season + 1
        self.round = 1
        self.db.set_time_settings(self.season, self.round)
        self.log.log_info('Start von Saison {}'.format(self.season))
        self.log.log_info('Start der Hinrunde')
        # TODO Benachrichtigung an Spieler?

    def week2(self):
        # Ende der Hinrunde, Start der Rückrunde
        self.round = 2
        self.db.set_time_settings(self.season, self.round)
        self.log.log_info('Ende der Hinrunde')
        self.log.log_info('Start der Rückrunde')
        # TODO Benachrichtigung an Spieler?

    def week3(self):
        # Ende der Rückrunde, Start der Pause-Woche
        self.round = 0
        self.db.set_time_settings(self.season, self.round)
        self.log.log_info('Ende der Rückrunde')
        self.log.log_info('Start der Pause-Woche')
        # TODO Benachrichtigung an Spieler?

    def create_game_schedule(self, player_list):
        """Liefert einen Spielplan einer Liga im (Double) Round Robin Format.
        Einzelne Begegnungen werden hierbei als Tupel (Sp1, Sp2) gespeichert.
        Als player_list wird eine Liste der L_IDs von Spielern übergeben.
        Zurückgegeben.
        Freilose werden nicht gesondert zurückgegeben.
        Rückgabe ist eine Liste der Begegnungen für die Hinrunde sowie der
        Rückrunde (jeweils gespiegelt)"""
        players = len(player_list)
        if players % 2 == 1:
            player_list.append(-1)
            players = players + 1
        game_schedule = []
        game_schedule_drr = []  # Spielplan für die Rückrunde

        for o in range(players-1):  # N-1 Spiele für N Spieler
            # Spielerliste für den Spieltag anlegen
            # Die Liste wird durchrotiert, sodass jeder gegen jeden spielt,
            # anschließend werden die Begegnungen anhand der Listenposition
            # bestimmt. Formel: (o + i) % (l-1) + 1 (l=länge, o=spieltag)
            # Der erste Spieler behält stets seine Position
            gameday = []
            for i in range(players):
                gameday.append(player_list[(o + i) % (players-1)+1])
            gameday[0] = player_list[0]
            for k in range(len(gameday)//2):
                if gameday[k] == -1 or gameday[-1-k] == -1:
                    # Freilos nicht in Liste eintragen
                    pass
                else:
                    game_schedule.append((gameday[k], gameday[-1-k]))
                    game_schedule_drr.append((gameday[-1-k], gameday[k]))

        return game_schedule, game_schedule_drr

    def regroup(self):
        # Spieler-Informationen zwischenspeichern
        player_info = {}
        # Liga-Namen zwischenspeichern
        league_names = {}

        # Liga-Ergebnisse vorheriger Saison laden
        # Liste aller L_IDs der aktuellen Saison
        l_ids = self.db.get_all_leagues(self.season)
        leagues = []
        # Für jede Liga die Tabelle abrufen und eintragen
        for l in l_ids:
            # In der Form: (L_ID, [Tabelle der Liga], Level, Name)
            leagues.append((l[0], self.db.get_league_table(l[0]), l[1], l[2]))
            # Namen der Ligen zwischenspeichern
            league_names[l[0]] = l[2]

        # Überprüfen, ob Spieler noch spielen wollen
        # Status aller Spieler laden
        status = self.db.get_player_status(self.season)
        # Spieler die nicht spielen wollen durch leere Einträge ersetzen
        placeholder = (-1, 0, 0, 0, 0, 0, 0, 0, 0)  # Leerer Eintrag
        new_leagues = []
        for l in range(len(leagues)):
            players = leagues[l][1]  # Liste der Liga-Ergebnisse
            rem = []  # Liste der zu löschenden Elemente
            for p in players:
                # Spieler der Info-Liste hinzufügen und aktuelle Liga speichern
                player_info[p[0]] = {}
                player_info[p[0]]['last_league'] = leagues[l][0]
                player_info[p[0]]['last_level'] = leagues[l][2]
                if status[p[0]] == 0:
                    # Wenn Status = 0, wird der aktuelle Eintrag zur Löschliste
                    # hinzugefügt
                    rem.append(p)
                    player_info[p[0]]['next_league'] = None
                    player_info[p[0]]['next_level'] = None
            for r in rem:
                # Entsprechende Einträge löschen und durch einen leere Einträge
                # (P_ID = -1) ersetzen
                players.append(placeholder)
                players.remove(r)
            new_leagues.append((leagues[l][0], players))

        # Auf- und Abstiege durchführen
        if len(new_leagues) > 1:  # Sonst keine Auf-/Abstiege
            for l in range(len(new_leagues)-1):
                top = new_leagues[l][1]
                bot = new_leagues[l+1][1]
                swap_down_1 = top[6]  # Höhere Liga, Platz 7
                swap_down_2 = top[7]  # Höhere Liga, Platz 8
                swap_up_1 = bot[0]   # Tiefere Liga, Platz 1
                swap_up_2 = bot[1]   # Tiefere Liga, Platz 2
                # Spieler aus alten Ligen entfernen
                new_leagues[l][1].remove(swap_down_1)
                new_leagues[l][1].remove(swap_down_2)
                new_leagues[l+1][1].remove(swap_up_1)
                new_leagues[l+1][1].remove(swap_up_2)
                # Spieler in neue Ligen einfügen
                new_leagues[l][1].insert(6, swap_up_1)
                new_leagues[l][1].insert(7, swap_up_2)
                new_leagues[l+1][1].insert(0, swap_down_1)
                new_leagues[l+1][1].insert(1, swap_down_2)

        # Ligen in eine Liste zusammenführen und leere Einträge entfernen
        # Liste speichert nur noch die Spieler und nicht mehr die Ergebnisse
        single_list = []
        for l in new_leagues:
            for p in l[1]:
                if p is not placeholder:
                    single_list.append(p[0])
        # Warteliste anhängen
        queue = self.db.get_queue()
        for p in queue:
            player_info[p] = {}
            player_info[p]['last_league'] = 0
            player_info[p]['last_level'] = 0
        single_list.extend(queue)

        # Einteilung in neue Ligen von oben nach unten in 8er Gruppen
        # Spieler werden bei Einteilung aus Warteliste entfernt
        new_leagues = []
        while len(single_list) >= 8:
            league = []
            for i in range(8):
                league.append(single_list[0])
                if single_list[0] in queue:
                    self.db.remove_from_queue(single_list[0])
                single_list.remove(single_list[0])
            new_leagues.append(league)
        # Unterste Liga ab 4 Spielern, sonst weiter auf Warteliste
        if len(single_list) >= 4:
            league = []
            for i in range(len(single_list)):
                league.append(single_list[0])
                if single_list[0] in queue:
                    self.db.remove_from_queue(single_list[0])
                single_list.remove(single_list[0])
            new_leagues.append(league)
        else:
            for p in range(len(single_list)):
                if player_info[single_list[p]]['last_league'] is not 0:
                    self.db.add_to_queue(single_list[p])
                player_info[single_list[p]]['next_league'] = 0
                player_info[single_list[p]]['next_level'] = 0

        # Ligen erstellen
        for l in range(len(new_leagues)):
            name = 'Liga {}'.format(l+1)
            l_id = self.db.create_league(name, self.season+1, l+1)
            league_names[l_id] = name
            # Spieler den Ligen hinzufügen
            for p in new_leagues[l]:
                self.db.add_to_league(l_id, p)
                player_info[p]['next_league'] = l_id
                player_info[p]['next_level'] = l + 1
            # Spiele anlegen
            hr, rr = self.create_game_schedule(new_leagues[l])
            self.db.create_games(l_id, 1, hr)
            self.db.create_games(l_id, 2, rr)

        # Spieler benachrichtigen
        league_names[0] = 'Warteliste'
        for p in player_info:
            last = player_info[p]['last_level']
            next = player_info[p]['next_level']
            last_name = league_names[player_info[p]['last_league']]
            if next is None:
                next_name = None
            else:
                next_name = league_names[player_info[p]['next_league']]

            # Spieler spielt nächste Saison nicht mehr
            if next is None:
                text = ('Du spielst nächste Saison nicht mehr mit. Sobald du '
                        'wieder teilnehmen möchtest, änder einfach deinen '
                        'Status im Account-Menü!')
            # Spieler war in Warteliste
            elif last == 0:
                # Spieler bleibt in Warteliste
                if next == 0:
                    text = ('Leider sind nicht genügend Spieler vorhanden. Du '
                            'befindest dich auch in der nächsten Saison '
                            'weiterhin auf der Warteliste!')
                # Spieler steigt aus Warteliste auf
                else:
                    text = ('Du spielst nächste Saison in {}. '
                            'Viel Erfolg!').format(next_name)
            else:
                if next == 0:
                    text = ('Leider sind nicht genügend Spieler vorhanden. Du '
                            'befindest dich für nächste Saison auf der '
                            'Warteliste!')
                elif last == next:
                    text = ('Du hälst deine Liga und spielst nächste Saison in '
                            '{}. Viel Erfolg!').format(next_name)
                elif last > next:
                    text = ('Du bist aufgestiegen und spielst nächste Saison '
                            'in {}. Viel Erfolg!').format(next_name)
                elif last < next:
                    text = ('Du bist leider abgestiegen und spielst nächste '
                            'Saison in {}. Viel Erfolg!').format(next_name)
                else:
                    self.log.log_error('Fehler beim benachrichtigen eines '
                                       'Spielers')
                    print('p:', p)
                    print('player_info', player_info)
                    continue
            self.message_player(p, text)

    def message_player(self, p_id, message):
        # TODO Wie soll benachrichtigt werden? Momentan nur Telegram

        # Versenden über Telegram
        chat_id = self.db.get_input_method(p_id, self.telegramBot.INPUT_METHOD)
        print('Send Message: "{}" to {}'.format(message, p_id))
        if chat_id:
            # Sofern Eingabemethode vorhanden, Nachricht senden
            self.telegramBot.send_message(chat_id, message)
        else:
            self.log.log_error('Spieler hat keine TelegramID')

    def is_currently_playing(self, p_id):
        """Gibt zurück, ob der übergebene Spieler aktuell in einer Liga spielt
        oder nicht"""
        return self.db.is_in_league(p_id, self.season)

    def get_active_matches(self, p_id):
        """Gibt eine Liste der aktuellen Duelle eines Spielers zurück.
        Jedes der Duelle ist ein Tupel der Form:
        (M_ID, Gegner_ID, Gegner_Name, Erg1, Erg2, Status)
        M_ID ist die M_ID des Duells,
        Gegner_ID ist hierbei die P_ID und Gegner_Name der Name des Gegners,
        Erg1 und Erg2 sind das Ergebnis des Duells (sofern bereits eingetragen)
        und Status ist der aktuelle Verifizierungsstatus des Duells
        (Siehe Dokumentation der Datenbank).
        Alle Werte sind aus Sicht der Spielers angeordnet"""
        return self.db.get_active_matches(p_id)

    def submit_result(self, m_id, p_id, res1, res2):
        """"""
        # TODO implement
        pass


if __name__ == "__main__":
    QDLiga()
