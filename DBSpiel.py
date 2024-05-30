import random
import sqlite3
import os

# Konstanten definieren
LEBENSPUNKTE = {'schwach': 50, 'mittel': 70, 'stark': 90}
MAX_SCHADEN = {'schwach': 30, 'mittel': 40, 'stark': 50}
HEILTRANK_WERTE = {'Kleiner Heiltrank': 30, 'Mittlerer Heiltrank': 60, 'Großer Heiltrank': 100}
SPIELFELD_GROESSE = 1000
GEGNER_TYPEN = ['schwach', 'mittel', 'stark']
ANZAHL_GEGNER_PRO_TYP = 50
SPIELER_START_LEBENSPUNKTE = 400
SPIELER_MAX_SCHADEN = 35
DB_DATEI = 'spielerdaten.db'

# Datenbankverbindung herstellen und Tabellen erstellen
def initialisiere_datenbank():
    conn = sqlite3.connect(DB_DATEI)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS spieler (
            name TEXT PRIMARY KEY,
            lebenspunkte INTEGER,
            max_lebenspunkte INTEGER,
            erfahrung INTEGER,
            level INTEGER,
            gegenstaende TEXT,
            faehigkeiten TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gegner (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            typ TEXT,
            lebenspunkte INTEGER,
            max_schaden INTEGER,
            name TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS heiltraenke (
            name TEXT PRIMARY KEY,
            wert INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS faehigkeiten (
            name TEXT PRIMARY KEY,
            schaden INTEGER
        )
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO heiltraenke (name, wert) VALUES
        ('Kleiner Heiltrank', 30),
        ('Mittlerer Heiltrank', 60),
        ('Großer Heiltrank', 100)
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO faehigkeiten (name, schaden) VALUES
        ('kleiner Feuerball', 50),
        ('kleines Eismesser', 50),
        ('kleiner Blitzschlag', 50),
        ('mittlerer Feuerball', 80),
        ('mittleres Eismesser', 80),
        ('mittlerer Blitzschlag', 80)
    ''')
    conn.commit()
    conn.close()

class Gegenstand:
    def __init__(self, name, typ, wert):
        self.name = name
        self.typ = typ
        self.wert = wert

class Faehigkeit:
    def __init__(self, name, schaden):
        self.name = name
        self.schaden = schaden

class LevelSystem:
    def __init__(self, erfahrung, level=1):
        self.erfahrung = erfahrung
        self.level = level

    def erfahrung_sammeln(self, punkte, spieler):
        self.erfahrung += punkte
        if self.erfahrung >= self.level * 100:
            self.level_up(spieler)

    def level_up(self, spieler):
        self.level += 1
        spieler.max_lebenspunkte += 10
        spieler.lebenspunkte = spieler.max_lebenspunkte
        print(f"Glückwunsch! Du hast Level {self.level} erreicht! Deine maximalen Lebenspunkte wurden um 10 erhöht und sind jetzt {spieler.max_lebenspunkte}.")
        spieler.gegner_multiplikator *= 1.05
        spieler.spielfeld = erstelle_spielfeld(spieler.gegner_multiplikator)

class Gegner:
    def __init__(self, typ, multiplikator=1.0):
        self.typ = typ
        self.lebenspunkte = int(LEBENSPUNKTE[typ] * multiplikator)
        self.max_schaden = int(MAX_SCHADEN[typ] * multiplikator)
        self.name = generiere_gegnernamen(typ)

    def angreifen(self):
        return random.randint(1, self.max_schaden)

class Spieler:
    def __init__(self, name, lebenspunkte, max_lebenspunkte, erfahrung, level, gegenstaende, faehigkeiten):
        self.name = name
        self.lebenspunkte = lebenspunkte
        self.max_lebenspunkte = max_lebenspunkte
        self.level_system = LevelSystem(erfahrung, level)
        self.gegenstaende = gegenstaende
        self.faehigkeiten = faehigkeiten
        self.gegner_multiplikator = 1.0
        self.spielfeld = erstelle_spielfeld(self.gegner_multiplikator)

    def inventar_anzeigen(self):
        if not self.gegenstaende:
            print("Dein Inventar ist leer.")
        else:
            print("Du hast folgende Gegenstände in deinem Inventar:")
            for gegenstand in self.gegenstaende:
                print(f"{gegenstand.name} - Typ: {gegenstand.typ}, Wert: {gegenstand.wert}")

        if not self.faehigkeiten:
            print("Du hast keine Fähigkeiten im Inventar.")
        else:
            print("Du hast folgende Fähigkeiten im Inventar:")
            for faehigkeit in self.faehigkeiten:
                print(f"{faehigkeit.name}")

    def angreifen(self):
        return random.randint(1, SPIELER_MAX_SCHADEN)

    def heilen(self, wert=30):
        self.lebenspunkte = min(self.lebenspunkte + wert, self.max_lebenspunkte)
        print(f"Du wurdest um {wert} Lebenspunkte geheilt. Lebenspunkte: {self.lebenspunkte}/{self.max_lebenspunkte}")

    def gegenstand_verwenden(self, gegenstand_name):
        gegenstand = next((g for g in self.gegenstaende if g.name == gegenstand_name), None)
        if gegenstand:
            if gegenstand.typ == 'Heiltrank':
                self.heilen(gegenstand.wert)
                self.gegenstaende.remove(gegenstand)
            else:
                print(f"Der Gegenstand {gegenstand.name} kann nicht verwendet werden.")
        else:
            print(f"Der Gegenstand {gegenstand_name} ist nicht in deinem Inventar.")

    def heiltrank_nutzen(self):
        heiltraenke = [g for g in self.gegenstaende if g.typ == 'Heiltrank']
        if heiltraenke:
            antwort = input("Möchtest du einen Heiltrank verwenden? (j/n): ")
            if antwort.lower() == 'j':
                self.heilen(heiltraenke[0].wert)
                self.gegenstaende.remove(heiltraenke[0])
            else:
                print("Heiltrank nicht verwendet.")
        else:
            print("Keine Heiltränke im Inventar.")

    def finde_heiltraenke(self):
        conn = sqlite3.connect(DB_DATEI)
        cursor = conn.cursor()
        cursor.execute('''SELECT name, wert FROM heiltraenke''')
        heiltraenke_liste = cursor.fetchall()
        conn.close()

        anzahl_gefundene_heiltraenke = random.randint(0, 2)
        if anzahl_gefundene_heiltraenke > 0:
            for _ in range(anzahl_gefundene_heiltraenke):
                heiltrank_name, heiltrank_wert = random.choice(heiltraenke_liste)
                heiltrank = Gegenstand(heiltrank_name, 'Heiltrank', heiltrank_wert)
                self.add_gegenstand(heiltrank)
                print(f"Du hast einen {heiltrank_name} gefunden und deinem Inventar hinzugefügt.")
        else:
            print("Keine Heiltränke gefunden.")

    def finde_schatz(self):
        self.finde_heiltraenke()
        self.finde_faehigkeiten()

    def finde_faehigkeiten(self):
        conn = sqlite3.connect(DB_DATEI)
        cursor = conn.cursor()
        cursor.execute('SELECT name, schaden FROM faehigkeiten')
        faehigkeiten_liste = cursor.fetchall()
        conn.close()

        anzahl_gefundene_faehigkeiten = random.randint(0, 1)
        if anzahl_gefundene_faehigkeiten > 0:
            for _ in range(anzahl_gefundene_faehigkeiten):
                faehigkeit_name, faehigkeit_schaden = random.choice(faehigkeiten_liste)
                faehigkeit = Faehigkeit(faehigkeit_name, faehigkeit_schaden)
                self.faehigkeiten.append(faehigkeit)
                print(f"Du hast die Fähigkeit {faehigkeit_name} gefunden und deinem Inventar hinzugefügt.")
        else:
            print("Keine Fähigkeiten gefunden.")

    def add_gegenstand(self, gegenstand):
        self.gegenstaende.append(gegenstand)

def generiere_gegnernamen(typ):
    if typ == 'schwach':
        return f"Schwacher Gegner #{random.randint(1, 100)}"
    elif typ == 'mittel':
        return f"Mittelstarker Gegner #{random.randint(1, 100)}"
    elif typ == 'stark':
        return f"Starker Gegner #{random.randint(1, 100)}"

def erstelle_spielfeld(gegner_multiplikator):
    spielfeld = []
    for gegner_typ in GEGNER_TYPEN:
        for _ in range(ANZAHL_GEGNER_PRO_TYP):
            gegner = Gegner(gegner_typ, gegner_multiplikator)
            spielfeld.append(gegner)
    random.shuffle(spielfeld)
    return spielfeld

def spieler_speichern(spieler):
    conn = sqlite3.connect(DB_DATEI)
    cursor = conn.cursor()
    gegenstaende = ','.join([f"{g.name}:{g.typ}:{g.wert}" for g in spieler.gegenstaende])
    faehigkeiten = ','.join([f.name for f in spieler.faehigkeiten])
    cursor.execute('''
        INSERT OR REPLACE INTO spieler (name, lebenspunkte, max_lebenspunkte, erfahrung, level, gegenstaende, faehigkeiten)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (spieler.name, spieler.lebenspunkte, spieler.max_lebenspunkte, spieler.level_system.erfahrung, 
          spieler.level_system.level, gegenstaende, faehigkeiten))
    conn.commit()
    conn.close()

def spieler_laden(name):
    conn = sqlite3.connect(DB_DATEI)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM spieler WHERE name = ?', (name,))
    row = cursor.fetchone()
    conn.close()
    if row:
        # Trennzeichen von Komma zu Semikolon ändern
        gegenstaende_strings = row[5].split(';') if row[5] else []
        gegenstaende = []
        for g in gegenstaende_strings:
            teile = g.split(':')
            if len(teile) == 3:
                gegenstaende = [Gegenstand(*g.split(':')) for g in row[5].split(',')] if row[5] else []
                gegenstaende.append(gegenstaende)
            else:
                print(f"Fehlerhafter Gegenstand: {g}")
        faehigkeiten = row[6].split(',') if row[6] else []
        return Spieler(row[0], row[1], row[2], row[3], row[4], gegenstaende, faehigkeiten)
    else:
        return None




def gasthaus(spieler):
    while True:
        print("\n--- Gasthaus ---")
        print("1. Spielerinformationen anzeigen")
        print("2. Inventar anzeigen")
        print("3. Fähigkeiten anzeigen")
        print("4. Gasthaus verlassen")

        wahl = input("Was möchtest du tun? ")

        if wahl == '1':
            print(f"Spielername: {spieler.name}")
            print(f"Lebenspunkte: {spieler.lebenspunkte}/{spieler.max_lebenspunkte}")
            print(f"Erfahrung: {spieler.level_system.erfahrung}")
            print(f"Level: {spieler.level_system.level}")
        elif wahl == '2':
            spieler.inventar_anzeigen()
        elif wahl == '3':
            if not spieler.faehigkeiten:
                print("Du hast keine Fähigkeiten.")
            else:
                print("Du hast folgende Fähigkeiten:")
                for faehigkeit in spieler.faehigkeiten:
                    print(f"{faehigkeit.name} - Schaden: {faehigkeit.schaden}")
        elif wahl == '4':
            print("Du verlässt das Gasthaus.")
            break
        else:
            print("Ungültige Auswahl. Bitte versuche es erneut.")

# Hauptspielschleife
def spiel_starten():
    initialisiere_datenbank()

    name = input("Gib deinen Spielernamen ein: ")
    spieler = spieler_laden(name)
    if not spieler:
        spieler = Spieler(name, SPIELER_START_LEBENSPUNKTE, SPIELER_START_LEBENSPUNKTE, 0, 1, [], [])

    print(f"Willkommen, {spieler.name}!")

    while True:
        print("\n1. Weitergehen")
        print("2. Inventar anzeigen")
        print("3. Heiltrank verwenden")
        print("4. Gasthaus betreten")
        print("5. Spiel speichern und beenden")

        wahl = input("Was möchtest du tun? ")

        if wahl == '1':
            if not spieler.spielfeld:
                print("Das Spielfeld ist leer. Du hast alle Gegner besiegt!")
                break
            gegner = spieler.spielfeld.pop(0)
            print(f"Ein {gegner.typ}er Gegner mit {gegner.lebenspunkte} Lebenspunkten erscheint.")

            while gegner.lebenspunkte > 0 and spieler.lebenspunkte > 0:
                while True:
                    aktion = input("Was möchtest du tun? (angreifen/heilen/inventar/faehigkeit/gasthaus): ").lower()
                    if aktion in ["angreifen", "heilen", "inventar", "faehigkeit", "gasthaus"]:
                        break
                    else:
                        print("Ungültige Aktion. Bitte wählen Sie eine der angegebenen Aktionen.")

                if aktion == "angreifen":
                    schaden = spieler.angreifen()
                    gegner.lebenspunkte -= schaden
                    print(f"Du hast {schaden} Schaden verursacht. Gegner Lebenspunkte: {gegner.lebenspunkte}")
                elif aktion == "heilen":
                    spieler.heilen()
                elif aktion == "inventar":
                    spieler.inventar_anzeigen()
                    gegenstand_name = input("Welchen Gegenstand möchtest du verwenden? (Name eingeben oder leer lassen): ")
                    if gegenstand_name:
                        spieler.gegenstand_verwenden(gegenstand_name)
                elif aktion == "faehigkeit":
                    for i, faehigkeit in enumerate(spieler.faehigkeiten):
                        print(f"{i + 1}: {faehigkeit.name} (Schaden: {faehigkeit.schaden})")
                    faehigkeit_index = int(input("Welche Fähigkeit möchtest du einsetzen? (Nummer eingeben): ")) - 1
                    if 0 <= faehigkeit_index < len(spieler.faehigkeiten):
                        faehigkeit = spieler.faehigkeiten[faehigkeit_index]
                        gegner.lebenspunkte -= faehigkeit.schaden
                        print(f"Du hast {faehigkeit.schaden} Schaden mit {faehigkeit.name} verursacht. Gegner Lebenspunkte: {gegner.lebenspunkte}")
                    else:
                        print("Ungültige Auswahl. Bitte wählen Sie eine gültige Nummer.")
                elif aktion == "gasthaus":
                    gasthaus(spieler)
                    continue

                if gegner.lebenspunkte > 0:
                    gegner_schaden = gegner.angreifen()
                    spieler.lebenspunkte -= gegner_schaden
                    print(f"Der Gegner greift an und verursacht {gegner_schaden} Schaden. Deine Lebenspunkte: {spieler.lebenspunkte}")

            if spieler.lebenspunkte <= 0:
                print("Du bist gestorben. Spiel vorbei.")
                break

            print(f"Du hast den {gegner.typ}en Gegner besiegt!")
            spieler.finde_heiltraenke()
            erfahrungspunkte = 10 * (GEGNER_TYPEN.index(gegner.typ) + 1)
            spieler.level_system.erfahrung_sammeln(erfahrungspunkte, spieler)  # Hier den spieler übergeben
            spieler_speichern(spieler)
        elif wahl == '2':
            spieler.inventar_anzeigen()
        elif wahl == '3':
            spieler.heiltrank_nutzen()
        elif wahl == '4':
            gasthaus(spieler)
        elif wahl == '5':
            spieler_speichern(spieler)
            print("Spiel gespeichert. Bis zum nächsten Mal!")
            break
        else:
            print("Ungültige Auswahl. Bitte versuche es erneut.")


spiel_starten()
