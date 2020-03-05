#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler,
                          ConversationHandler, Filters)
from TelegramTimer import TelegramTimer
import threading


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

        # Handler registrieren
        self.add_all_handler()

        # Keyboards anlegen
        self.keyboards = {}
        self.create_keyboards()

        # Informationen für Nutzer werden hier zwischengespeichert
        self.user = {}

        # Timer für Timeout wird gestartet
        self.timer = TelegramTimer(self)
        self.log.log_info('TelegramTimer gestartet!')

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
        self.ACCOUNT = 400
        self.REGISTER = 410
        self.REGISTER_YESNO = 411
        self.REGISTER_NAME = 412
        self.REGISTER_CONFIRM = 413

        # Menüs als Conversations. Im Hauptmenü können die verschiedenen Menüs
        # aufgerufen werden (Ebene 1, E1). Deren Untermenüs (E2, ...) müssen
        # jedoch zuerst implementiert werden, somit erfolgt die Reihenfolge von
        # unten nach oben.
        default_handler = ConversationHandler(
            entry_points=[],
            states={},
            fallbacks=[CommandHandler('cancel', self.cancel)],
            map_to_parent={}
        )
        go_back_handler = MessageHandler(Filters.regex('^(Zurück)$'),
                                         self.go_back)  # Zurück ins Hauptmenü

        # Menü: Eintragen (E1)
        # TODO Implementieren

        # Menü: Spielplan (E1)
        # TODO Implementieren

        # Menü: Tabelle (E1)
        # TODO Implementieren

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
            }
        )

        # Account (E1)
        account_handler = ConversationHandler(
            entry_points=[MessageHandler(Filters.regex('^(Account)$'),
                                         self.account)],
            states={
                self.ACCOUNT: [register_handler,
                               go_back_handler],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)]
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
        self.keyboards['main'] = [['Eintragen', 'Spielplan'],
                                  ['Tabelle', 'Account'],
                                  ['Support', 'Mehr']]  # Hauptmenü
        self.keyboards['account'] = [['Registrieren', 'Zurück']]  # Account

    def stop(self):
        # Timer beenden
        self.timer.stop()

        # Lösung aus dem Forum
        # https://github.com/python-telegram-bot/python-telegram-bot/issues/801
        def shutdown():
            self.updater.stop()
            self.updater.is_idle = False
        threading.Thread(target=shutdown).start()

    def cancel(self, update, context):
        # Wird mit /cancel aufgerufen und bricht aktuelle Vorgänge ab
        chat_id = update.effective_chat.id
        message = update.message.text
        self.user_input(chat_id, message, check_user=True)
        # Wenn /register abgebrochen wird:
        self.user[chat_id].pop('register_username', None)
        update.message.reply_text('Abgebrochen.')
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
        self.timer.update(chat_id)  # Erneuert den Timestamp im Timer
        self.log.log_input('{}: {}'.format(chat_id, message))

    def timeout(self, chat_id):
        # TODO implement
        pass

    def mainmenu(self, update, context):
        # Hauptmenü
        # Aufgerufen mit /start
        # Anzeigen der weiteren Menüpunkte
        chat_id = update.effective_chat.id
        message = update.message.text
        self.user_input(chat_id, message, check_user=True)
        text = 'Willkommen in der QDLiga!\n' \
               'Hier entsteht der Telegram-Bot um die QDLiga zu nutzen.\n' \
               'Bisher kannst du dich schon im Menü "Account" registrieren!\n' \
               'Komm bitte bald wieder, um den fertigen Bot zu nutzen!'
        update.message.reply_text(
            text, reply_markup=ReplyKeyboardMarkup(self.keyboards['main']))

    def account(self, update, context):
        # Menü für Account (E1)
        # Aufgerufen mit /account oder über das Hauptmenü
        # Leitet an Untermenüs weiter
        chat_id = update.effective_chat.id
        message = update.message.text
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
            return self.account(update, context)  # Zurück zum Account-Menü
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
            return self.account(update, context)  # Zurück zum Account-Menü

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
                return self.account(update, context)  # Zurück zum Account-Menü
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
                return self.account(update, context)  # Zurück zum Account-Menü
        else:
            self.user[chat_id].pop('username', None)
            update.message.reply_text(
                'Versuch es einfach nochmal!')
            return self.account(update, context)  # Zurück zum Account-Menü
