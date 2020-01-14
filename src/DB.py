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
            print(e)
            raise Exception('Fehler beim schließen der Verbindung.\n' + e)
