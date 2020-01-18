#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Logger:
    def __init__(self, filepath='', filename='log.txt'):
        self.filepath = filepath
        self.filename = filename

    def log_notification(self, text, exception=None):
        # Log für wichtige Dinge, die den Admins mitgeteilt werden sollte
        print(text)
        if exception:
            print(exception)

    def log_error(self, text, exception=None):
        # Log für Dinge, die unerwartet schiefgegangen sind
        print(text)
        if exception:
            print(exception)

    def log_exception(self, text, exception=None):
        # Log für Fehler, die korrekt abgefangen und behandelt wurden
        print(text)
        if exception:
            print(exception)

    def log_input(self, text):
        # Log für alle Eingaben
        print(text)

    def log_info(self, text):
        # Log für alle Infos der Komponenten
        print(text)
