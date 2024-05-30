import sqlite3
import random

# Konstanten definieren
HEILTRANK_WERTE = {'Kleiner Heiltrank': 30, 'Mittlerer Heiltrank': 60, 'Großer Heiltrank': 100}
SPIELER_START_LEBENSPUNKTE = 400
SPIELER_MAX_SCHADEN = 35
DB_DATEI = 'spielerdaten.db'
SPIELFELD_GROESSE = 1000
ANZAHL_GEGNER = 900

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
            name TEXT,
            lebenspunkte INTEGER,
            max_schaden INTEGER
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

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crafting_items (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            effect TEXT NOT NULL
        )
    ''')

    # Initiale Handwerksitems in die Tabelle einfügen
    crafting_items = [
        (1, "Magisches Kraut", "Kraut", "Heilung"),
        (2, "Eisenerz", "Erz", "Stärke"),
        (3, "Drachenschuppe", "Schuppe", "Verteidigung")
    ]

    cursor.executemany('''
        INSERT OR IGNORE INTO crafting_items (id, name, type, effect) VALUES (?, ?, ?, ?)
    ''', crafting_items)

    conn.commit()
    conn.close()

def gegner_generieren():
    gegner_daten = [
        ('Wilder Bär', 'Tier', 'mittel', 70, 20),
        ('Werwolf', 'Tier', 'stark', 90, 30),
        ('Troll', 'Humanoid', 'mittel', 80, 25),
        ('Todesritter', 'Untoter', 'stark', 100, 35),
        ('Todesgolem', 'Golem', 'stark', 110, 40),
        ('Sturmhexe', 'Magisch', 'mittel', 60, 50)
    ]

    conn = sqlite3.connect(DB_DATEI)
    cursor = conn.cursor()

    for name, typ, staerke, lebenspunkte, max_schaden in gegner_daten:
        for _ in range(ANZAHL_GEGNER // len(gegner_daten)):
            cursor.execute('''
                INSERT INTO gegner (typ, name, lebenspunkte, max_schaden) VALUES (?, ?, ?, ?)
            ''', (typ, name, lebenspunkte, max_schaden))

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

class Handwerksgegenstand:
    def __init__(self, name, typ, effekt):
        self.name = name
        self.typ = typ
        self.effekt = effekt

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
    def __init__(self, id):
        self.id = id
        conn = sqlite3.connect(DB_DATEI)
        cursor = conn.cursor()
        cursor.execute('SELECT typ, name, lebenspunkte, max_schaden FROM gegner WHERE id = ?', (id,))
        gegner_daten = cursor.fetchone()
        conn.close()
        if gegner_daten:
            self.typ, self.name, self.lebenspunkte, self.max_schaden = gegner_daten
        else:
            raise ValueError(f"Gegner mit ID {id} nicht in der Datenbank gefunden.")
    def angreifen(self):
        return random.randint(1, self.max_schaden)
    
    def drop_item(self):
        items = ["Magisches Kraut", "Eisenerz", "Drachenschuppe"]
        return random.choice(items)

def lade_gegner(id):
    conn = sqlite3.connect(DB_DATEI)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM gegner WHERE id = ?', (id,))
    gegner_id = cursor.fetchone()
    conn.close()
    if gegner_id:
        return Gegner(gegner_id[0])
    else:
        return None

class Spieler:
    def __init__(self, name, lebenspunkte, max_lebenspunkte, erfahrung, level, gegenstaende, faehigkeiten, handwerksgegenstaende, gegner_multiplikator):
        self.name = name
        self.lebenspunkte = lebenspunkte
        self.max_lebenspunkte = max_lebenspunkte
        self.level_system = LevelSystem(erfahrung, level)
        self.gegenstaende = gegenstaende
        self.faehigkeiten = faehigkeiten
        self.handwerksgegenstaende = handwerksgegenstaende
        self.gegner_multiplikator = gegner_multiplikator
        self.spielfeld = erstelle_spielfeld(self.gegner_multiplikator)
        self.position = 0

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

        if not self.handwerksgegenstaende:
            print("Du hast keine Handwerksgegenstände im Inventar.")
        else:
            print("Du hast folgende Handwerksgegenstände im Inventar:")
            for gegenstand in self.handwerksgegenstaende:
                print(f"{gegenstand.name} - Typ: {gegenstand.typ}, Effekt: {gegenstand.effekt}")

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
        self.finde_handwerksgegenstaende()

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

    def finde_handwerksgegenstaende(self):
        conn = sqlite3.connect(DB_DATEI)
        cursor = conn.cursor()
        cursor.execute('SELECT name, type, effect FROM crafting_items')
        crafting_items_list = cursor.fetchall()
        conn.close()

        anzahl_gefundene_items = random.randint(0, 2)
        if anzahl_gefundene_items > 0:
            for _ in range(anzahl_gefundene_items):
                item_name, item_type, item_effect = random.choice(crafting_items_list)
                item = Handwerksgegenstand(item_name, item_type, item_effect)
                self.add_handwerksgegenstand(item)
                print(f"Du hast einen {item_name} gefunden und deinem Inventar hinzugefügt.")
        else:
            print("Keine Handwerksgegenstände gefunden.")

    def add_gegenstand(self, gegenstand):
        self.gegenstaende.append(gegenstand)

    def add_faehigkeit(self, faehigkeit):
        self.faehigkeiten.append(faehigkeit)

    def add_handwerksgegenstand(self, gegenstand):
        self.handwerksgegenstaende.append(gegenstand)

    def nach_kampf_heilen(self):
        self.lebenspunkte = min(self.lebenspunkte + 10, self.max_lebenspunkte)
        print(f"Nach dem Kampf heilst du 10 Lebenspunkte. Lebenspunkte: {self.lebenspunkte}/{self.max_lebenspunkte}")

    def handwerken(self):
        if not self.handwerksgegenstaende:
            print("Keine Handwerksgegenstände im Inventar.")
            return
        
        print("Wähle zwei Handwerksgegenstände zum Kombinieren:")
        for i, gegenstand in enumerate(self.handwerksgegenstaende):
            print(f"{i + 1}. {gegenstand.name} (Typ: {gegenstand.typ}, Effekt: {gegenstand.effekt})")
        
        wahl1 = int(input("Nummer des ersten Gegenstands: ")) - 1
        wahl2 = int(input("Nummer des zweiten Gegenstands: ")) - 1
        
        if 0 <= wahl1 < len(self.handwerksgegenstaende) and 0 <= wahl2 < len(self.handwerksgegenstaende):
            gegenstand1 = self.handwerksgegenstaende[wahl1]
            gegenstand2 = self.handwerksgegenstaende[wahl2]
            neue_faehigkeit = self.kombiniere_handwerksgegenstaende(gegenstand1, gegenstand2)
            self.add_faehigkeit(neue_faehigkeit)
            self.handwerksgegenstaende.remove(gegenstand1)
            self.handwerksgegenstaende.remove(gegenstand2)
            print(f"Du hast eine neue Fähigkeit {neue_faehigkeit.name} erstellt!")
        else:
            print("Ungültige Auswahl.")
    
    def kombiniere_handwerksgegenstaende(self, gegenstand1, gegenstand2):
        name = f"{gegenstand1.name}-{gegenstand2.name} Fähigkeit"
        schaden = random.randint(20, 100)
        return Faehigkeit(name, schaden)

# Weitere Funktionen

def generiere_gegnernamen(typ):
    return f"{typ.capitalize()} Gegner {random.randint(1, 1000)}"

def erstelle_spielfeld(multiplikator):
    spielfeld = [None] * SPIELFELD_GROESSE
    conn = sqlite3.connect(DB_DATEI)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM gegner')
    gegner_ids = cursor.fetchall()
    conn.close()

    if gegner_ids:
        gegner_ids = [id[0] for id in gegner_ids]
        zufaellige_gegner = random.sample(gegner_ids, min(ANZAHL_GEGNER, len(gegner_ids)))
        for gegner_id in zufaellige_gegner:
            position = random.randint(1, SPIELFELD_GROESSE - 1)
            while spielfeld[position] is not None:
                position = random.randint(1, SPIELFELD_GROESSE - 1)
            spielfeld[position] = gegner_id
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

    spieler = Spieler(spieler_daten[0], spieler_daten[1], spieler_daten[2], spieler_daten[3], spieler_daten[4], [], [], [], spieler_daten[5])
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
    gegner_generieren()
    name = input("Gib deinen Spielernamen ein: ")
    spieler = spieler_laden(name)

    if spieler is None:
        print(f"Spieler {name} nicht gefunden, ein neues Spiel wird gestartet.")
        spieler = Spieler(name, SPIELER_START_LEBENSPUNKTE, SPIELER_START_LEBENSPUNKTE, 0, 1, [], [], [], 1.0)
        spieler_speichern(spieler)
    else:
        print(f"Willkommen zurück, {name}!")

    while True:
        print("\n1. Weitergehen\n2. Inventar anzeigen\n3. Heiltrank verwenden\n4. Gasthaus betreten\n5. Handwerk\n6. Spiel speichern und beenden")
        aktion = input("Was möchtest du tun? ")

        if aktion == '1':
            wuerfel = random.randint(1, 6)
            neue_position = spieler.position + wuerfel

            if neue_position >= SPIELFELD_GROESSE:
                print("Du hast das Ende des Spielfelds erreicht.")
                continue

            spieler.position = neue_position
            gegner_id = spieler.spielfeld[spieler.position]

            if gegner_id is None:
                print(f"Du gehst {wuerfel} Felder weiter und landest auf einem leeren Feld.")
            else:
                gegner = lade_gegner(gegner_id)
                if gegner:
                    print(f"Ein {gegner.typ} namens {gegner.name} erscheint!")
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
                        elif gegner.lebenspunkte <= 0:
                            print("Du hast den Gegner besiegt!")
                            erfahrung = random.randint(10, 20)
                            print(f"Du erhältst {erfahrung} Erfahrungspunkte.")
                            spieler.level_system.erfahrung_sammeln(erfahrung, spieler)
                            
                            # Sicherstellen, dass der besiegte Gegner im Spielfeld entfernt wird
                            spieler.spielfeld[spieler.position] = None
                            
                            spieler.nach_kampf_heilen()
                            spieler.finde_schatz()
                            
                            # Gegner droppt Handwerksgegenstände
                            drop = gegner.drop_item()
                            print(f"Der Gegner hat {drop} fallen gelassen.")
                            conn = sqlite3.connect(DB_DATEI)
                            cursor = conn.cursor()
                            cursor.execute('SELECT name, type, effect FROM crafting_items WHERE name = ?', (drop,))
                            item_data = cursor.fetchone()
                            conn.close()
                            if item_data:
                                item = Handwerksgegenstand(item_data[0], item_data[1], item_data[2])
                                spieler.add_handwerksgegenstand(item)

        elif aktion == '2':
            spieler.inventar_anzeigen()

        elif aktion == '3':
            spieler.heiltrank_nutzen()

        elif aktion == '4':
            print("Du betrittst das Gasthaus und ruhst dich aus. Alle Lebenspunkte werden wiederhergestellt.")
            spieler.lebenspunkte = spieler.max_lebenspunkte

        elif aktion == '5':
            spieler.handwerken()

        elif aktion == '6':
            spieler_speichern(spieler)
            print("Spiel gespeichert. Bis zum nächsten Mal!")
            break

        else:
            print("Ungültige Eingabe. Bitte versuche es erneut.")

if __name__ == "__main__":
    spiel_starten()
