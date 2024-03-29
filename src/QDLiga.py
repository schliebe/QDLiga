#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Logger import Logger
from DB import DB
from TelegramBot import TelegramBot
from EventTimer import EventTimer
from MediaGenerator import MediaGenerator


class QDLiga:
    def __init__(self):
        def load_token():
            # Lade Tokens aus Token.txt
            tokens = {'Telegram_Bot_Token': ''}  # Default Werte
            file = open('../Token.txt', 'r')
            for line in file:
                key, value = line.split('=', 1)
                tokens[key] = value
            file.close()
            return tokens

        def check_required_directories():
            import pathlib
            # match_data Ordner erstellen, sofern nicht vorhanden
            pathlib.Path('../match_data').mkdir(exist_ok=True)

        self.PTS_WIN = 5
        self.PTS_DRAW = 3
        self.PTS_LOSE = 1
        self.PTS_NOTPLAYED = 0

        # Logger erstellen
        self.log = Logger()

        # Tokens laden
        token = load_token()

        # Benötigte Ordner erstellen, falls nötig
        check_required_directories()

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

        self.mediaGenerator = MediaGenerator(self)
        self.log.log_info('MediaGenerator geladen')

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

        elif text == '/message':  # Sendet eine Nachricht an einen Spieler
            username = input('Nachricht an wen?\n'
                             'Nutzername eingeben: ')
            p_id = self.get_p_id(username)
            if p_id:
                message = input('Welche Nachricht senden?\n')
                self.message_player(p_id, message)
            else:
                print('Nutzer konnte nicht gefunden werden')

        elif text == '/running':  # Gibt alle noch nicht bestätigten Spiele aus
            matches = self.get_all_running_matches()
            print('Liste aller nicht bestätigten Spiele:')
            print_list = ''
            for m in matches:
                # None durch Striche ersetzen
                if m[9] == 0:
                    res1 = res2 = pts1 = pts2 = '-'
                else:
                    res1 = str(m[5])  # Als String, für schönere Formatierung
                    res2 = str(m[6])
                    pts1 = str(m[7])
                    pts2 = str(m[8])
                print_list += ('[{}] {:>12} vs. {:12} - Res: {:>2}:{:2} - '
                               'Pts: {:>2}:{:2} - Verified: {}\n')\
                    .format(m[0], m[10], m[11], res1, res2, pts1, pts2, m[9])
            print(print_list)

        elif text == '/setresult':  # Trägt ein Ergebnis ein
            m_id = input('Ergebnis welches Duells festlegen?\n'
                         'M_ID eingeben: ')
            if m_id.isdigit():
                match = self.db.load_match(m_id)
            else:
                match = None
            if match:
                p1 = self.get_username(match[3])
                p2 = self.get_username(match[4])
                print('Match {} - Liga {} Runde {}\n'
                      'Eingetragenes Ergebnis:\n'
                      '{} - {}:{} - {}'.format(match[0], match[1], match[2],
                                               p1, match[5], match[6], p2))
                res1 = input('Ergebnis von {}: '.format(p1))
                res2 = input('Ergebnis von {}: '.format(p2))
                pts1 = input('Punkte für {}: '.format(match[3]))
                pts2 = input('Punkte für {}: '.format(match[4]))
                if not (res1.isdigit() and res2.isdigit() and
                        pts1.isdigit() and pts2.isdigit()):
                    print('Unzulässige Eingabe')
                    return
                print('Neues Ergebnis:\n'
                      'Fragen: {}:{}\n'
                      'Punkte: {}:{}'.format(res1, res2, pts1, pts2))
                choice = input('Ergebnis eintragen? [J/N]\n')
                if choice.lower() == 'j':
                    # Überprüfen, ob Punkteverteilung zulässig ist
                    pts1 = int(pts1)
                    pts2 = int(pts2)
                    legal_points = True
                    if pts1 == 5 and (pts2 < 0 or pts2 > 1):
                        # 5 Punkte für P1, aber weder 1 noch 0 Punkte für P2
                        legal_points = False
                    elif pts1 == 3 and pts2 != 3:
                        # 3 Punkte für P1, aber nicht 3 Punkte für P2
                        legal_points = False
                    elif pts1 == 1 and pts2 != 5:
                        # 1 Punkt für P1, aber nicht 5 Punkte für P2
                        legal_points = False
                    elif pts1 == 0 and pts2 != 5 and pts2 != 0:
                        # 0 Punkte für P1, aber weder 5, noch 0 Punkte für P2
                        legal_points = False
                    elif pts1 != 5 and pts1 != 3 and pts1 != 1 and pts1 != 0:
                        # P1 bekommt unzulässige Punkte
                        legal_points = False
                    # Nachfragen, falls unzulässig
                    if not legal_points:
                        choice = input('Punkteverteilung unzulässig. '
                                       'Trotzdem eintragen? [J/N]\n')
                        if choice.lower() == 'j':
                            legal_points = True
                    # Eintragen, wenn Ergebnis zulässig
                    if legal_points:
                        self.set_final_result(m_id, res1, res2, pts1, pts2)
                    else:
                        print('Ergebnis nicht eingetragen')
                else:
                    print('Ergebnis nicht eingetragen')
            else:
                print('Duell existiert nicht')

        elif text == '/rename':  # Ändert den Nutzernamen eines Spielers
            username = input('Wessen Nutzername soll geändert werden?\n'
                             'Nutzername eingeben: ')
            p_id = self.get_p_id(username)
            if p_id:
                new_name = input('Neuen Nutzernamen eingeben:\n')
                choice = input('Nutzer von "{}" in "{}" umbenennen? [J/N]\n'
                               .format(username, new_name))
                if choice.lower() == 'j':
                    self.rename_user(p_id, new_name)
            else:
                print('Nutzer konnte nicht gefunden werden')

        elif text == '/help':  # Zeigt die möglichen Befehle
            print('Folgende Befehle können genutzt werden:\n'
                  '/stop: Die QDLiga und alle zugehörigen Module beenden\n'
                  '/message: Sendet eine Nachricht an einen Spieler\n'
                  '/running: Gibt eine Liste aller noch nicht bestätigten '
                  'Spiele aus\n'
                  '/setresult: Das Ergebnis eines Duells festlegen\n'
                  '/rename: Ändert den Nutzernamen eines Spielers\n'
                  '/help: Diese Liste aufrufen\n')

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
        zurück. Der Spieler wird der Warteliste hinzugefügt"""
        try:
            p_id = self.db.insert_player(username)
            in_queue = self.db.is_in_queue(p_id)
            if not in_queue:
                self.db.add_to_queue(p_id)
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
        # Benachrichtigung an Spieler
        self.notify_active_players(
            'Die Hinrunde ist gestartet!\n'
            'Du hast 7 Tage Zeit deine Duelle zu spielen. Deine aktuellen '
            'Spiele findest du im Duelle Menü.')

    def week2(self):
        # Ende der Hinrunde, Start der Rückrunde
        self.round = 2
        self.db.set_time_settings(self.season, self.round)
        self.log.log_info('Ende der Hinrunde')
        self.log.log_info('Start der Rückrunde')
        # Benachrichtigung an Spieler
        self.notify_active_players(
            'Die Hinrunde ist beendet und die Rückrunde ist gestartet!\n'
            'Du hast 7 Tage Zeit deine Duelle zu spielen. Deine aktuellen '
            'Spiele findest du im Duelle Menü.')
        self.clear_match_data()

    def week3(self):
        # Ende der Rückrunde, Start der Pause-Woche
        self.round = 0
        self.db.set_time_settings(self.season, self.round)
        self.log.log_info('Ende der Rückrunde')
        self.log.log_info('Start der Pause-Woche')
        # Benachrichtigung an Spieler
        self.notify_active_players(
            'Die Rückrunde ist beendet!\n'
            'Die vorläufigen Ergebnisse können im Liga Menü angesehen werden.')
        self.clear_match_data()

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
        if self.season == 0:
            l_ids = []
        else:
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
                player_info[p[0]]['last_place'] = players.index(p) + 1
                if status[p[0]] == 0:
                    # Wenn Status = 0, wird der aktuelle Eintrag zur Löschliste
                    # hinzugefügt
                    rem.append(p)
                    player_info[p[0]]['next_league'] = None
                    player_info[p[0]]['next_level'] = None
            for r in rem:
                # Entsprechende Einträge löschen und durch leere Einträge
                # (P_ID = -1) ersetzen
                players.append(placeholder)
                players.remove(r)
            new_leagues.append((leagues[l][0], players))

        # Auf- und Abstiege durchführen
        if len(new_leagues) > 1:  # Sonst keine Auf-/Abstiege
            for l in range(len(new_leagues)-1):
                top = new_leagues[l][1]
                bot = new_leagues[l+1][1]
                # TODO Eventuell anpassen für mehr als 8 Spieler pro Liga
                swap_down_1 = top[6]  # Höhere Liga, Platz 7
                swap_down_2 = top[7]  # Höhere Liga, Platz 8
                swap_up_1 = bot[0]  # Tiefere Liga, Platz 1
                swap_up_2 = bot[1]  # Tiefere Liga, Platz 2
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
            player_info[p]['last_place'] = 0
        single_list.extend(queue)

        # Einteilung in neue Ligen von oben nach unten in 8er Gruppen
        # Spieler werden bei Einteilung aus Warteliste entfernt
        # TODO Eventuell anpassen für mehr als 8 Spieler pro Liga
        new_leagues = []
        while len(single_list) >= 8:
            league = []
            for i in range(8):
                league.append(single_list[0])
                if single_list[0] in queue:
                    self.db.remove_from_queue(single_list[0])
                single_list.remove(single_list[0])
            new_leagues.append(league)
        # Unterste Liga ab 4 Spielern, sonst übrige Spieler auf Warteliste
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
            place = player_info[p]['last_place']
            last = player_info[p]['last_level']
            next = player_info[p]['next_level']
            last_name = league_names[player_info[p]['last_league']]
            if next is None:
                next_name = None
            else:
                next_name = league_names[player_info[p]['next_league']]

            # Ergebnis mitteilen, wenn Spieler letzte Runde gespielt hat
            if place != 0:
                # Wenn Sieger von Liga 1, spezielle Nachricht
                if last == 1 and place == 1:
                    text_place = ('Du bist der Sieger von {}. '
                                  'Herzlichen Glückwunsch!'.format(last_name))
                else:
                    text_place = ('Du hast {} auf dem {}. Platz abgeschlossen!'
                                  .format(last_name, place))
            else:
                text_place = None

            # Spieler spielt nächste Saison nicht mehr
            if next is None:
                text = ('Du spielst nächste Saison nicht mehr mit. Sobald du '
                        'wieder teilnehmen möchtest, ändere einfach deinen '
                        'Status im Account-Menü!')
            # Spieler war in Warteliste
            elif last == 0:
                # Spieler bleibt in Warteliste
                if next == 0:
                    text = ('Leider sind nicht genügend Spieler vorhanden. '
                            'Du befindest dich auch in der nächsten Saison '
                            'weiterhin auf der Warteliste!')
                # Spieler steigt aus Warteliste auf
                else:
                    text = ('Du spielst nächste Saison in {}. '
                            'Viel Erfolg!').format(next_name)
            # Spieler hat in Liga gespielt
            else:
                if next == 0:
                    text = ('Leider sind nicht genügend Spieler vorhanden. '
                            'Du befindest dich für nächsten Saison auf der '
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
                    self.log.log_error('p:', p)
                    self.log.log_error('player_info', player_info)
                    continue
            # Wenn gespielt, Ergebnis an Spieler senden
            if text_place:
                self.message_player(p, text_place)
            # Auf- und Abstiegsmeldungen senden
            self.message_player(p, text)
        self.log.log_info('Regroup beendet')

    def message_player(self, p_id, message):
        # TODO Wie soll benachrichtigt werden? Momentan nur Telegram

        # Versenden über Telegram
        chat_id = self.db.get_input_method(p_id, self.telegramBot.INPUT_METHOD)

        self.log.log_info('Sende Nachricht: "{}" an {}'.format(message, p_id))
        if chat_id:
            # Sofern Eingabemethode vorhanden, Nachricht senden
            self.telegramBot.send_message(chat_id, message)
        else:
            self.log.log_error('Spieler hat keine TelegramID')

    def message_support(self, message):
        # TODO Mit Support korrekt implementieren! Nur für den Testlauf genutzt

        # Nutzer aus SupportUser.txt lesen, die Meldungen erhalten sollen
        support = []
        file = open('../SupportUser.txt', 'r')
        for line in file:
            support.append(line.strip())
        file.close()

        # Versenden über Telegram an alle festgelegten Support-Nutzer
        for telegramID in support:
            self.log.log_info('Sende Support-Nachricht: "{}" an {}'
                              .format(message, telegramID))
            support_message = '~~~SUPPORT~~~\n{}\n~~~SUPPORT~~~'.format(message)
            self.telegramBot.send_message(telegramID, support_message)

    def is_currently_playing(self, p_id):
        """Gibt zurück, ob der übergebene Spieler aktuell in einer Liga spielt
        oder nicht"""
        # TODO durch get_player_league() ersetzen
        return self.db.is_in_league(p_id, self.season)

    def get_player_league(self, p_id, season=None):
        """Gibt zurück, in welcher Liga der übergebene Spieler in der
        angegebenen Saison (None, wenn aktuelle Saison) gespielt hat.
        Gibt None zurück, falls Spieler in keiner Liga gespielt hat"""
        if season:
            return self.db.get_player_league(p_id, season)
        else:
            return self.db.get_player_league(p_id, self.season)

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
        """Lädt das aktuelle Ergebnis des Duells aus der Datenbank und überprüft
        wie das übergebene Ergebnis angewendet werden soll.
        Zudem wird auch der Gegner informiert.
        Status 0: Ergebnis in Datenbank eintragen, Status je nach Spieler auf
            1 bzw. 2 setzen
        Status 1/2: Ergebnis mit Ergebnis in der Datenbank abgleichen.
            Wenn korrekt auf Status 3, sonst auf Status 4 bzw. 5 setzen und
            Benachrichtigung für Support auslösen
        Status 4/5: Fehlermeldung, da unerwünschte Aktion"""
        # Duell laden
        match = self.db.load_match(m_id)
        if match:
            m_id, _, _, p1, p2, r1, r2, pts1, pts2, verified = match
            # Überprüfen ob p1 oder p2 das neue Ergebnis gesendet hat
            if p_id == p1:
                from_p1 = True
            elif p_id == p2:
                from_p1 = False
            else:
                self.log.log_error(('Ungültiger Spieler beim eingeben des '
                                   'Ergebnis'))
                return
            # Fallunterscheidung, siehe Kommentar
            # Kein Ergebnis vorhanden
            if verified == 0:
                # Berechnen, wie viele Punkte die Spieler erhalten
                if res1 > res2:
                    pts_for = self.PTS_WIN
                    pts_against = self.PTS_LOSE
                elif res1 == res2:
                    pts_for = self.PTS_DRAW
                    pts_against = self.PTS_DRAW
                elif res1 < res2:
                    pts_for = self.PTS_LOSE
                    pts_against = self.PTS_WIN
                # Ergebnis in Datenbank aktualisieren
                # Wenn p2 das Ergebnis gesendet hat werden die Eingaben
                # entsprechend getauscht
                if from_p1:
                    self.db.update_match(
                        m_id, res1, res2, pts_for, pts_against, 1)
                    # Gegenspieler benachrichtigen
                    self.message_player(
                        p2,
                        'Dein Gegner hat ein Ergebnis eingetragen. Du kannst '
                        'es im Duelle-Menü bestätigen!')
                    self.save_to_match_data(
                        m_id, 'Ergebnis von {} eingetragen: {} - {}:{} - {}'
                              .format(p1, p1, res1, res2, p2))
                else:
                    self.db.update_match(
                        m_id, res2, res1, pts_against, pts_for, 2)
                    # Gegenspieler benachrichtigen
                    self.message_player(
                        p1,
                        'Dein Gegner hat ein Ergebnis eingetragen. Du kannst '
                        'es im Duelle-Menü bestätigen!')
                    self.save_to_match_data(
                        m_id, 'Ergebnis von {} eingetragen: {} - {}:{} - {}'
                              .format(p2, p1, res1, res2, p2))
            # Spieler 2 bestätigt oder korrigiert Ergebnis von Spieler 1
            elif verified == 1 and not from_p1:
                if res1 == r2 and res2 == r1:
                    # Ergebnis bestätigt, Status auf 3 setzen
                    self.db.update_match(m_id, r1, r2, pts1, pts2, 3)
                    # Gegenspieler benachrichtigen
                    self.message_player(
                        p1,
                        'Dein Gegner hat ein Ergebnis bestätigt und das Duell '
                        'damit beendet.')
                    self.save_to_match_data(
                        m_id, 'Ergebnis von {} bestätigt: {} - {}:{} - {}'
                              .format(p2, p1, res1, res2, p2))
                else:
                    # Ergebnis korrigiert, Status auf 4 setzen
                    # Admin benachrichtigen, Problem zu lösen
                    self.db.update_match(m_id, r1, r2, pts1, pts2, 4)
                    self.save_to_match_data(
                        m_id, 'Korrigiertes Ergebnis von {}: {} - {}:{} - {}'
                              .format(p2, p1, res1, res2, p2))
                    # TODO Anfrage an Support korrekt weiterleiten
                    self.message_support(
                        'Eingegebenes Ergebnis unterscheidet sich!\n'
                        'M_ID: {}\n'
                        'Vorheriges Ergebnis: {}:{}\n'
                        'Neu eingetragenes Ergebnis: {}:{}\n'
                        'Eingetragen von: {}'
                        .format(m_id, r1, r2, res2, res1, p_id))
            # Spieler 1 bestätigt oder korrigiert Ergebnis von Spieler 2
            elif verified == 2 and from_p1:
                if res1 == r1 and res2 == r2:
                    # Ergebnis bestätigt, Status auf 3 setzen
                    self.db.update_match(m_id, r1, r2, pts1, pts2, 3)
                    # Gegenspieler benachrichtigen
                    self.message_player(
                        p2,
                        'Dein Gegner hat ein Ergebnis bestätigt und das Duell '
                        'damit beendet.')
                    self.save_to_match_data(
                        m_id, 'Ergebnis von {} bestätigt: {} - {}:{} - {}'
                              .format(p1, p1, res1, res2, p2))
                else:
                    # Ergebnis korrigiert, Status auf 5 setzen
                    # Admin benachrichtigen um Problem zu lösen
                    self.db.update_match(m_id, r1, r2, pts1, pts2, 5)
                    self.save_to_match_data(
                        m_id, 'Korrigiertes Ergebnis von {}: {} - {}:{} - {}'
                              .format(p1, p1, res1, res2, p2))
                    # TODO Anfrage an Support korrekt weiterleiten
                    self.message_support(
                        'Eingegebenes Ergebnis unterscheidet sich!\n'
                        'M_ID: {}\n'
                        'Vorheriges Ergebnis: {}:{}\n'
                        'Neu eingetragenes Ergebnis: {}:{}\n'
                        'Eingetragen von: {}'
                        .format(m_id, r1, r2, res1, res2, p_id))
            else:
                self.log.log_error(('Ungewünschter Status des zu ändernden '
                                   'Duells'))
        else:
            self.log.log_error('Fehler beim laden des Duells')

    def set_final_result(self, m_id, res1, res2, pts1, pts2):
        """Setzt das finale Ergebnis eines Duells und benachrichtigt die
        Spieler darüber"""
        # Ergebnis eintragen
        self.db.update_match(m_id, res1, res2, pts1, pts2, 3)

        # Spieler benachrichtigen
        # Match-Daten laden
        match = self.db.load_match(m_id)
        _, season, _, _ = self.get_league_info(match[1])
        if match[2] == 1:
            round = 'Hinrunde'
        elif match[2] == 2:
            round = 'Rückrunde'
        else:
            round = '?'
        p1 = self.get_username(match[3])
        p2 = self.get_username(match[4])
        # Nachricht vorbereiten und an beide Spieler versenden
        message = ('Das Ergebnis deines Duells gegen {} (Saison {}, {}) wurde '
                   'auf {}:{} festgelegt.\nErhaltene Punkte: {}')
        self.message_player(match[3],
                            message.format(p2, season, round, res1, res2, pts1))
        self.message_player(match[4],
                            message.format(p1, season, round, res2, res1, pts2))

        # Logging
        self.log.log_info('Ergebnis für Duell {} mit Ergebnis {}:{} '
                          'eingetragen'.format(m_id, res1, res2))
        self.save_to_match_data(
            m_id, 'Ergebnis {}:{} durch Konsole eingetragen'.format(res1, res2))

    def get_stats_top10(self):
        """Gibt die Top 10 der Gesamtstatistik zurück.
        Die einzelnen Zeilen haben die Form:
        (P_ID, Username, Matches, Win, Draw, Lose, NotPlayed, Correct, Perfect,
        Points)"""
        return self.db.get_stats_top10()

    def get_stats_single(self, p_id):
        """Gibt den Gesamtstatistikwert eines einzelnen Spielers zurück.
        Die Zeile hat die Form:
        (Pos, P_ID, Username, Matches, Win, Draw, Lose, NotPlayed, Correct,
        Perfect, Points)"""
        return self.db.get_stats_single(p_id)

    def generate_statistics_table(self, p_id=None):
        """Gibt ein Bild der Statistik-Tabelle zurück.
        Darin sind die besten 10 Spieler sowie ggf. der aufrufende Spieler
        enthalten, sofern sich dieser nicht in den Top 10 befindet"""
        return self.mediaGenerator.generate_statistics(p_id)

    def get_league_table(self, l_id):
        """Gibt die Tabelle der übergebenen Liga zurück"""
        return self.db.get_league_table(l_id)

    def generate_league_table(self, l_id):
        """Gibt ein Bild der Liga-Tabelle der übergebenen Liga zurück"""
        # Daten der Liga laden
        name, _, _, level = self.db.get_league_info(l_id)

        # Min und Max Level der aktuellen Saison laden
        min_level = 1
        max_level = self.db.get_league_max_level(self.season)

        # Bestimmen welche Hintergrundfarben verwendet werden sollen.
        # Mögliche Werte sind:
        # 0 - Keine Einfärbung
        # 1 - Platz 1 wird gold hinterlegt
        #  (Nur eine Liga)
        # 2 - Platz 1 wird gold hinterlegt, Platz 7 und 8 rot
        #  (Mehr als eine Liga, für erste Liga)
        # 3 - Platz 1 und 2 werden grün hinterlegt
        #  (Mehr als eine Liga, für letzte Liga)
        # 4 - Platz 1 und 2 werden grün hinterlegt, Platz 7 und 8 rot
        #  (Mehr als eine Liga, für weder erste noch letzte Liga)
        color = 0
        if max_level == min_level and level == min_level:
            color = 1
        elif min_level < max_level and level == min_level:
            color = 2
        elif min_level < max_level and level == max_level:
            color = 3
        elif min_level < max_level and min_level < level < max_level:
            color = 4

        return self.mediaGenerator.generate_league_table(l_id, name, color)

    def get_username(self, p_id):
        """Gibt den Nutzernamen des übergebenen Spielers zurück"""
        return self.db.get_username(p_id)

    def get_league_info(self, l_id):
        """Gibt Name, Saison, Anzahl der Spieler, sowie Level der
        übergebenen Liga zurück"""
        return self.db.get_league_info(l_id)

    def get_active_players(self, season=None):
        """Gibt eine Liste mit den P_IDs aller Spieler aus, die aktuell in einer
        Liga spielen"""
        if season:
            return self.db.get_active_players(season)
        else:
            return self.db.get_active_players(self.season)

    def notify_active_players(self, message):
        """Sendet eine Nachricht an alle Spieler, die sich aktuell in einer
        Liga befinden"""
        players = self.get_active_players()
        for p in players:
            self.message_player(p, message)

    def save_to_match_data(self, m_id, text):
        # Entsprechende match_data Datei öffnen (match_data/[m_id].txt)
        # Wird angelegt, wenn nicht bereits vorhanden
        file = open('../match_data/{}.txt'.format(m_id), 'a')
        file.write('{}\n\n'.format(text))
        file.close()

    def clear_match_data(self):
        import os
        match_data = os.listdir('../match_data')
        for data in match_data:
            if data.endswith('.txt'):
                m_id = data[:-4]
                match = self.db.load_match(m_id)
                if match[9] == 3:
                    os.remove('../match_data/{}'.format(data))
        self.log.log_info('Nicht benötigte Match Data gelöscht.')

    def daily_reminder(self, weekday):
        # Jeder Spieler, der noch ein Duell bestätigen muss erhällt eine kurze
        # Benachrichtigung
        # TODO überprüfen, ob offene Support-Tickets (sobald vorhanden)
        matches = self.db.get_unconfirmed_matches()
        notify_list = set()
        for match in matches:
            # Wenn verified = 1: Spieler 2 hat noch nicht bestätigt
            if match[3] == 1:
                notify_list.add(match[2])
            # Wenn verified = 2: Spieler 1 hat noch nicht bestätigt
            elif match[3] == 2:
                notify_list.add(match[1])

        for p_id in notify_list:
            self.message_player(p_id, 'Erinnerung:\n'
                                      'Du hast noch nicht alle Ergebnisse '
                                      'bestätigt, die von deinen Gegnern '
                                      'eingetragen wurden!')

        # Alle Spieler, die ihre Spiele noch nicht gespielt haben erhalten
        # Samstag und Sonntag vor Ablauf der Zeit eine Benachrichtigung
        # TODO Erwähnen, was zu tun ist, falls die Zeit abgelaufen ist
        text = None
        if weekday == 5:  # Samstag
            text = ('Erinnerung: Du hast nur noch bis Morgen Abend Zeit um '
                    'deine restlichen Duelle zu spielen!')
        elif weekday == 6:  # Sonntag
            text = ('Erinnerung: Du hast nur noch bis Heute Abend Zeit um '
                    'deine restlichen Duelle zu spielen!\n'
                    'Für nicht gespielte Spiele erhältst du keine Punkte!')
        if text:
            matches = self.get_all_running_matches()
            notify_list = set()
            for m in matches:
                if self.round == m[2] and m[9] == 0:
                    notify_list.add(m[3])
                    notify_list.add(m[4])

            for p_id in notify_list:
                self.message_player(p_id, text)

    def get_league_matches(self, l_id, include_names=False):
        if include_names:
            return self.db.get_league_matches_with_names(l_id)
        else:
            return self.db.get_league_matches(l_id)

    def generate_result_list(self, l_id):
        """Gibt ein Bild der Ergebnisliste der übergebenen Liga zurück"""
        return self.mediaGenerator.generate_result_list(l_id)

    def rename_user(self, p_id, new_name):
        """Ändert den Nutzernamen des übergebenen Spielers in den neuen Namen"""
        old_name = self.get_username(p_id)
        self.db.rename_user(p_id, new_name)
        self.log.log_info('Name von "{}" (P_ID: {}) in "{}" geändert.'
                          .format(old_name, p_id, new_name))

    def get_all_running_matches(self):
        """Gibt eine Liste aller Spiele zurück, die noch nicht bestätigt wurden.
        (Also: Alle Spiele, die noch nicht von beiden Seiten eingetragen und
        bestätigt worden sind)"""
        return self.db.get_all_running_matches()


if __name__ == "__main__":
    QDLiga()
