#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import threading


class TelegramBot:
    def __init__(self, parent):
        # Verbindung zur QDLiga
        self.parent = parent

        # Bot-Attribute festlegen
        self.updater = Updater(
            token='TOKEN',
            use_context=True)
        self.dispatcher = self.updater.dispatcher

        # Handler registrieren
        self.register_handler()

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

    def register_handler(self):
        # Handler registrieren
        # CommandHandler
        start_handler = CommandHandler('start', self.start)
        self.dispatcher.add_handler(start_handler)
        test_handler = CommandHandler('test', self.test)
        self.dispatcher.add_handler(test_handler)
        # MessageHandler
        answer_handler = MessageHandler(Filters.text, self.answer)
        self.dispatcher.add_handler(answer_handler)

    # Ausgeführt bei /start
    def start(self, update, context):
        chat_id = update.effective_chat.id
        text = 'Willkommen in der QDLiga!\n' \
               'Hier entsteht der Telegram-Bot um die QDLiga zu nutzen. Leider ' \
               'ist noch nicht alles fertig, also komm doch bitte bald wieder!'
        print('{}: /start'.format(chat_id))
        context.bot.send_message(chat_id=chat_id, text=text)

    def answer(self, update, context):
        chat_id = update.effective_chat.id
        text = update.message.text
        print('{}: {}'.format(chat_id, text))
        context.bot.send_message(chat_id=chat_id, text=text)

    def test(self, update, context):
        chat_id = update.effective_chat.id
        id = self.parent.test(chat_id)
        context.bot.send_message(chat_id=chat_id, text='Du hast jetzt die ID '
                                                       '{}'.format(id))
