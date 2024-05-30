import sqlite3
import random

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
            gegner_multiplikator REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventar (
            spieler_name TEXT,
            gegenstand_name TEXT,
            gegenstand_typ TEXT,
            gegenstand_wert INTEGER,
            FOREIGN KEY (spieler_name) REFERENCES spieler(name)
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

# Klassen und weitere Funktionen

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

    def faehigkeit_einsetzen(self):
        if not self.faehigkeiten:
            print("Keine Fähigkeiten im Inventar.")
            return 0
        print("Wähle eine Fähigkeit aus:")
        for i, faehigkeit in enumerate(self.faehigkeiten):
            print(f"{i + 1}. {faehigkeit.name} (Schaden: {faehigkeit.schaden})")
        wahl = int(input("Nummer der Fähigkeit: ")) - 1
        if 0 <= wahl < len(self.faehigkeiten):
            faehigkeit = self.faehigkeiten[wahl]
            print(f"Du setzt {faehigkeit.name} ein und verursachst {faehigkeit.schaden} Schaden.")
            return faehigkeit.schaden
        else:
            print("Ungültige Auswahl.")
            return 0

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
            print("Wähle einen Heiltrank aus:")
            for i, heiltrank in enumerate(heiltraenke):
                print(f"{i + 1}. {heiltrank.name} (Wert: {heiltrank.wert})")
            wahl = int(input("Nummer des Heiltranks: ")) - 1
            if 0 <= wahl < len(heiltraenke):
                heiltrank = heiltraenke[wahl]
                self.heilen(heiltrank.wert)
                self.gegenstaende.remove(heiltrank)
            else:
                print("Ungültige Auswahl.")
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
                self.add_faehigkeit(faehigkeit)
                print(f"Du hast die Fähigkeit {faehigkeit_name} gefunden und deinem Inventar hinzugefügt.")
        else:
            print("Keine Fähigkeiten gefunden.")

    def add_gegenstand(self, gegenstand):
        self.gegenstaende.append(gegenstand)

    def add_faehigkeit(self, faehigkeit):
        self.faehigkeiten.append(faehigkeit)

    def nach_kampf_heilen(self):
        self.lebenspunkte = min(self.lebenspunkte + 10, self.max_lebenspunkte)
        print(f"Nach dem Kampf heilst du 10 Lebenspunkte. Lebenspunkte: {self.lebenspunkte}/{self.max_lebenspunkte}")

# Weitere Funktionen

def generiere_gegnernamen(typ):
    return f"{typ.capitalize()} Gegner {random.randint(1, 1000)}"

def erstelle_spielfeld(multiplikator):
    spielfeld = []
    for typ in GEGNER_TYPEN:
        for _ in range(ANZAHL_GEGNER_PRO_TYP):
            gegner = Gegner(typ, multiplikator)
            spielfeld.append(gegner)
    random.shuffle(spielfeld)
    return spielfeld

def spieler_speichern(spieler):
    conn = sqlite3.connect(DB_DATEI)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO spieler (name, lebenspunkte, max_lebenspunkte, erfahrung, level, gegner_multiplikator)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (spieler.name, spieler.lebenspunkte, spieler.max_lebenspunkte, spieler.level_system.erfahrung, spieler.level_system.level, spieler.gegner_multiplikator))

    cursor.execute('DELETE FROM inventar WHERE spieler_name = ?', (spieler.name,))
    for gegenstand in spieler.gegenstaende:
        cursor.execute('''
            INSERT INTO inventar (spieler_name, gegenstand_name, gegenstand_typ, gegenstand_wert)
            VALUES (?, ?, ?, ?)
        ''', (spieler.name, gegenstand.name, gegenstand.typ, gegenstand.wert))

    conn.commit()
    conn.close()

