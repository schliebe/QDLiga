-- Für die Datenbank kann entweder die default DB verwendet oder diese SQL-Befehle ausgeführt werden
CREATE DATABASE qdliga

-- Einstellungen der QDLiga
CREATE TABLE "Settings" (
	"Season"	INTEGER NOT NULL UNIQUE,
	"Round"	INTEGER NOT NULL UNIQUE,
	PRIMARY KEY("Season","Round")
)

-- Standardwerte für Settings
INSERT INTO "Settings" ("Season", "Round") VALUES ('1', '1');

-- Zeitlich festgelegte Events
CREATE TABLE "Events" (
	"Timestamp"	TEXT NOT NULL UNIQUE,
	"Event"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("Timestamp","Event")
)

-- Ligen
CREATE TABLE "League" (
	"L_ID"	INTEGER NOT NULL UNIQUE,
	"Name"	TEXT NOT NULL,
	"Season"	INTEGER NOT NULL,
	"Players"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("L_ID")
)

-- Warteliste
INSERT INTO "League" ("L_ID", "Name", "Season", "Players") VALUES ('0', 'Warteliste', '0', '0');

-- Informationen zu den einzelnen Spielern
CREATE TABLE "Player" (
	"P_ID"	INTEGER UNIQUE,
	"Username"	TEXT NOT NULL UNIQUE,
	"Status"	INTEGER NOT NULL DEFAULT 0,
	"TelegramID"	TEXT UNIQUE,
	PRIMARY KEY("P_ID")
)

-- Verknüpfung zwischen Liga und Spieler
CREATE TABLE "InLeague" (
	"League"	INTEGER NOT NULL,
	"Player"	INTEGER NOT NULL,
	FOREIGN KEY("League") REFERENCES "League"("L_ID"),
	PRIMARY KEY("League","Player"),
	FOREIGN KEY("Player") REFERENCES "Player"("P_ID")
)

-- Ergebnisse der einzelnen Spiele
CREATE TABLE "Match" (
	"M_ID"	INTEGER NOT NULL UNIQUE,
	"League"	INTEGER NOT NULL,
	"Round"	INTEGER NOT NULL,
	"P1"	INTEGER NOT NULL,
	"P2"	INTEGER NOT NULL,
	"Res1"	INTEGER,
	"Res2"	INTEGER,
	"Pts1"	INTEGER,
	"Pts2"	INTEGER,
	"Verified"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("M_ID"),
	FOREIGN KEY("League") REFERENCES "League"("L_ID"),
	FOREIGN KEY("P1") REFERENCES "Player"("P_ID"),
	FOREIGN KEY("P2") REFERENCES "Player"("P_ID")
)

-- Statistiken der Spieler als View
-- Achtung: NotPlayed, wenn 0 Punkte und Perfect bei 18 richtigen Antworten
CREATE VIEW Stats (P_ID, Matches, Win, Draw, Lose, NotPlayed, Correct, Perfect, Points)
AS
SELECT Players.P_ID AS P_ID, IFNULL(Matches, 0) AS Matches, IFNULL(Win, 0) AS Win, IFNULL(Draw, 0) AS Draw, IFNULL(Lose, 0) AS Lose, IFNULL(NotPlayed, 0) AS NotPlayed, IFNULL(Correct, 0) AS Correct, IFNULL(Perfect, 0) AS Perfect, IFNULL(Points, 0) AS Points
FROM (
	SELECT P_ID
	FROM Player
) AS Players
LEFT JOIN (
	SELECT P_ID, COUNT(P_ID) AS Matches, SUM(Win) AS Win, SUM(Draw) AS Draw, SUM(Lose) AS Lose, SUM(NotPlayed) AS NotPlayed, SUM(Res) AS Correct, SUM(Perfect) AS Perfect, SUM(Pts) AS Points
	FROM (
		SELECT P_ID, Res, Pts,
			CASE
				WHEN Res > Enemy THEN 1
				ELSE 0
			END AS Win,
			CASE
				WHEN Res = Enemy THEN 1
				ELSE 0
			END AS Draw,
			CASE
				WHEN Res = 0 THEN 0
				WHEN Res < Enemy THEN 1
				ELSE 0
			END AS Lose,
			CASE
				WHEN Pts = 0 THEN 1
				ELSE 0
			END AS NotPlayed,
			CASE
				WHEN Res = 18 THEN 1
				ELSE 0
			END AS Perfect
		FROM (
			SELECT P1 AS P_ID, Res1 AS Res, Res2 AS Enemy, Pts1 AS Pts
			FROM Match
			WHERE Verified = 3
			UNION ALL
			SELECT P2 AS P_ID, Res2 AS Res, Res1 AS Enemy, Pts2 AS Pts
			FROM Match
			WHERE Verified = 3)
		)
	GROUP BY P_ID
	) AS Stat
ON Players.P_ID = Stat.P_ID
ORDER BY Points DESC, Correct DESC, Win DESC, Perfect DESC, NotPlayed ASC, Matches ASC, P_ID ASC