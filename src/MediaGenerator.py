#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw, ImageFont
import numpy as np


class MediaGenerator:
    def __init__(self, parent):
        self.parent = parent

        # Auf True setzen, wenn auf Linux verwendet
        # Schrift wird um etwa 7px nach unten verschoben, wenn auf Linux
        self.using_linux = True
        if self.using_linux:
            self.offset = -7
        else:
            self.offset = 0

        # Schriftarten anlegen
        self.font = {}
        self.init_font()

        # Erstelle alle für die Liga benötigten Bilder
        self.league = {}
        self.init_league()

        # Erstelle alle für die Statistik benötigten Bilder
        self.statistics = {}
        self.init_statistics()

        # Erstelle alle für die Ergebnisliste benötigten Bilder
        self.result_list = {}
        self.init_result_list()

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

    def init_league(self):
        # Pixelgenauer Plan in doc/media/Liga_Tabelle.pdn

        # --- Spaltenbeschriftung generieren ---
        # Schwarzes 1300x72 Bild generieren
        top = Image.new('RGBA', (998, 72), (0, 0, 0))

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
        top.alpha_composite(matches, (484, 15))
        top.alpha_composite(win, (547, 15))
        top.alpha_composite(draw_emoji, (610, 15))
        top.alpha_composite(lose, (673, 15))
        top.alpha_composite(notplayed, (736, 15))
        top.alpha_composite(correct, (811, 15))
        top.alpha_composite(perfect, (886, 15))
        top.alpha_composite(points, (949, 15))

        # Text auf Bild schreiben
        draw = ImageDraw.Draw(top)
        draw.text((26, 20 + self.offset), '#', font=self.font['bs_32'])
        draw.text((86, 20 + self.offset), 'Name', font=self.font['bs_32'])

        # Linien auf Bild zeichnen
        draw.line([(477, 10), (477, 61)], width=3)
        draw.line([(540, 10), (540, 61)], width=3)
        draw.line([(792, 10), (792, 61)], width=3)
        draw.line([(942, 10), (942, 61)], width=3)

        self.league['top'] = top

        # --- Trennlinie generieren ---
        # Schwarzes 1200x3 Bild generieren
        line = Image.new('RGBA', (998, 3), (0, 0, 0))
        draw = ImageDraw.Draw(line)

        # Linie ziehen
        draw.line([(10, 1), (997, 1)], width=3)

        self.league['line'] = line

        # --- Legende generieren ---
        # Schwarzes 302x520 Bild generieren
        legend = Image.new('RGBA', (302, 520), (0, 0, 0))

        # Emojis auf Bild Platzieren
        legend.alpha_composite(matches, (15, 75))
        legend.alpha_composite(win, (15, 129))
        legend.alpha_composite(draw_emoji, (15, 183))
        legend.alpha_composite(lose, (15, 237))
        legend.alpha_composite(notplayed, (15, 291))
        legend.alpha_composite(correct, (15, 345))
        legend.alpha_composite(perfect, (15, 399))
        legend.alpha_composite(points, (15, 453))

        # Text auf Bild schreiben
        draw = ImageDraw.Draw(legend)
        draw.text((70, 84 + self.offset), 'Duelle', font=self.font['bs_26_cond'])
        draw.text((70, 138 + self.offset), 'Siege', font=self.font['bs_26_cond'])
        draw.text((70, 192 + self.offset), 'Unentschieden', font=self.font['bs_26_cond'])
        draw.text((70, 246 + self.offset), 'Niederlagen', font=self.font['bs_26_cond'])
        draw.text((70, 300 + self.offset), 'Nicht gespielt', font=self.font['bs_26_cond'])
        draw.text((70, 354 + self.offset), 'Richtige Fragen', font=self.font['bs_26_cond'])
        draw.text((70, 408 + self.offset), 'Perfekte Spiele', font=self.font['bs_26_cond'])
        draw.text((70, 462 + self.offset), 'Punkte', font=self.font['bs_26_cond'])

        # Linien auf Bild zeichnen
        draw.line([(7, 10), (7, 509)], width=3)
        draw.line([(15, 73), (291, 73)], width=3)

        self.league['legend'] = legend

        # --- Farbverlauf generieren ---
        # Schwarzes 510x1 Bild generieren
        gold = Image.new('RGBA', (510, 1), (0, 0, 0, 0))
        green = Image.new('RGBA', (510, 1), (0, 0, 0, 0))
        red = Image.new('RGBA', (510, 1), (0, 0, 0, 0))
        for i in range(255):
            gold.putpixel((2 * i, 0), (200, 170, 0, (255 - i)))
            gold.putpixel((2 * i + 1, 0), (200, 170, 0, (255 - i)))
            green.putpixel((2 * i, 0), (0, 255, 0, (255 - i)))
            green.putpixel((2 * i + 1, 0), (0, 255, 0, (255 - i)))
            red.putpixel((2 * i, 0), (255, 0, 0, (255 - i)))
            red.putpixel((2 * i + 1, 0), (255, 0, 0, (255 - i)))
        # Auf gewünschte Zielhöhe strecken
        gold = gold.resize((510, 51))
        green = green.resize((510, 51))
        red = red.resize((510, 51))

        self.league['gold'] = gold
        self.league['green'] = green
        self.league['red'] = red

    def generate_league_table(self, l_id, name, use_colors=0):
        """Generiert die Liga-Tabelle der übergebenen Liga.
        Durch use_colors wird festgelegt, ob bestimmte Felder farblich
        hinterlegt werden sollen.
        Mögliche Werte sind:
        0 - Keine Einfärbung
        1 - Platz 1 wird gold hinterlegt
        2 - Platz 1 wird gold hinterlegt, Platz 7 und 8 rot
        3 - Platz 1 und 2 werden grün hinterlegt
        4 - Platz 1 und 2 werden grün hinterlegt, Platz 7 und 8 rot"""
        # Pixelgenauer Plan in doc/media/Liga_Tabelle.pdn

        # Liste mit Bildelementen. Diese werden nacheinander unten angefügt
        # Die Legende wird zum Schluss an der Seite angefügt
        img_list = []

        # Kopfzeile zu Liste hinzufügen
        img_list.append(self.league['top'])
        img_list.append(self.league['line'])

        # Tabelle laden
        table = self.parent.get_league_table(l_id)

        # Methode um einzelne Spieler-Zeilen zu generieren
        # Bei color ggf. Farb-Hintergrund übergeben
        def create_league_row(place, elem, color=None):
            # Schwarzes 998x51 Bild generieren
            stat = Image.new('RGBA', (998, 51), (0, 0, 0))
            draw = ImageDraw.Draw(stat)

            # Nutzername ermitteln
            username = self.parent.get_username(elem[0])
            if not username:
                username = ''

            # Sofern angegeben Hintergrund setzen
            if color:
                stat.alpha_composite(color, (10, 0))

            # Werte in entsprechende Spalte schreiben
            # Position
            (x, _) = draw.textsize('{}.'.format(place), font=self.font['bs_32'])
            xpos = 10 + max((60 - x) // 2, 0)
            draw.text((xpos, 6 + self.offset), '{}.'.format(place), font=self.font['bs_32'])
            # Name
            (x, _) = draw.textsize(username, font=self.font['bs_26'])
            if x < 385:
                draw.text((85, 9 + self.offset), username, font=self.font['bs_26'])
            else:
                draw.text((85, 9 + self.offset), username, font=self.font['bs_26_cond'])
            # Duelle
            (x, _) = draw.textsize(str(elem[1]), font=self.font['bs_32'])
            xpos = 485 + (48 - x)
            draw.text((xpos, 6 + self.offset), str(elem[1]), font=self.font['bs_32'])
            # Siege
            (x, _) = draw.textsize(str(elem[2]), font=self.font['bs_32'])
            xpos = 548 + (48 - x)
            draw.text((xpos, 6 + self.offset), str(elem[2]), font=self.font['bs_32'])
            # Unentschieden
            (x, _) = draw.textsize(str(elem[3]), font=self.font['bs_32'])
            xpos = 611 + (48 - x)
            draw.text((xpos, 6 + self.offset), str(elem[3]), font=self.font['bs_32'])
            # Niederlagen
            (x, _) = draw.textsize(str(elem[4]), font=self.font['bs_32'])
            xpos = 674 + (48 - x)
            draw.text((xpos, 6 + self.offset), str(elem[4]), font=self.font['bs_32'])
            # Nicht gespielt
            (x, _) = draw.textsize(str(elem[5]), font=self.font['bs_32'])
            xpos = 737 + (48 - x)
            draw.text((xpos, 6 + self.offset), str(elem[5]), font=self.font['bs_32'])
            # Richtige Fragen
            (x, _) = draw.textsize(str(elem[6]), font=self.font['bs_32'])
            xpos = 800 + (72 - x)
            draw.text((xpos, 6 + self.offset), str(elem[6]), font=self.font['bs_32'])
            # Perfekte Spiele
            (x, _) = draw.textsize(str(elem[7]), font=self.font['bs_32'])
            xpos = 887 + (48 - x)
            draw.text((xpos, 6 + self.offset), str(elem[7]), font=self.font['bs_32'])
            # Punkte
            (x, _) = draw.textsize(str(elem[8]), font=self.font['bs_32'])
            xpos = 950 + (48 - x)
            draw.text((xpos, 6 + self.offset), str(elem[8]), font=self.font['bs_32'])

            return stat

        # Für jeden Eintrag eine Zeile generieren und eine Trennlinie einfügen
        place = 1
        for elem in table:
            color = None
            if 1 <= use_colors <= 2 and place == 1:
                color = self.league['gold']
            elif 3 <= use_colors <= 4 and 1 <= place <= 2:
                color = self.league['green']
            elif (use_colors == 2 or use_colors == 4) and 7 <= place <= 8:
                color = self.league['red']

            stat = create_league_row(place, elem, color)

            # Zeile und Trennlinie einfügen
            img_list.append(stat)
            img_list.append(self.league['line'])

            place += 1

        # Finales Bild zusammensetzen
        # Schwarzes 1300x517 Bild generieren
        league = Image.new('RGBA', (1300, 517), (0, 0, 0))
        height = 0
        for elem in img_list:
            league.paste(elem, (0, height))
            height += elem.height

        # Legende einfügen
        league.paste(self.league['legend'], (998, 0))

        # Liga-Name über Legende hinzufügen
        draw = ImageDraw.Draw(league)
        (x, _) = draw.textsize(name, font=self.font['bs_32'])
        xpos = 1013 + (277 - x) // 2
        draw.text((xpos, 16 + self.offset), name, font=self.font['bs_32'])

        return league

    def init_statistics(self):
        # Pixelgenauer Plan in doc/media/Statistik_Tabelle.pdn

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
        draw.text((26, 20 + self.offset), '#', font=self.font['bs_32'])
        draw.text((86, 20 + self.offset), 'Name', font=self.font['bs_32'])

        # Linien auf Bild zeichnen
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
        draw.text((67, 9 + self.offset), 'Duelle', font=self.font['bs_26'])
        draw.text((240, 9 + self.offset), 'Siege', font=self.font['bs_26'])
        draw.text((399, 9 + self.offset), 'Unentschieden', font=self.font['bs_26'])
        draw.text((707, 9 + self.offset), 'Niederlagen', font=self.font['bs_26'])
        draw.text((970, 9 + self.offset), 'Nicht gespielt', font=self.font['bs_26'])
        draw.text((67, 59 + self.offset), 'Richtige Fragen', font=self.font['bs_26'])
        draw.text((388, 59 + self.offset), 'Perfekte Spiele', font=self.font['bs_26'])
        draw.text((704, 59 + self.offset), 'Punkte', font=self.font['bs_26'])

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
            draw.text((xpos, 3 + self.offset), '{}.'.format(place), font=self.font['bs_32'])
            # Name
            (x, _) = draw.textsize(elem[1], font=self.font['bs_26'])
            if x < 385:
                draw.text((85, 6 + self.offset), elem[1], font=self.font['bs_26'])
            else:
                draw.text((85, 6 + self.offset), elem[1], font=self.font['bs_26_cond'])
            # Duelle
            (x, _) = draw.textsize(str(elem[2]), font=self.font['bs_32'])
            xpos = 485 + (72 - x)
            draw.text((xpos, 3 + self.offset), str(elem[2]), font=self.font['bs_32'])
            # Siege
            (x, _) = draw.textsize(str(elem[3]), font=self.font['bs_32'])
            xpos = 572 + (72 - x)
            draw.text((xpos, 3 + self.offset), str(elem[3]), font=self.font['bs_32'])
            # Unentschieden
            (x, _) = draw.textsize(str(elem[4]), font=self.font['bs_32'])
            xpos = 659 + (72 - x)
            draw.text((xpos, 3 + self.offset), str(elem[4]), font=self.font['bs_32'])
            # Niederlagen
            (x, _) = draw.textsize(str(elem[5]), font=self.font['bs_32'])
            xpos = 746 + (72 - x)
            draw.text((xpos, 3 + self.offset), str(elem[5]), font=self.font['bs_32'])
            # Nicht gespielt
            (x, _) = draw.textsize(str(elem[6]), font=self.font['bs_32'])
            xpos = 833 + (72 - x)
            draw.text((xpos, 3 + self.offset), str(elem[6]), font=self.font['bs_32'])
            # Richtige Fragen
            (x, _) = draw.textsize(str(elem[7]), font=self.font['bs_32'])
            xpos = 920 + (96 - x)
            draw.text((xpos, 3 + self.offset), str(elem[7]), font=self.font['bs_32'])
            # Perfekte Spiele
            (x, _) = draw.textsize(str(elem[8]), font=self.font['bs_32'])
            xpos = 1031 + (48 - x)
            draw.text((xpos, 3 + self.offset), str(elem[8]), font=self.font['bs_32'])
            # Punkte
            (x, _) = draw.textsize(str(elem[9]), font=self.font['bs_32'])
            xpos = 1094 + (96 - x)
            draw.text((xpos, 3 + self.offset), str(elem[9]), font=self.font['bs_32'])

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
        # Die einzelnen Zeilen untereinander kopieren
        for elem in img_list:
            statistics.paste(elem, (0, height))
            height += elem.height

        return statistics

    def init_result_list(self):
        # Pixelgenauer Plan in doc/media/Liga_Ergebnisse.pdn

        # --- Trennlinie generieren ---
        # Schwarzes 1450x10 Bild generieren
        line = Image.new('RGBA', (1450, 10), (0, 0, 0))
        draw = ImageDraw.Draw(line)

        # Linie auf Bild zeichnen
        draw.line([(10, 4), (1439, 4)], width=4)
        self.result_list['line'] = line

        # --- Farbverlauf-Umrandung generieren ---
        # Transparenz-Matrix berechnen (350x10, Verlauf von oben nach unten,
        #  Verlauf 150px von links, Verlauf 100x von rechts)

        # Erste Zeile mit vollen Farben
        horizontal = np.zeros(350)
        # Farbverlauf von links
        step = 255 / 150
        current = 0
        for i in range(150):
            horizontal[i] = np.rint(current)
            current += step
        # Kein Farbverlauf in der Mitte
        horizontal[150:250] = 255
        # Farbverlauf nach rechts
        step = 255 / 100
        current = 255
        for i in range(100):
            horizontal[250 + i] = np.rint(current)
            current -= step
        horizontal = horizontal.reshape((1, 350))

        # Farbverlauf nach unten
        vertical = np.zeros(10)
        for i in range(10):
            vertical[i] = 1 - (0.1 * i)
        vertical = vertical.reshape((10, 1))

        # Beide Vektoren zu Matrix multiplizieren
        transp = np.dot(vertical, horizontal)
        transp = np.rint(transp)

        # Linke Seite für alle Farben erstellen
        # Schwarzes 350x40 Bild generieren
        green_l = Image.new('RGBA', (350, 40), (0, 0, 0, 0))
        yellow_l = Image.new('RGBA', (350, 40), (0, 0, 0, 0))
        red_l = Image.new('RGBA', (350, 40), (0, 0, 0, 0))
        gray_l = Image.new('RGBA', (350, 40), (0, 0, 0, 0))

        # Für Oberseite die Farben mit entsprechender Transparenz setzen
        for y in range(transp.shape[0]):
            for x in range(transp.shape[1]):
                green_l.putpixel((x, y), (0, 255, 0, (int(transp[y, x]))))
                yellow_l.putpixel((x, y), (255, 216, 0, (int(transp[y, x]))))
                red_l.putpixel((x, y), (255, 0, 0, (int(transp[y, x]))))
                gray_l.putpixel((x, y), (192, 192, 192, (int(transp[y, x]))))

        # Oberseite flippen und nach unten kopieren
        green = green_l.crop((0, 0, 350, 10)).transpose(Image.FLIP_TOP_BOTTOM)
        green_l.paste(green, (0, 30, 350, 40))
        yellow = yellow_l.crop((0, 0, 350, 10)).transpose(Image.FLIP_TOP_BOTTOM)
        yellow_l.paste(yellow, (0, 30, 350, 40))
        red = red_l.crop((0, 0, 350, 10)).transpose(Image.FLIP_TOP_BOTTOM)
        red_l.paste(red, (0, 30, 350, 40))
        gray = gray_l.crop((0, 0, 350, 10)).transpose(Image.FLIP_TOP_BOTTOM)
        gray_l.paste(gray, (0, 30, 350, 40))

        self.result_list['green_l'] = green_l
        self.result_list['yellow_l'] = yellow_l
        self.result_list['red_l'] = red_l
        self.result_list['gray_l'] = gray_l

        # Umrandung nach rechts spiegeln
        self.result_list['green_r'] = green_l.transpose(Image.FLIP_LEFT_RIGHT)
        self.result_list['yellow_r'] = yellow_l.transpose(Image.FLIP_LEFT_RIGHT)
        self.result_list['red_r'] = red_l.transpose(Image.FLIP_LEFT_RIGHT)
        self.result_list['gray_r'] = gray_l.transpose(Image.FLIP_LEFT_RIGHT)

    def generate_result_list(self, l_id):
        """Generiert Ergebnisliste der übergebenen Liga"""
        # Pixelgenauer Plan in doc/media/Liga_Ergebnisse.pdn

        # Liste mit Bildelementen. Diese werden nacheinander unten angefügt
        img_list = []

        # Liga-Daten laden
        league, season, _, _, = self.parent.get_league_info(l_id)
        matches = self.parent.get_league_matches(l_id, include_names=True)

        # Duelle auf Hin- und Rückrunde aufteilen
        # Duelle in Form: (P1_Name, P2_Name, Res1, Res2, Pts1, Pts2, Verified)
        round1 = []
        round2 = []
        for m in matches:
            if m[2] == 1:
                round1.append((m[10], m[11], m[5], m[6], m[7], m[8], m[9]))
            elif m[2] == 2:
                round2.append((m[10], m[11], m[5], m[6], m[7], m[8], m[9]))

        # Kopfzeile erstellen und einfügen
        # Schwarzes 1450x55 Bild generieren
        head = Image.new('RGBA', (1450, 55), (0, 0, 0))
        draw = ImageDraw.Draw(head)
        # Liga und Saison in Kopfzeile schreiben
        text = 'Saison {} - {}'.format(season, league)
        x, _ = draw.textsize(text, font=self.font['bs_32'])
        xpos = (1450 - x) // 2
        draw.text((xpos, 8 + self.offset), text, font=self.font['bs_32'])
        img_list.append(head)

        # Trennlinie einfügen
        img_list.append(self.result_list['line'])

        def create_single_entry(match):
            name_left = match[0]
            name_right = match[1]
            if match[6] == 3:
                result = '{}:{}'.format(match[2], match[3])
            else:
                result = '-:-'

            # Schwarzes 700x45 Bild generieren
            entry = Image.new('RGBA', (700, 45), (0, 0, 0))
            draw = ImageDraw.Draw(entry)

            # Hintergrundfarbe
            if match[6] == 3:
                # Spieler 1
                if match[4] == 5:
                    entry.alpha_composite(self.result_list['green_l'], (0, 0))
                elif match[4] == 3:
                    entry.alpha_composite(self.result_list['yellow_l'], (0, 0))
                elif match[4] == 1:
                    entry.alpha_composite(self.result_list['red_l'], (0, 0))
                elif match[4] == 0:
                    entry.alpha_composite(self.result_list['gray_l'], (0, 0))
                # Spieler 2
                if match[5] == 5:
                    entry.alpha_composite(self.result_list['green_r'], (350, 0))
                elif match[5] == 3:
                    entry.alpha_composite(self.result_list['yellow_r'], (350, 0))
                elif match[5] == 1:
                    entry.alpha_composite(self.result_list['red_r'], (350, 0))
                elif match[5] == 0:
                    entry.alpha_composite(self.result_list['gray_r'], (350, 0))

            # Spieler 1, rechtsbündig
            x, _ = draw.textsize(name_left, font=self.font['bs_26'])
            xpos = 290 - x
            draw.text((xpos, 4 + self.offset), name_left,
                      font=self.font['bs_26'])
            # Ergebnis, mittig
            x, _ = draw.textsize(result, font=self.font['bs_26'])
            xpos = 310 + (80 - x) // 2
            draw.text((xpos, 4 + self.offset), result, font=self.font['bs_26'])
            # Spieler 2, linksbündig
            draw.text((410, 4 + self.offset), name_right,
                      font=self.font['bs_26'])

            return entry

        # Liste Hinrunde erstellen
        round1_list = []
        # Überschrift Hinrunde
        round1_top = Image.new('RGBA', (700, 45), (0, 0, 0))
        draw = ImageDraw.Draw(round1_top)
        x, _ = draw.textsize('Hinrunde', font=self.font['bs_32'])
        xpos = (700 - x) // 2
        draw.text((xpos, 4 + self.offset), 'Hinrunde', font=self.font['bs_32'])
        round1_list.append(round1_top)
        # Einzelne Matches
        for match in round1:
            round1_list.append(create_single_entry(match))
        # Hinrunde-Liste zusammensetzen
        height = 0
        for elem in round1_list:
            height += elem.height
        # Schwarzes 700xheight Bild generieren
        round1 = Image.new('RGBA', (700, height), (0, 0, 0))
        height = 0
        # Die einzelnen Zeilen untereinander kopieren
        for elem in round1_list:
            round1.paste(elem, (0, height))
            height += elem.height

        # Liste Rückrunde erstellen
        round2_list = []
        # Überschrift Hinrunde
        round2_top = Image.new('RGBA', (700, 45), (0, 0, 0))
        draw = ImageDraw.Draw(round2_top)
        x, _ = draw.textsize('Rückrunde', font=self.font['bs_32'])
        xpos = (700 - x) // 2
        draw.text((xpos, 4 + self.offset), 'Rückrunde', font=self.font['bs_32'])
        round2_list.append(round2_top)
        # Einzelne Matches
        for match in round2:
            round2_list.append(create_single_entry(match))
        # Rückrunde-Liste zusammensetzen
        height = 0
        for elem in round2_list:
            height += elem.height
        # Schwarzes 700xheight Bild generieren
        round2 = Image.new('RGBA', (700, height), (0, 0, 0))
        height = 0
        # Die einzelnen Zeilen untereinander kopieren
        for elem in round2_list:
            round2.paste(elem, (0, height))
            height += elem.height

        # Beide Listen zusammenfügen
        height = max(round1.height, round2.height)
        # Schwarzes 1450xheight Bild generieren
        rounds = Image.new('RGBA', (1450, height), (0, 0, 0))
        rounds.paste(round1, (0, 0))
        rounds.paste(round2, (740, 0))
        # Trennlinie hinzufügen
        draw = ImageDraw.Draw(rounds)
        draw.line([(724, 0), (724, height)], width=4)

        img_list.append(rounds)

        # Finales Bild zusammensetzen
        height = 0
        for elem in img_list:
            height += elem.height

        # Schwarzes 1450xheight Bild generieren
        result_list = Image.new('RGBA', (1450, height), (0, 0, 0))
        height = 0
        # Die einzelnen Zeilen untereinander kopieren
        for elem in img_list:
            result_list.paste(elem, (0, height))
            height += elem.height

        return result_list