def spieler_laden(name):
    conn = sqlite3.connect(DB_DATEI)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM spieler WHERE name = ?', (name,))
    spieler_daten = cursor.fetchone()
    if not spieler_daten:
        return None

    spieler = Spieler(spieler_daten[0], spieler_daten[1], spieler_daten[2], spieler_daten[3], spieler_daten[4], [], [])
    spieler.level_system = LevelSystem(spieler_daten[3], spieler_daten[4])
    spieler.gegner_multiplikator = spieler_daten[5]

    cursor.execute('SELECT * FROM inventar WHERE spieler_name = ?', (name,))
    inventar_daten = cursor.fetchall()
    for gegenstand_daten in inventar_daten:
        gegenstand = Gegenstand(gegenstand_daten[1], gegenstand_daten[2], gegenstand_daten[3])
        spieler.gegenstaende.append(gegenstand)

    conn.close()
    return spieler

def spiel_starten():
    initialisiere_datenbank()
    name = input("Gib deinen Spielernamen ein: ")
    spieler = spieler_laden(name)

    if spieler is None:
        print(f"Spieler {name} nicht gefunden, ein neues Spiel wird gestartet.")
        spieler = Spieler(name, SPIELER_START_LEBENSPUNKTE, SPIELER_START_LEBENSPUNKTE, 0, 1, [], [])
    else:
        print(f"Willkommen zurück, {name}!")

    while True:
        print("\n1. Weitergehen\n2. Inventar anzeigen\n3. Heiltrank verwenden\n4. Gasthaus betreten\n5. Spiel speichern und beenden")
        aktion = input("Was möchtest du tun? ")

        if aktion == '1':
            gegner = random.choice(spieler.spielfeld)
            print(f"Ein {gegner.typ} Gegner erscheint!")
            while gegner.lebenspunkte > 0 and spieler.lebenspunkte > 0:
                print("\nWähle deine Aktion:")
                print("1. Angriff")
                print("2. Fähigkeit einsetzen")
                print("3. Heiltrank verwenden")
                aktion = input("Aktion: ")

                if aktion == '1':
                    schaden = spieler.angreifen()
                    gegner.lebenspunkte -= schaden
                    print(f"Du greifst den Gegner an und verursachst {schaden} Schaden. Gegner hat noch {gegner.lebenspunkte} Lebenspunkte.")
                elif aktion == '2':
                    schaden = spieler.faehigkeit_einsetzen()
                    gegner.lebenspunkte -= schaden
                    print(f"Du setzt eine Fähigkeit ein und verursachst {schaden} Schaden. Gegner hat noch {gegner.lebenspunkte} Lebenspunkte.")
                elif aktion == '3':
                    spieler.heiltrank_nutzen()
                else:
                    print("Ungültige Aktion. Du verlierst deinen Zug.")
                
                if gegner.lebenspunkte > 0:
                    schaden = gegner.angreifen()
                    spieler.lebenspunkte -= schaden
                    print(f"Der Gegner greift dich an und verursacht {schaden} Schaden. Du hast noch {spieler.lebenspunkte} Lebenspunkte.")

            if spieler.lebenspunkte <= 0:
                print("Du wurdest besiegt!")
                break
            else:
                print("Du hast den Gegner besiegt!")
                erfahrung = random.randint(10, 20)
                print(f"Du erhältst {erfahrung} Erfahrungspunkte.")
                spieler.level_system.erfahrung_sammeln(erfahrung, spieler)
                
                # Sicherstellen, dass der besiegte Gegner im Spielfeld enthalten ist
                if gegner in spieler.spielfeld:
                    spieler.spielfeld.remove(gegner)
                else:
                    print("Fehler: Gegner nicht im Spielfeld gefunden.")

                spieler.nach_kampf_heilen()
                spieler.finde_schatz()

        elif aktion == '2':
            spieler.inventar_anzeigen()

        elif aktion == '3':
            spieler.heiltrank_nutzen()

        elif aktion == '4':
            print("Du betrittst das Gasthaus und ruhst dich aus. Alle Lebenspunkte werden wiederhergestellt.")
            spieler.lebenspunkte = spieler.max_lebenspunkte

        elif aktion == '5':
            spieler_speichern(spieler)
            print("Spiel gespeichert. Bis zum nächsten Mal!")
            break

        else:
            print("Ungültige Eingabe. Bitte versuche es erneut.")

if __name__ == "__main__":
    spiel_starten()
