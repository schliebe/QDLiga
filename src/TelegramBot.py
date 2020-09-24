#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler,
                          ConversationHandler, Filters)
import threading
from io import BytesIO


class TelegramBot:
    def __init__(self, parent, log, token):
        # Logger setzen
        self.log = log

        # Verbindung zur QDLiga
        self.parent = parent

        # Bot-Attribute festlegen
        self.updater = Updater(
            token=token,
            use_context=True)
        self.dispatcher = self.updater.dispatcher

        # Bezeichnung der Eingabemethode
        self.INPUT_METHOD = 'TelegramID'

        # Timeout-Zeit festlegen
        self.TIMEOUT_TIME = 600  # Timeout in Sekunden (10 Minuten)

        # Handler registrieren
        self.add_all_handler()

        # Keyboards anlegen
        self.keyboards = {}
        self.create_keyboards()

        # Informationen für Nutzer werden hier zwischengespeichert
        self.user = {}

        # Bot starten
        self.updater.start_polling()
        # self.updater.idle()  TODO Nötig? Dann in QDLiga als Thread aufrufen?

    def add_all_handler(self):
        # Handler registrieren
        # CommandHandler
        start_handler = CommandHandler('start', self.mainmenu)
        self.dispatcher.add_handler(start_handler)
        # ConversationHandler
        self.add_conversationhandler()

    def add_conversationhandler(self):
        # Nummern der Zustände
        self.MATCHES = 100
        self.MATCHES_SELECT = 101
        self.MATCHES_PTS1 = 102
        self.MATCHES_PTS2 = 103
        self.MATCHES_CONFIRM = 104
        self.MATCHES_VERIFY = 105
        self.LEAGUE = 200
        self.STATISTICS = 300
        self.ACCOUNT = 400
        self.REGISTER = 410
        self.REGISTER_YESNO = 411
        self.REGISTER_NAME = 412
        self.REGISTER_CONFIRM = 413
        self.STATUS = 420
        self.STATUS_YESNO = 421
        self.STATUS_CHOOSE = 422
        self.STATUS_CONFIRM = 423

        self.TIMEOUT = ConversationHandler.TIMEOUT

        # Menüs als Conversations. Im Hauptmenü können die verschiedenen Menüs
        # aufgerufen werden (Ebene 1, E1). Deren Untermenüs (E2, ...) müssen
        # jedoch zuerst implementiert werden, somit erfolgt die Reihenfolge von
        # unten nach oben.
        default_handler = ConversationHandler(
            entry_points=[],
            states={
                self.TIMEOUT: [
                    MessageHandler(None, self.timeout)
                ]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
            map_to_parent={},
            conversation_timeout=self.TIMEOUT_TIME
        )
        go_back_handler = MessageHandler(Filters.regex('^(Zurück)$'),
                                         self.go_back)  # Zurück ins Hauptmenü

        # Menü: Duelle (E1)
        matches_handler = ConversationHandler(
            entry_points=[MessageHandler(Filters.regex('^(Duelle)$'),
                                         self.matches)],
            states={
                self.MATCHES_SELECT: [
                    go_back_handler,
                    MessageHandler(Filters.text, self.matches_select),
                ],
                self.MATCHES_PTS1: [
                    MessageHandler(Filters.text, self.matches_pts1)
                ],
                self.MATCHES_PTS2: [
                    MessageHandler(Filters.text, self.matches_pts2)
                ],
                self.MATCHES_CONFIRM: [
                    MessageHandler(Filters.regex('^(Ja|Nein)$'),
                                   self.matches_confirm)
                ],
                self.MATCHES_VERIFY: [
                    MessageHandler(Filters.regex('^(Ja|Nein)$'),
                                   self.matches_verify)
                ],
                self.TIMEOUT: [
                    MessageHandler(None, self.timeout)
                ],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
            conversation_timeout=self.TIMEOUT_TIME
        )
        self.dispatcher.add_handler(matches_handler)

        # Menü: Liga (E1)
        league_handler = ConversationHandler(
            entry_points=[MessageHandler(Filters.regex('^(Liga)$'),
                                         self.league)],
            states={
                self.LEAGUE: [
                    go_back_handler,
                    MessageHandler(Filters.regex('^(Tabelle)$'),
                                   self.league_select),
                ],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
            conversation_timeout=self.TIMEOUT_TIME
        )
        self.dispatcher.add_handler(league_handler)

        # Menü: Statistiken (E1)
        statistics_handler = ConversationHandler(
            entry_points=[MessageHandler(Filters.regex('^(Statistiken)$'),
                                         self.statistics)],
            states={
                self.STATISTICS: [
                    go_back_handler,
                    MessageHandler(Filters.regex('^(Statistik anzeigen)$'),
                                   self.statistics_select),
                ],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
            conversation_timeout=self.TIMEOUT_TIME
        )
        self.dispatcher.add_handler(statistics_handler)

        # Menü: Account
        # Registrieren (E2)
        register_handler = ConversationHandler(
            entry_points=[MessageHandler(Filters.regex('^(Registrieren)$'),
                                         self.register)],
            states={
                self.REGISTER_YESNO: [
                    MessageHandler(Filters.regex('^(Ja|Nein)$'),
                                   self.register_yesno)
                ],
                self.REGISTER_NAME: [
                    MessageHandler(Filters.text, self.register_name)
                ],
                self.REGISTER_CONFIRM: [
                    MessageHandler(Filters.regex('^(Ja|Nein)$'),
                                   self.register_confirm)
                ],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
            map_to_parent={
                self.ACCOUNT: self.ACCOUNT,
                self.TIMEOUT: self.ACCOUNT,
                ConversationHandler.END: ConversationHandler.END,
            },
            conversation_timeout=self.TIMEOUT_TIME
        )

        # Status ändern (E2)
        status_handler = ConversationHandler(
            entry_points=[MessageHandler(Filters.regex('^(Status ändern)$'),
                                         self.status)],
            states={
                self.STATUS_YESNO: [
                    MessageHandler(Filters.regex('^(Ja|Nein)$'),
                                   self.status_yesno)
                ],
                self.STATUS_CHOOSE: [
                    MessageHandler(Filters.regex('^(Aktiv|Inaktiv)$'),
                                   self.status_choose)
                ],
                self.STATUS_CONFIRM: [
                    MessageHandler(Filters.regex('^(Ja|Nein)$'),
                                   self.status_confirm)
                ],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
            map_to_parent={
                self.ACCOUNT: self.ACCOUNT,
                ConversationHandler.END: ConversationHandler.END,
            },
            conversation_timeout=self.TIMEOUT_TIME
        )

        # Account (E1)
        account_handler = ConversationHandler(
            entry_points=[MessageHandler(Filters.regex('^(Account)$'),
                                         self.account)],
            states={
                self.ACCOUNT: [register_handler,
                               status_handler,
                               go_back_handler],
                self.TIMEOUT: [
                    MessageHandler(None, self.timeout)
                ],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
            conversation_timeout=self.TIMEOUT_TIME
        )
        self.dispatcher.add_handler(account_handler)

        # Menü: Support (E1)
        # TODO Implementieren

        # Menü: Mehr (E1)
        # TODO Implementieren

    def create_keyboards(self):
        # Speichert alle möglichen Keyboards, sodass diese nicht immer neu
        # erstellt werden müssen
        self.keyboards['yesno'] = [['Ja', 'Nein']]  # Ja/Nein
        self.keyboards['main'] = [['Duelle', 'Liga'],
                                  ['Statistiken', 'Account'],
                                  ['Support', 'Mehr']]  # Hauptmenü
        self.keyboards['league'] = [['Tabelle'],
                                    ['Zurück']]  # Liga
        self.keyboards['statistics'] = [['Statistik anzeigen'],
                                        ['Zurück']]  # Statistiken
        self.keyboards['account'] = [['Registrieren', 'Status ändern'],
                                     ['Zurück']]  # Account
        self.keyboards['status'] = [['Aktiv', 'Inaktiv']]  # Status ändern

    def stop(self):
        # Lösung aus dem Forum
        # https://github.com/python-telegram-bot/python-telegram-bot/issues/801
        def shutdown():
            self.updater.stop()
            self.updater.is_idle = False
        threading.Thread(target=shutdown).start()

    def send_message(self, chat_id, message, disable_notification=False):
        self.updater.bot.send_message(chat_id, message,
                                      disable_notification=disable_notification)

    def send_image(self, chat_id, image, caption=None, disable_notification=False):
        bio = BytesIO()
        bio.name = 'image.png'
        image.save(bio, 'PNG')
        bio.seek(0)

        self.updater.bot.send_photo(chat_id, photo=bio, caption=caption,
                                    disable_notification=disable_notification)

    def cleanup(self, update, context, text):
        # Löscht die zwischengespeicherten Daten eines Users, beim Abbrechen
        # durch /cancel, beim Timeout oder beim Beenden des Bot.
        # Führt zurück ins Hauptmenü
        chat_id = update.effective_chat.id
        self.user.pop(chat_id, None)
        update.message.reply_text(text)
        self.mainmenu(update, context)

    def cancel(self, update, context):
        # Wird mit /cancel aufgerufen
        # Bricht den aktuellen Vorgang ab und führt zurück ins Hauptmenü
        chat_id = update.effective_chat.id
        message = update.message.text
        self.user_input(chat_id, message, check_user=True)
        self.cleanup(update, context, 'Abgebrochen.')
        return ConversationHandler.END

    def timeout(self, update, context):
        # Wird durch Timeout im ConversationHandler ausgelöst
        # Bricht den aktuellen Vorgang ab und führt zurück ins Hauptmenü
        chat_id = update.effective_chat.id
        message = update.message.text
        self.cleanup(update, context, ('Das hat etwas zu lange gedauert. '
                                       'Versuch es einfach nochmal!'))
        return ConversationHandler.END

    def go_back(self, update, context):
        # Wird durch den Zurück-Button eines Untermenüs aufgerufen
        # Geht ins Hauptmenü zurück
        self.mainmenu(update, context)
        return ConversationHandler.END

    def user_input(self, chat_id, message, check_user=False):
        # Wird aufgerufen, wenn der User eine Eingabe tätigt
        # Überprüft, dass ein Objekt des Nutzers vorhanden ist und legt
        #  ansonsten eines an (nur wenn check_user=True)
        # Loggt die Eingabe
        # Aktualisiert den Timeout-Timer
        if check_user and chat_id not in self.user:
            self.user[chat_id] = {}  # Legt Nutzerobjekt an, wenn nötig
        self.log.log_input('{}: {}'.format(chat_id, message))

    def mainmenu(self, update, context):
        # Hauptmenü
        # Aufgerufen mit /start
        # Anzeigen der weiteren Menüpunkte
        chat_id = update.effective_chat.id
        message = update.message.text
        # self.user_input(chat_id, message, check_user=True)
        text = 'Willkommen in der QDLiga!\n' \
               'Hier entsteht der Telegram-Bot um die QDLiga zu nutzen.\n' \
               'Bisher kannst du dich schon im Menü "Account" registrieren!\n' \
               'Komm bitte bald wieder, um den fertigen Bot zu nutzen!'
        update.message.reply_text(
            text, reply_markup=ReplyKeyboardMarkup(self.keyboards['main']))

    def matches(self, update, context):
        # Menü für Duelle (E1)
        # Aufgerufen über das Hauptmenü
        # Überprüft, ob Spieler bereits registriert ist und gerade spielt
        # Zeigt dann die aktiven Spiele und erlaubt es Ergebnisse einzutragen
        # Farben: Rot: '🔴' Gelb: '🟡' Grün: '🟢' Schwarz: '⚫️' Weiß: '⚪️'
        chat_id = update.effective_chat.id
        message = update.message.text
        self.user_input(chat_id, message, check_user=True)
        p_id = self.parent.get_p_id_from_input(self.INPUT_METHOD, chat_id)
        if p_id is None:
            update.message.reply_text(
                ('Um mitspielen zu können musst du dich zuerst im Account-Menü '
                 'registrieren!'))
            self.mainmenu(update, context)
            return ConversationHandler.END
        self.user[chat_id]['p_id'] = p_id
        if not self.parent.is_currently_playing(p_id):
            update.message.reply_text(
                ('Du spielst momentan in keiner Liga mit. Warte bitte bis zum '
                 'Ende der aktuellen Saison, bevor es los gehen kann!'))
            self.mainmenu(update, context)
            return ConversationHandler.END
        else:
            matches = self.parent.get_active_matches(self.user[chat_id]['p_id'])
            color_boxes = {0: '[⚪️]', 1: '[⚫️]', 2: '[🟡]', 3: '[🟢]',
                           4: '[🔴]', 5: '[🔴]'}
            match_list = ''
            active_matches = {}
            matches_keyboard = []
            for m in matches:
                if m[3] is None or m[4] is None:
                    result = '-:-'
                else:
                    result = '{}:{}'.format(m[3], m[4])
                match_list = match_list + '{} {} | {}\n'.format(
                    color_boxes[m[5]], result, m[2])
                if m[5] == 0 or m[5] == 2:
                    active_matches[m[2]] = m
                    matches_keyboard.append([m[2]])
            self.user[chat_id]['active_matches'] = active_matches
            matches_keyboard.append(['Zurück'])
            color_legend = ('[⚪️]: Duell muss noch eingetragen werden\n'
                            '[🟢]: Duell beendet\n'
                            '[🟡]: Ergebnis bestätigen\n'
                            '[⚫️]: Warten auf den Gegner\n'
                            '[🔴]: Problem beim Eintragen\n')
            reply = ('Legende:\n{}\nDeine aktuellen Gegner sind:\n{}\n'
                     'Welches Ergebnis möchtest du eintragen?').format(
                color_legend, match_list)
            update.message.reply_text(
                reply, reply_markup=ReplyKeyboardMarkup(matches_keyboard))
            return self.MATCHES_SELECT

    def matches_select(self, update, context):
        # Status des Spiel gegen den ausgewählten Gegner überprüfen
        # Neues Ergebnis (0), oder Ergebnis bestätigen (2) unterscheiden
        chat_id = update.effective_chat.id
        message = update.message.text
        self.user_input(chat_id, message)
        if message in self.user[chat_id]['active_matches']:
            match = self.user[chat_id]['active_matches'][message]
            if match[5] == 0:
                self.user[chat_id]['match'] = match
                reply = 'Wie viele Fragen hast du richtig beantwortet?'
                update.message.reply_text(
                    reply, reply_markup=ReplyKeyboardRemove())
                return self.MATCHES_PTS1
            elif match[5] == 2:
                self.user[chat_id]['match'] = match
                result = '{}:{}'.format(match[3], match[4])
                reply = 'Ist der Spielstand {} richtig?'.format(result)
                update.message.reply_text(
                    reply,
                    reply_markup=ReplyKeyboardMarkup(self.keyboards['yesno']))
                return self.MATCHES_VERIFY
        else:
            reply = ('Konnte das Spiel nicht finden. Welches Ergebnis möchtest '
                     'du eintragen?')
            update.message.reply_text(reply)

    def matches_pts1(self, update, context):
        # Speichert die Punktzahl des ersten Spielers
        chat_id = update.effective_chat.id
        message = update.message.text
        self.user_input(chat_id, message)
        if message.isdigit():
            res1 = int(message)
            if 0 <= res1 <= 18:
                self.user[chat_id]['res1'] = res1
                reply = 'Wie viele Fragen hat dein Gegner richtig beantwortet?'
                update.message.reply_text(reply)
                return self.MATCHES_PTS2
        reply = 'Bitte ein gültiges Ergebnis eingeben!'
        update.message.reply_text(reply)

    def matches_pts2(self, update, context):
        # Speichert die Punktzahl des zweiten Spielers
        chat_id = update.effective_chat.id
        message = update.message.text
        self.user_input(chat_id, message)
        if message.isdigit():
            res2 = int(message)
            if 0 <= res2 <= 18:
                self.user[chat_id]['res2'] = res2
                reply = 'Möchtest du das Ergebnis {}:{} eintragen?'.format(
                    self.user[chat_id]['res1'], res2)
                update.message.reply_text(
                    reply,
                    reply_markup=ReplyKeyboardMarkup(self.keyboards['yesno']))
                return self.MATCHES_CONFIRM
        reply = 'Bitte ein gültiges Ergebnis eingeben!'
        update.message.reply_text(reply)

    def matches_confirm(self, update, context):
        # Bestätigung, ob Ergebnis korrekt ist
        chat_id = update.effective_chat.id
        message = update.message.text
        self.user_input(chat_id, message)
        if message == 'Ja':
            match = self.user[chat_id]['match']
            p_id = self.user[chat_id]['p_id']
            res1 = self.user[chat_id]['res1']
            res2 = self.user[chat_id]['res2']
            self.parent.submit_result(match[0], p_id, res1, res2)
            if self.user[chat_id]['match'][5] == 0:
                reply = ('Das Ergebnis wurde eingetragen und muss nur noch von '
                         'deinem Gegner bestätigt werden!')
            elif self.user[chat_id]['match'][5] == 2:
                reply = ('Das korrigierte Ergebnis wurde abgeschickt und wird '
                         'jetzt vom Support bearbeitet!')
            update.message.reply_text(reply)
            self.user[chat_id].pop('match', None)
            self.user[chat_id].pop('active_matches', None)
            self.mainmenu(update, context)
            return ConversationHandler.END
        elif message == 'Nein':
            reply = 'Versuch es einfach nochmal!'
            update.message.reply_text(reply)
            self.mainmenu(update, context)
            return ConversationHandler.END
        self.user[chat_id].pop('active_matches', None)

    def matches_verify(self, update, context):
        # Bestätigen eines vom Gegner eingetragenen Ergebnisses
        # Möglichkeit das Ergebnis zu korrigieren, falls nicht richtig
        chat_id = update.effective_chat.id
        message = update.message.text
        self.user_input(chat_id, message)
        if message == 'Ja':
            match = self.user[chat_id]['match']
            p_id = self.user[chat_id]['p_id']
            self.parent.submit_result(match[0], p_id, match[3], match[4])
            reply = 'Das Ergebnis wurde bestätigt und eingetragen!'
            update.message.reply_text(reply)
            self.user[chat_id].pop('match', None)
            self.user[chat_id].pop('active_matches', None)
            self.mainmenu(update, context)
            return ConversationHandler.END
        elif message == 'Nein':
            reply = ('Bitte das Ergebnis korrigieren!\n\n'
                     'Wie viele Fragen hast du richtig beantwortet?')
            update.message.reply_text(reply, reply_markup=ReplyKeyboardRemove())
            return self.MATCHES_PTS1

    def league(self, update, context, log_input=True):
        # Menü für Liga (E1)
        # Aufgerufen über das Hauptmenü
        chat_id = update.effective_chat.id
        message = update.message.text
        if log_input:
            self.user_input(chat_id, message, True)
        # Daten von Spieler und Liga laden
        p_id = self.parent.get_p_id_from_input(self.INPUT_METHOD, chat_id)
        l_id = self.parent.get_player_league(p_id)
        if l_id:
            self.user[chat_id]['l_id'] = l_id
            name, season, _, _ = self.parent.get_league_info(l_id)
            update.message.reply_text(
                'Saison {}\n'
                'Du spielst in {}'.format(season, name),
                reply_markup=ReplyKeyboardMarkup(self.keyboards['league']))
            return self.LEAGUE
        else:
            update.message.reply_text(
                'Du musst dich in einer aktiven Liga befinden, bevor du diese '
                'aufrufen kannst!')
            self.mainmenu(update, context)
            return ConversationHandler.END

    def league_select(self, update, context):
        chat_id = update.effective_chat.id
        message = update.message.text
        self.user_input(chat_id, message)
        l_id = self.user[chat_id]['l_id']
        image = self.parent.generate_league_table(l_id)
        self.send_image(chat_id, image)
        return ConversationHandler.LEAGUE

    def statistics(self, update, context, log_input=True):
        # Menü für Statistiken (E1)
        # Aufgerufen über das Hauptmenü
        chat_id = update.effective_chat.id
        message = update.message.text
        if log_input:
            self.user_input(chat_id, message, True)
        update.message.reply_text(
            'Du kannst deine Statistiken mit denen der besten 10 Spieler '
            'anzeigen lassen!',
            reply_markup=ReplyKeyboardMarkup(self.keyboards['statistics']))
        return self.STATISTICS

    def statistics_select(self, update, context):
        chat_id = update.effective_chat.id
        message = update.message.text
        self.user_input(chat_id, message)
        p_id = self.parent.get_p_id_from_input(self.INPUT_METHOD, chat_id)
        if not p_id:
            update.message.reply_text(
                'Spiel bei der QDLiga mit um auch deine eigenen Statistiken zu '
                'sehen!',
                reply_markup=ReplyKeyboardMarkup(self.keyboards['statistics']))
            image = self.parent.generate_statistics_table(None)
            self.send_image(chat_id, image)
        else:
            image = self.parent.generate_statistics_table(p_id)
            self.send_image(chat_id, image)
        self.mainmenu(update, context)
        return ConversationHandler.END

    def account(self, update, context, log_input=True):
        # Menü für Account (E1)
        # Aufgerufen über das Hauptmenü
        # Leitet an Untermenüs weiter
        chat_id = update.effective_chat.id
        message = update.message.text
        if log_input:
            self.user_input(chat_id, message)
        update.message.reply_text(
            'Was möchtest du tun?',
            reply_markup=ReplyKeyboardMarkup(self.keyboards['account']))
        return self.ACCOUNT

    def register(self, update, context):
        # Menü für Registrieren (E2)
        # Aufgerufen über das Account-Menü
        # Abfragen des Nutzernamen für die Registrierung
        chat_id = update.effective_chat.id
        message = update.message.text
        self.user_input(chat_id, message, True)
        if self.parent.check_input_method_used('TelegramID', chat_id):
            update.message.reply_text(
                ('Dein Telegram-Account wurde bereits registriert.\n'
                 'Wenn du deinen Nutzernamen ändern willst, oder andere '
                 'Probleme hast, melde dich bitte beim Support!'))
            return self.account(update, context, False)  # Zurück zum Account-Menü
        else:
            update.message.reply_text(
                'Möchtest du dich für die QDLiga registrieren?',
                reply_markup=ReplyKeyboardMarkup(self.keyboards['yesno'],
                                                 one_time_keyboard=True))
            return self.REGISTER_YESNO

    def register_yesno(self, update, context):
        # Wertet die vorherige Antwort, ob sich der Nutzer registrieren will
        chat_id = update.effective_chat.id
        message = update.message.text
        self.user_input(chat_id, message)
        if message == 'Ja':
            update.message.reply_text(
                'Gib bitte deinen QD Nutzernamen ein!',
                reply_markup=ReplyKeyboardRemove())
            return self.REGISTER_NAME
        else:
            update.message.reply_text(
                'Wenn du es dir anders überlegst, versuch es einfach nochmal!')
            return self.account(update, context, False)  # Zurück zum Account-Menü

    def register_name(self, update, context):
        # Speichert den eingegebenen Nutzernamen ab
        # Fragt nach Bestätigung mit Ja/Nein Keyboard
        chat_id = update.effective_chat.id
        message = update.message.text
        self.user_input(chat_id, message)
        self.user[chat_id]['register_username'] = message
        update.message.reply_text(
            'Ist der QD-Name "{}" richtig?'.format(message),
            reply_markup=ReplyKeyboardMarkup(self.keyboards['yesno'],
                                             one_time_keyboard=True))
        return self.REGISTER_CONFIRM

    def register_confirm(self, update, context):
        # Wertet die vorherige Antwort aus, ob der Nutzer die Registrierung
        # bestätigen will
        # Schreibt den Nutzer und die TelegramID in die Datenbank
        # Gibt Fehlermeldungen zurück, falls nicht möglich
        chat_id = update.effective_chat.id
        message = update.message.text
        self.user_input(chat_id, message)
        if message == 'Ja':
            username = self.user[chat_id]['register_username']
            try:
                p_id = self.parent.register_new_player(username)
                self.user[chat_id]['p_id'] = p_id
                self.parent.add_input_method(p_id, self.INPUT_METHOD, chat_id)
                update.message.reply_text(('Du wurdest erfolgreich als "{}" '
                                           'registriert!'.format(username)))
                self.user[chat_id]['username'] = username
                self.user[chat_id].pop('register_username', None)
                return self.account(update, context, False)  # Zurück zum Account-Menü
            except BaseException as e:
                # Sende angepasste Fehlernachricht, sofern Fehler bekannt
                if str(e) == 'UNIQUE constraint failed: Player.TelegramID':
                    text = ('Du kannst dich mit deinem Telegram-Account nur '
                            'einmal anmelden!')
                elif str(e) == 'UNIQUE constraint failed: Player.Username':
                    text = 'Dieser Nutzername wurde bereits registriert!'
                else:
                    text = 'Fehler beim registrieren. Bitte versuch es nochmal!'
                self.user[chat_id].pop('username', None)
                self.user[chat_id].pop('register_username', None)
                update.message.reply_text(text)
                return self.account(update, context, False)  # Zurück zum Account-Menü
        else:
            self.user[chat_id].pop('username', None)
            update.message.reply_text(
                'Versuch es einfach nochmal!')
            return self.account(update, context, False)  # Zurück zum Account-Menü

    def status(self, update, context):
        # Menü für Status ändern (E2)
        # Aufgerufen über das Account-Menü
        # Ermöglicht das Ändern des Status
        chat_id = update.effective_chat.id
        message = update.message.text
        self.user_input(chat_id, message, True)
        try:
            p_id = self.parent.get_p_id_from_input(self.INPUT_METHOD, chat_id)
            if p_id:
                self.user[chat_id]['p_id'] = p_id
                status = self.parent.get_status(p_id)
                self.user[chat_id]['status'] = status
                if status == 0:  # Status 0 = Inaktiv
                    status = 'Inaktiv'
                elif status == 1:  # Status 1 = Aktiv
                    status = 'Aktiv'
                update.message.reply_text(
                    ('Dein aktueller Status ist "{}", möchtest du deinen '
                     'Status ändern?'.format(status)),
                    reply_markup=ReplyKeyboardMarkup(self.keyboards['yesno']))
                return self.STATUS_YESNO
            else:
                update.message.reply_text(
                    ('Du musst dich zuerst registrieren, bevor du deinen '
                     'Status ändern kannst!'))
                return self.account(update, context, False)  # Zurück zum Account-Menü
        except BaseException as e:
            update.message.reply_text(
                'Fehler beim Laden des Status. Bitte versuch es nochmal')
            return self.account(update, context, False)  # Zurück zum Account-Menü

    def status_yesno(self, update, context):
        chat_id = update.effective_chat.id
        message = update.message.text
        self.user_input(chat_id, message)
        if message == 'Ja':
            update.message.reply_text(
                'Auf was möchtest du deinen Status ändern?',
                reply_markup=ReplyKeyboardMarkup(self.keyboards['status']))
            return self.STATUS_CHOOSE
        else:
            update.message.reply_text(
                'Du kannst den Status jederzeit ändern.')
            return self.account(update, context, False)  # Zurück zum Account-Menü

    def status_choose(self, update, context):
        chat_id = update.effective_chat.id
        message = update.message.text
        self.user_input(chat_id, message)
        if message == 'Aktiv':
            status = 1
        elif message == 'Inaktiv':
            status = 0
        else:
            update.message.reply_text(('Ungültiger Status "{}". Bitte versuch '
                                       'es nochmal'.format(message)))
            return self.account(update, context, False)  # Zurück zum Account-Menü
        if self.user[chat_id]['status'] == status:
            update.message.reply_text(
                'Der Status ist bereits "{}".'.format(message))
            return self.account(update, context, False)  # Zurück zum Account-Menü
        else:
            self.user[chat_id]['status'] = status
            update.message.reply_text(
                'Status auf "{}" setzen?'.format(message),
                reply_markup=ReplyKeyboardMarkup(self.keyboards['yesno']))
            return self.STATUS_CONFIRM

    def status_confirm(self, update, context):
        chat_id = update.effective_chat.id
        message = update.message.text
        self.user_input(chat_id, message)
        if message == 'Ja':
            try:
                p_id = self.user[chat_id]['p_id']
                status = self.user[chat_id]['status']
                self.parent.set_status(p_id, status)
                update.message.reply_text(
                    'Status wurde erfolgreich geändert!')
                return self.account(update, context, False)  # Zurück zum Account-Menü
            except BaseException as e:
                print(str(e))
                update.message.reply_text(
                    'Fehler beim setzen des Status. Bitte versuch es nochmal!')
                self.user[chat_id].pop('status', None)
                return self.account(update, context)  # Zürück zum Account-Menü
        else:
            update.message.reply_text(
                'Versuch es einfach nochmal!')
            self.user[chat_id].pop('status', None)
            return self.account(update, context, False)  # Zurück zum Account-Menü
