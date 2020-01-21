#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler,
                          ConversationHandler, Filters)
import threading


class TelegramBot:
    def __init__(self, parent, log):
        # Logger setzen
        self.log = log

        # Verbindung zur QDLiga
        self.parent = parent

        # Bot-Attribute festlegen
        self.updater = Updater(
            token='TOKEN',
            use_context=True)
        self.dispatcher = self.updater.dispatcher

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

    def stop(self):
        # Lösung aus dem Forum
        # https://github.com/python-telegram-bot/python-telegram-bot/issues/801
        def shutdown():
            self.updater.stop()
            self.updater.is_idle = False
        threading.Thread(target=shutdown).start()

    def add_all_handler(self):
        # Handler registrieren
        # CommandHandler
        start_handler = CommandHandler('start', self.start)
        self.dispatcher.add_handler(start_handler)
        cancel_handler = CommandHandler('cancel', self.cancel)
        self.dispatcher.add_handler(cancel_handler)
        # MessageHandler
        # answer_handler = MessageHandler(Filters.text, self.answer)
        # self.dispatcher.add_handler(answer_handler)
        # ConversationHandler
        self.add_conversationhandler()

    def create_keyboards(self):
        # Speichert alle möglichen Keyboards, sodass diese nicht immer neu
        # erstellt werden müssen
        self.keyboards['yesno'] = [['Ja', 'Nein']]  # Ja/Nein
        self.keyboards['main'] = [['Eintragen', 'Spielplan'],
                                  ['Tabelle', 'Account'],
                                  ['Support', 'Mehr']]  # Hauptmenü

    def add_conversationhandler(self):
        # Handler und Zustände für /register
        self.REGISTER_YESNO = 1
        self.REGISTER_NAME = 2
        self.REGISTER_CONFIRM = 3
        self.REGISTER_END = ConversationHandler.END
        register_handler = ConversationHandler(
            entry_points=[CommandHandler('register', self.register)],
            states={
                self.REGISTER_YESNO: [MessageHandler(
                    Filters.regex('^(Ja|Nein)$'), self.register_yesno)],
                self.REGISTER_NAME: [MessageHandler(
                    Filters.text, self.register_name)],
                self.REGISTER_CONFIRM: [MessageHandler(
                    Filters.regex('^(Ja|Nein)$'), self.register_confirm)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)]
        )
        self.dispatcher.add_handler(register_handler)

    def start(self, update, context):
        # Ausgeführt bei /start
        chat_id = update.effective_chat.id
        text = 'Willkommen in der QDLiga!\n' \
               'Hier entsteht der Telegram-Bot um die QDLiga zu nutzen. ' \
               'Leider ist noch nicht alles fertig, also komm doch bitte ' \
               'bald wieder!\n' \
               'Du kannst dich aber schonmal mit /register registrieren!'
        print('{}: /start'.format(chat_id))
        context.bot.send_message(chat_id=chat_id, text=text)

    def answer(self, update, context):
        # TODO löschen, weil nicht gebraucht
        chat_id = update.effective_chat.id
        text = update.message.text
        print('{}: {}'.format(chat_id, text))
        context.bot.send_message(chat_id=chat_id, text=text)

    def register(self, update, context):
        # Wird mit /register aufgerufen
        # Startet die Conversation zum abfragen des Nutzernamen für die
        # Registrierung
        # Fragt durch Ja/Nein-Keyboard ob man sich registrieren möchte
        chat_id = update.effective_chat.id
        if self.parent.check_input_method_used('TelegramID', chat_id):
            update.message.reply_text(
                ('Dein Telegram-Account wurde bereits registriert.\n'
                 'Wenn du deinen Nutzernamen ändern willst, oder andere '
                 'Probleme hast, melde dich bitte beim Support: /support'))
            return self.REGISTER_END
        else:
            update.message.reply_text(
                'Möchtest du dich für die QDLiga registrieren?',
                reply_markup=ReplyKeyboardMarkup(self.keyboards['yesno'],
                                                 one_time_keyboard=True))
            return self.REGISTER_YESNO

    def register_yesno(self, update, context):
        # Wertet die vorherige Antwort, ob sich der Nutzer registrieren will
        chat_id = update.effective_chat.id
        text = update.message.text
        if text == 'Ja':
            update.message.reply_text(
                'Gib bitte deinen QD Nutzernamen ein!',
                reply_markup=ReplyKeyboardRemove())
            return self.REGISTER_NAME
        else:
            update.message.reply_text(
                'Wenn du es dir anders überlegst, Gib einfach /register ein!',
                reply_markup=ReplyKeyboardRemove())
            return self.REGISTER_END

    def register_name(self, update, context):
        # Speichert den eingegebenen Nutzernamen ab
        # Fragt nach Bestätigung mit Ja/Nein Keyboard
        chat_id = update.effective_chat.id
        text = update.message.text
        if chat_id not in self.user:
            self.user[chat_id] = {}
        self.user[chat_id]['username'] = text
        update.message.reply_text(
            'Ist der QD-Name "{}" richtig?'.format(text),
            reply_markup=ReplyKeyboardMarkup(self.keyboards['yesno'],
                                             one_time_keyboard=True))
        return self.REGISTER_CONFIRM

    def register_confirm(self, update, context):
        # Wertet die vorherige Antwort aus, ob der Nutzer die Registrierung
        # bestätigen will
        # Schreibt den Nutzer und die TelegramID in die Datenbank
        # Gibt Fehlermeldungen zurück, falls nicht möglich
        chat_id = update.effective_chat.id
        text = update.message.text
        if text == 'Ja':
            username = self.user[chat_id]['username']
            try:
                p_id = self.parent.register_new_player(username)
                self.user[chat_id][p_id] = p_id
                self.parent.add_input_method(p_id, 'TelegramID', chat_id)
                text = ('Du wurdest erfolgreich als "{}" registriert!'
                        .format(username))
            except BaseException as e:
                # Sende angepasste Fehlernachricht, sofern Fehler bekannt
                if str(e) == 'UNIQUE constraint failed: Player.TelegramID':
                    text = ('Du kannst dich mit deinem Telegram-Account nur '
                            'einmal anmelden!')
                elif str(e) == 'UNIQUE constraint failed: Player.Username':
                    text = 'Dieser Nutzername wurde bereits registriert!'
                else:
                    text = ('Fehler beim registrieren. Bitte versuch es '
                            'nochmal: /register')
            update.message.reply_text(
                text,
                reply_markup=ReplyKeyboardRemove())
            return self.REGISTER_END
        else:
            self.user[chat_id].pop('username', None)
            update.message.reply_text(
                'Versuch es einfach nochmal: /register',
                reply_markup=ReplyKeyboardRemove())
            return self.REGISTER_END

    def cancel(self, update, context):
        # TODO implement
        print('Cancel')
        chat_id = update.effective_chat.id
        context.bot.send_message(chat_id=chat_id, text='Abgebrochen')
