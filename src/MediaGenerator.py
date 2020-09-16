#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw, ImageFont


class MediaGenerator:
    def __init__(self, parent):
        self.parent = parent

        # Schriftarten anlegen
        self.font = {}
        self.init_font()

        # Erstelle alle für die Statistik benötigten Bilder
        self.statistics = {}
        self.init_statistics()

    def init_font(self):
        # Achtung: Falsche Benennung der Variation ist ein Bug
        bahnschrift_26 = ImageFont.truetype('../media/bahnschrift.ttf', 36)
        bahnschrift_26.set_variation_by_name(b'SemiBold')
        self.font['bs_26'] = bahnschrift_26

        bahnschrift_26_condensed = ImageFont.truetype(
            '../media/bahnschrift.ttf', 36)
        bahnschrift_26_condensed.set_variation_by_name(b'SemiBold Condensed')
        self.font['bs_26_cond'] = bahnschrift_26_condensed

        bahnschrift_32 = ImageFont.truetype('../media/bahnschrift.ttf', 43)
        bahnschrift_32.set_variation_by_name(b'SemiBold')
        self.font['bs_32'] = bahnschrift_32

    def init_statistics(self):
        # Pixelgenauer Plan in /media/Statistik_Tabelle.pdn

        # --- Spaltenbeschriftung generieren ---
        # Schwarzes 1200x69 Bild generieren
        top = Image.new('RGBA', (1200, 69), (0, 0, 0))

        # Emojis laden
        # Wegen Bug nicht möglich diese als Text zu generieren
        matches = Image.open('../media/emojis/Matches.png').convert('RGBA')
        win = Image.open('../media/emojis/Win.png').convert('RGBA')
        draw_emoji = Image.open('../media/emojis/Draw.png').convert('RGBA')
        lose = Image.open('../media/emojis/Lose.png').convert('RGBA')
        notplayed = Image.open('../media/emojis/NotPlayed.png').convert('RGBA')
        correct = Image.open('../media/emojis/Correct.png').convert('RGBA')
        perfect = Image.open('../media/emojis/Perfect.png').convert('RGBA')
        points = Image.open('../media/emojis/Points.png').convert('RGBA')

        # Emojis auf Bild Platzieren
        top.alpha_composite(matches, (496, 15))
        top.alpha_composite(win, (583, 15))
        top.alpha_composite(draw_emoji, (670, 15))
        top.alpha_composite(lose, (757, 15))
        top.alpha_composite(notplayed, (844, 15))
        top.alpha_composite(correct, (943, 15))
        top.alpha_composite(perfect, (1030, 15))
        top.alpha_composite(points, (1117, 15))

        # Text auf Bild schreiben
        draw = ImageDraw.Draw(top)
        draw.text((26, 20), '#', font=self.font['bs_32'])
        draw.text((86, 20), 'Name', font=self.font['bs_32'])

        # Linien auf Bild schreiben
        draw.line([(477, 10), (477, 61)], width=3)
        draw.line([(564, 10), (564, 61)], width=3)
        draw.line([(912, 10), (912, 61)], width=3)
        draw.line([(1086, 10), (1086, 61)], width=3)

        self.statistics['top'] = top

        # --- Trennlinie generieren ---
        # Schwarzes 1200x9 Bild generieren
        line = Image.new('RGBA', (1200, 9), (0, 0, 0))
        draw = ImageDraw.Draw(line)

        # Linie ziehen
        draw.line([(10, 4), (1189, 4)], width=3)

        self.statistics['line'] = line

        # --- Legende generieren ---
        # Schwarzes 1200x110 Bild generieren
        legend = Image.new('RGBA', (1200, 110), (0, 0, 0))

        # Emojis auf Bild Platzieren
        legend.alpha_composite(matches, (10, 0))
        legend.alpha_composite(win, (183, 0))
        legend.alpha_composite(draw_emoji, (342, 0))
        legend.alpha_composite(lose, (650, 0))
        legend.alpha_composite(notplayed, (913, 0))
        legend.alpha_composite(correct, (10, 50))
        legend.alpha_composite(perfect, (331, 50))
        legend.alpha_composite(points, (647, 50))

        # Text auf Bild schreiben
        draw = ImageDraw.Draw(legend)
        draw.text((67, 9), 'Duelle', font=self.font['bs_26'])
        draw.text((240, 9), 'Siege', font=self.font['bs_26'])
        draw.text((399, 9), 'Unentschieden', font=self.font['bs_26'])
        draw.text((707, 9), 'Niederlagen', font=self.font['bs_26'])
        draw.text((970, 9), 'Nicht gespielt', font=self.font['bs_26'])
        draw.text((67, 59), 'Richtige Fragen', font=self.font['bs_26'])
        draw.text((388, 59), 'Perfekte Spiele', font=self.font['bs_26'])
        draw.text((704, 59), 'Punkte', font=self.font['bs_26'])

        self.statistics['legend'] = legend

    def generate_statistics(self, p_id=None):
        """Generiert Statistik-Tabelle der Top 10 und fügt ggf. die Statistik
        des Spielers an, der diese abrufen möchte"""
        # Pixelgenauer Plan in /media/Statistik_Tabelle.pdn

        # Liste mit Bildelementen. Diese werden nacheinander unten angefügt
        img_list = []

        # Kopfzeile zu Liste hinzufügen
        img_list.append(self.statistics['top'])

        # Statistik-Daten der Top 10 laden
        top10 = self.parent.get_stats_top10()

        # Methode um einzelne Spieler-Zeilen zu generieren
        def create_statistics_row(place, elem):
            # Schwarzes 1200x45 Bild generieren
            stat = Image.new('RGBA', (1200, 45), (0, 0, 0))
            draw = ImageDraw.Draw(stat)

            # Werte in entsprechende Spalte schreiben
            # Position
            (x, _) = draw.textsize('{}.'.format(place), font=self.font['bs_32'])
            xpos = 10 + max((60 - x) // 2, 0)
            draw.text((xpos, 3), '{}.'.format(place), font=self.font['bs_32'])
            # Name
            (x, _) = draw.textsize(elem[1], font=self.font['bs_26'])
            if x < 385:
                draw.text((85, 6), elem[1], font=self.font['bs_26'])
            else:
                draw.text((85, 6), elem[1], font=self.font['bs_26_cond'])
            # Duelle
            (x, _) = draw.textsize(str(elem[2]), font=self.font['bs_32'])
            xpos = 485 + (72 - x)
            draw.text((xpos, 3), str(elem[2]), font=self.font['bs_32'])
            # Siege
            (x, _) = draw.textsize(str(elem[3]), font=self.font['bs_32'])
            xpos = 572 + (72 - x)
            draw.text((xpos, 3), str(elem[3]), font=self.font['bs_32'])
            # Unentschieden
            (x, _) = draw.textsize(str(elem[4]), font=self.font['bs_32'])
            xpos = 659 + (72 - x)
            draw.text((xpos, 3), str(elem[4]), font=self.font['bs_32'])
            # Niederlagen
            (x, _) = draw.textsize(str(elem[5]), font=self.font['bs_32'])
            xpos = 746 + (72 - x)
            draw.text((xpos, 3), str(elem[5]), font=self.font['bs_32'])
            # Nicht gespielt
            (x, _) = draw.textsize(str(elem[6]), font=self.font['bs_32'])
            xpos = 833 + (72 - x)
            draw.text((xpos, 3), str(elem[6]), font=self.font['bs_32'])
            # Richtige Fragen
            (x, _) = draw.textsize(str(elem[7]), font=self.font['bs_32'])
            xpos = 920 + (96 - x)
            draw.text((xpos, 3), str(elem[7]), font=self.font['bs_32'])
            # Perfekte Spiele
            (x, _) = draw.textsize(str(elem[8]), font=self.font['bs_32'])
            xpos = 1031 + (48 - x)
            draw.text((xpos, 3), str(elem[8]), font=self.font['bs_32'])
            # Punkte
            (x, _) = draw.textsize(str(elem[9]), font=self.font['bs_32'])
            xpos = 1094 + (96 - x)
            draw.text((xpos, 3), str(elem[9]), font=self.font['bs_32'])

            return stat

        # Für jeden Eintrag eine Zeile generieren und nach Trennlinie einfügen
        place = 1
        for elem in top10:
            stat = create_statistics_row(place, elem)

            # Trennlinie und Zeile einfügen
            img_list.append(self.statistics['line'])
            img_list.append(stat)

            # Platzierungs-Counter um 1 erhöhen
            place += 1

        # Statistik des Spielers laden (falls übergeben)
        if p_id:
            player = self.parent.get_stats_single(p_id)
            # Statistik des Spielers hinzufügen, falls ausßerhalb der Top 10
            if player[0] > 10:
                stat = create_statistics_row(player[0], player[1:])

                img_list.append(self.statistics['line'])
                img_list.append(self.statistics['line'])
                img_list.append(stat)

        # Legende hinzufügen
        img_list.append(self.statistics['line'])
        img_list.append(self.statistics['line'])
        img_list.append(self.statistics['legend'])

        # Finales Bild zusammensetzen
        height = 0
        for elem in img_list:
            height += elem.height

        # Schwarzes 1200xheight Bild generieren
        statistics = Image.new('RGBA', (1200, height), (0, 0, 0))
        height = 0
        for elem in img_list:
            statistics.paste(elem, (0, height))
            height += elem.height

        return statistics
