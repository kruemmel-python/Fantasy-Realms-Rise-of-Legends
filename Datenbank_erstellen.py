import sqlite3
import random

# Verbindung zur SQLite-Datenbank herstellen
conn = sqlite3.connect('spiel.db')
cursor = conn.cursor()

# Tabelle für Gegner erstellen
cursor.execute('''
CREATE TABLE IF NOT EXISTS gegner (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    typ TEXT,
    lebenspunkte INTEGER,
    max_schaden INTEGER
)
''')

# Tabelle für Gegenstände erstellen
cursor.execute('''
CREATE TABLE IF NOT EXISTS gegenstaende (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    typ TEXT,
    wert INTEGER
)
''')

# Tabelle für Fähigkeiten erstellen
cursor.execute('''
CREATE TABLE IF NOT EXISTS faehigkeiten (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    schaden INTEGER,
    kosten INTEGER
)
''')

VORNAMEN = [
    'Aldarion', 'Erendis', 'Nimrodel', 'Amroth', 'Celepharn',
    'Eärnur', 'Glorfindel', 'Idril', 'Maedhros', 'Maglor',
    'Nerdanel', 'Oropher', 'Rúmil', 'Turgon', 'Voronwë',
    'Aegnor', 'Beleg', 'Curufin', 'Daeron', 'Ecthelion',
    'Tharanduil', 'Eowyn', 'Arwen', 'Galadriel', 'Legolas',
    'Gimli', 'Boromir', 'Faramir', 'Eomer', 'Theoden',
    'Elrond', 'Isildur', 'Anarion', 'Celeborn', 'Haldir',
    'Gandalf', 'Saruman', 'Radagast', 'Thorin', 'Balin',
    'Dwalin', 'Fili', 'Kili', 'Oin', 'Gloin',
    'Bifur', 'Bofur', 'Bombur', 'Dain', 'Thrain',
    'Thror', 'Beregond', 'Bergil', 'Hirgon', 'Ingold',
    'Irolas', 'Mablung', 'Damrod', 'Forlong', 'Ghan-buri-Ghan'
]
    
# Funktion, um einen zufälligen Namen für den Gegner zu generieren
def generiere_gegnernamen(typ):
    namen = {
        'schwach': ['Kobold', 'Goblin', 'Wicht'],
        'mittel': ['Ork', 'Troll', 'Werwolf'],
        'stark': ['Drache', 'Dämon', 'Riese']
    }
    return random.choice(namen[typ]) + ' ' + random.choice(VORNAMEN)

# Gegner mit einzigartigen Eigenschaften in die Datenbank einfügen
GEGNER_TYPEN = ['schwach', 'mittel', 'stark']
LEBENSPUNKTE = {'schwach': 50, 'mittel': 70, 'stark': 90}
MAX_SCHADEN = {'schwach': 30, 'mittel': 40, 'stark': 50}

# Gegner mit einzigartigen Eigenschaften in die Datenbank einfügen
for typ in GEGNER_TYPEN:
    for _ in range(50):  # Annahme: 10 Gegner pro Typ
        name = generiere_gegnernamen(typ)
        lebenspunkte = random.randint(LEBENSPUNKTE[typ] - 10, LEBENSPUNKTE[typ] + 10)
        max_schaden = random.randint(MAX_SCHADEN[typ] - 5, MAX_SCHADEN[typ] + 5)
        cursor.execute('INSERT INTO gegner (name, typ, lebenspunkte, max_schaden) VALUES (?, ?, ?, ?)',
                       (name, typ, lebenspunkte, max_schaden))

# Gegenstände-Daten einfügen
gegenstaende_liste = [
    ('Heiltrank', 'Heiltrank', 30),
    # Fügen Sie hier weitere Gegenstände hinzu...
]
for name, typ, wert in gegenstaende_liste:
    cursor.execute('INSERT INTO gegenstaende (name, typ, wert) VALUES (?, ?, ?)',
                   (name, typ, wert))

# Fähigkeiten-Daten einfügen
faehigkeiten_liste = [
    ('Feuerball', 50, 10),
    # Fügen Sie hier weitere Fähigkeiten hinzu...
]
for name, schaden, kosten in faehigkeiten_liste:
    cursor.execute('INSERT INTO faehigkeiten (name, schaden, kosten) VALUES (?, ?, ?)',
                   (name, schaden, kosten))

# Tabelle für Spieler erstellen
cursor.execute('''
CREATE TABLE IF NOT EXISTS spieler (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    hp INTEGER,  -- Lebenspunkte
    mp INTEGER,  -- Mana
    ex INTEGER,  -- Erfahrungspunkte
    lvl INTEGER  -- Level
)
''')



# Tabelle für Inventar erstellen
cursor.execute('''
CREATE TABLE IF NOT EXISTS inventar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    spieler_id INTEGER,
    gegenstand_id INTEGER,
    menge INTEGER,
    FOREIGN KEY (spieler_id) REFERENCES spieler(id),
    FOREIGN KEY (gegenstand_id) REFERENCES gegenstaende(id)
)
''')

# Beispiel-Daten für einen Spieler einfügen
spieler_name = 'Held'
spieler_hp = 100  # Startwert für Lebenspunkte
spieler_mp = 50   # Startwert für Mana
spieler_ex = 0    # Startwert für Erfahrungspunkte
spieler_lvl = 1   # Startlevel

cursor.execute('INSERT INTO spieler (name, hp, mp, ex, lvl) VALUES (?, ?, ?, ?, ?)',
               (spieler_name, spieler_hp, spieler_mp, spieler_ex, spieler_lvl))

# Beispiel-Daten für das Inventar einfügen
# Annahme: Die ID des Spielers ist 1 und die ID des Gegenstands 'Heiltrank' ist 1
spieler_id = 1
gegenstand_id = 1  # ID des Heiltranks
menge = 5  # Anzahl der Heiltränke im Inventar

cursor.execute('INSERT INTO inventar (spieler_id, gegenstand_id, menge) VALUES (?, ?, ?)',
               (spieler_id, gegenstand_id, menge))


# Änderungen speichern und Verbindung schließen
conn.commit()
conn.close()
