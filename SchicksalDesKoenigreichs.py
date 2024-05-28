import random
import csv
import os

# Konstanten definieren
LEBENSPUNKTE = {'schwach': 50, 'mittel': 70, 'stark': 90}
MAX_SCHADEN = {'schwach': 30, 'mittel': 40, 'stark': 50}
SPIELFELD_GROESSE = 1000
GEGNER_TYPEN = ['schwach', 'mittel', 'stark']
ANZAHL_GEGNER_PRO_TYP = 50
SPIELER_START_LEBENSPUNKTE = 100
SPIELER_MAX_SCHADEN = 35
CSV_DATEI = 'spielerdaten.csv'

# Beispiel für die Implementierung von Gegenständen
class Gegenstand:
    def __init__(self, name, typ, wert):
        self.name = name
        self.typ = typ
        self.wert = wert

# Beispiel für die Implementierung von Fähigkeiten
class Faehigkeit:
    def __init__(self, name, schaden, kosten):
        self.name = name
        self.schaden = schaden
        self.kosten = kosten  # Kosten könnten Energiepunkte oder ähnliches sein

# Beispiel für die Implementierung eines Level-Systems
class LevelSystem:
    def __init__(self, erfahrung, level=1):
        self.erfahrung = erfahrung
        self.level = level

    def erfahrung_sammeln(self, punkte, spieler):
        self.erfahrung += punkte
        if self.erfahrung >= self.level * 100:  # Annahme: 100 XP pro Level
            self.level_up(spieler)

    def level_up(self, spieler):
        self.level += 1
        spieler.max_lebenspunkte += 10  # Erhöhe die maximalen Lebenspunkte des Spielers um 10 bei jedem Levelaufstieg
        spieler.lebenspunkte = spieler.max_lebenspunkte  # Fülle die Lebenspunkte auf das Maximum auf
        print(f"Glückwunsch! Du hast Level {self.level} erreicht! Deine maximalen Lebenspunkte wurden um 10 erhöht und sind jetzt {spieler.max_lebenspunkte}.")
        # Erhöhe die Attribute der Gegner um 15% jedesmal wenn der spieler 1 Level aufsteigt.
        spieler.gegner_multiplikator *= 1.15  # Skaliere den Multiplikator um 15%
        spieler.spielfeld = erstelle_spielfeld(spieler.gegner_multiplikator)  # Aktualisiere das Spielfeld mit stärkeren Gegnern

# Definiere die Klassen für die Gegner
class Gegner:
    def __init__(self, typ, multiplikator=1.0):
        self.typ = typ
        self.lebenspunkte = int(LEBENSPUNKTE[typ] * multiplikator)
        self.max_schaden = int(MAX_SCHADEN[typ] * multiplikator)
        self.name = generiere_gegnernamen(typ)  # Generiere und speichere den Namen des Gegners

    def angreifen(self):
        return random.randint(1, self.max_schaden)

# Definiere die Klasse für den Spieler
class Spieler:
    def __init__(self, name, lebenspunkte, max_lebenspunkte, erfahrung, level, gegenstaende, faehigkeiten):
        # Initialisiere den Spieler mit Startlebenspunkten
        self.name = name
        self.lebenspunkte = lebenspunkte
        self.max_lebenspunkte = max_lebenspunkte
        self.level_system = LevelSystem(erfahrung, level)  # Füge das Level-System hinzu
        self.gegenstaende = gegenstaende  # Liste der Gegenstände des Spielers
        self.faehigkeiten = faehigkeiten  # Liste der Fähigkeiten des Spielers
        self.gegner_multiplikator = 1.0  # Startmultiplikator für die Gegner
        self.spielfeld = erstelle_spielfeld(self.gegner_multiplikator)  # Erstelle das Spielfeld mit Gegnern

    def angreifen(self):
        # Spieler führt einen Angriff aus und gibt zufälligen Schaden zurück
        return random.randint(1, SPIELER_MAX_SCHADEN)

    def heilen(self):
         # Erhöhe die Lebenspunkte des Spielers um 20, aber nicht über das Maximum
        self.lebenspunkte = min(self.lebenspunkte + 20, self.max_lebenspunkte)
        print(f"Als Siegesbonus wurden die Lebenspunkte des Spielers um 20 erhöht und sind jetzt {self.lebenspunkte}/{self.max_lebenspunkte}.")
        
    def add_gegenstand(self, gegenstand):
        self.gegenstaende.append(gegenstand)
        print(f"{gegenstand.name} wurde dem Inventar hinzugefügt.")

    def add_faehigkeit(self, faehigkeit):
        self.faehigkeiten.append(faehigkeit)
        print(f"Fähigkeit {faehigkeit.name} wurde erlernt.")

    def erfahrung_sammeln(self, punkte):
        self.level_system.erfahrung_sammeln(punkte, self)

# Funktionen zum Speichern und Laden von Spielerdaten
def speichere_spielerdaten(spieler):
    daten = [spieler.name, spieler.lebenspunkte, spieler.max_lebenspunkte,
             spieler.level_system.erfahrung, spieler.level_system.level,
             ';'.join([gegenstand.name for gegenstand in spieler.gegenstaende]),
             ';'.join([faehigkeit.name for faehigkeit in spieler.faehigkeiten])]

    vorhandene_daten = []

    if os.path.exists(CSV_DATEI):
        with open(CSV_DATEI, 'r', newline='') as file:
            reader = csv.reader(file)
            vorhandene_daten = list(reader)

    mit_kopfzeile = False

    if len(vorhandene_daten) == 0 or vorhandene_daten[0] != ['Name', 'Lebenspunkte', 'MaxLebenspunkte', 'Erfahrung', 'Level', 'Gegenstaende', 'Faehigkeiten']:
        mit_kopfzeile = True

    spieler_gefunden = False
    for i, zeile in enumerate(vorhandene_daten):
        if zeile[0] == spieler.name:
            vorhandene_daten[i] = daten
            spieler_gefunden = True
            break

    if not spieler_gefunden:
        vorhandene_daten.append(daten)

    with open(CSV_DATEI, 'w', newline='') as file:
        writer = csv.writer(file)
        if mit_kopfzeile:
            writer.writerow(['Name', 'Lebenspunkte', 'MaxLebenspunkte', 'Erfahrung', 'Level', 'Gegenstaende', 'Faehigkeiten'])
        writer.writerows(vorhandene_daten)

def lade_spielerdaten(name):
    if not os.path.exists(CSV_DATEI):
        return None

    with open(CSV_DATEI, 'r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Name'] == name:
                max_lebenspunkte = int(row['MaxLebenspunkte'])
                lebenspunkte = max_lebenspunkte  # Setze die Lebenspunkte auf die maximalen Lebenspunkte
                erfahrung = int(row['Erfahrung'])
                level = int(row['Level'])
                gegenstaende = [Gegenstand(name, '', 0) for name in row['Gegenstaende'].split(';') if name]
                faehigkeiten = [Faehigkeit(name, 0, 0) for name in row['Faehigkeiten'].split(';') if name]
                return Spieler(name, lebenspunkte, max_lebenspunkte, erfahrung, level, gegenstaende, faehigkeiten)
    return None

# Erstelle das Spielfeld und verteile die Gegner zufällig
def erstelle_spielfeld(multiplikator=1.0):
    spielfeld = [None] * SPIELFELD_GROESSE
    verfuegbare_positionen = list(range(SPIELFELD_GROESSE))

    for typ in GEGNER_TYPEN:
        for _ in range(ANZAHL_GEGNER_PRO_TYP):
            # Wähle eine zufällige Position für den Gegner und entferne sie aus der Liste
            position = random.choice(verfuegbare_positionen)
            verfuegbare_positionen.remove(position)
            spielfeld[position] = Gegner(typ, multiplikator)
    return spielfeld
# Funktion, um einen Namen für den Gegner basierend auf seiner Stärke zu generieren
def generiere_gegnernamen(typ):
    namen = {
        'schwach': ['Kobold', 'Goblin', 'Wicht'],
        'mittel': ['Ork', 'Troll', 'Werwolf'],
        'stark': ['Drache', 'Dämon', 'Riese']
    }
    return random.choice(namen[typ])

# Funktion, um die Kampfeinleitung zu erzählen
def kampfeinleitung(gegner):
    einleitungen = {
        'schwach': f"Achtung! Du bist auf einen {gegner.name} gestoßen. Bereite dich auf einen Kampf vor!",
        'mittel': f"Vorsicht! Ein wilder {gegner.name} kreuzt deinen Weg. Zeige ihm deine Stärke!",
        'stark': f"Ein mächtiger {gegner.name} erscheint! Dies wird eine wahre Herausforderung!"
    }
    print(einleitungen[gegner.typ])

# Definiere die Funktion für den Kampf
def kampf(spieler, gegner):
    kampfeinleitung(gegner)  # Erzähle die Kampfeinleitung
    while spieler.lebenspunkte > 0 and gegner.lebenspunkte > 0:
        schaden = spieler.angreifen()
        gegner.lebenspunkte -= schaden
        if gegner.lebenspunkte <= 0:
            print(f"{schaden} Schaden verursacht, {gegner.name} wurde besiegt!")
            spieler.erfahrung_sammeln(50)
            spieler.heilen()
            speichere_spielerdaten(spieler)
            return
        else:
            print(f"Der Spieler verursacht {schaden} Schaden. {gegner.name} hat noch {gegner.lebenspunkte} Lebenspunkte.")
        
        gegner_schaden = gegner.angreifen()
        spieler.lebenspunkte -= gegner_schaden
        if spieler.lebenspunkte <= 0:
            print(f"{gegner.name} verursacht {gegner_schaden} Schaden. Der Spieler wurde besiegt.")
            break
        else:
            print(f"{gegner.name} verursacht {gegner_schaden} Schaden. Spieler hat noch {spieler.lebenspunkte} Lebenspunkte.")

def erzaehle_geschichte():
    geschichte = """
    Herz der Mutigen: Das Schicksal des Königreichs
    In einer Welt, die von dunklen Mächten heimgesucht wird, liegt das Schicksal aller Lebewesen in den Händen eines mutigen Abenteurers - dir. 
    Vor langer Zeit wurde das Land in Stücke gerissen und von furchterregenden Kreaturen überrannt, die aus den Tiefen der Unterwelt kamen. 
    Die Legende besagt, dass nur derjenige, der das sagenumwobene Artefakt 'Herz der Mutigen' findet und die vier Elementwächter besiegt, 
    das Land vereinen und den Frieden wiederherstellen kann. Dieses Artefakt verleiht seinem Besitzer unvorstellbare Macht und die Fähigkeit, 
    die Dunkelheit zu vertreiben. Doch der Weg ist gefährlich und nur die Tapfersten wagen es, ihn zu beschreiten.

    Dein Abenteuer beginnt in den Ruinen des alten Königreichs, wo die ersten Hinweise auf das Artefakt versteckt sind. 
    Mit jedem Gegner, den du besiegst, und jedem Rätsel, das du löst, kommst du dem Ziel näher. Aber sei gewarnt: 
    Die Elementwächter werden nicht kampflos aufgeben. Sie werden alles in ihrer Macht Stehende tun, um dich aufzuhalten.

    Am Ende des Weges, wenn du alle Prüfungen bestanden und die Wächter besiegt hast, wartet das 'Herz der Mutigen' auf dich. 
    Mit ihm kannst du die Welt retten und als Held in die Geschichte eingehen. Bist du bereit, dein Schicksal anzunehmen und das größte Abenteuer deines Lebens zu beginnen?
    """
    print(geschichte)

# Füge den Aufruf der Funktion `erzaehle_geschichte()` direkt nach der Eingabe des Spielernamens ein.
def starte_spiel():
    name = input("Gib deinen Spielernamen ein: ")
    erzaehle_geschichte()
    spieler = lade_spielerdaten(name)

    if spieler is None:
        # Neuer Spieler
        spieler = Spieler(name, SPIELER_START_LEBENSPUNKTE, SPIELER_START_LEBENSPUNKTE, 0, 1, [], [])
    else:
        spieler.lebenspunkte = spieler.max_lebenspunkte  # Setze die Lebenspunkte auf die maximalen Lebenspunkte
        print(f"Willkommen zurück, {spieler.name}! Level: {spieler.level_system.level}, Erfahrungspunkte: {spieler.level_system.erfahrung}, Lebenspunkte: {spieler.lebenspunkte}/{spieler.max_lebenspunkte}")

    position = 0

    while position < SPIELFELD_GROESSE and spieler.lebenspunkte > 0:
        # Spieler würfelt und bewegt sich auf dem Spielfeld
        eingabe = input("Drücke Enter, um zu würfeln...")
        if eingabe == "":
            wurf = random.randint(1, 6)
            position += wurf
            position = min(position, SPIELFELD_GROESSE - 1)
            print(f"Der Spieler würfelt eine {wurf} und bewegt sich auf Feld {position}.")
            if spieler.spielfeld[position] is not None:
                # Ein Kampf findet statt, wenn ein Gegner auf dem Feld ist
                kampf(spieler, spieler.spielfeld[position])
                if spieler.lebenspunkte <= 0:
                    print("Der Spieler hat keine Lebenspunkte mehr und verliert das Spiel.")
                    break
            if position >= SPIELFELD_GROESSE - 1:
                # Spieler erreicht das Ziel und gewinnt das Spiel
                print("Der Spieler hat das Ziel erreicht und gewinnt das Spiel!")
                break
        else:
            print("Ungültige Eingabe. Bitte drücke nur die Enter-Taste.")

    # Spielende
    if spieler.lebenspunkte <= 0:
        print("Das Spiel ist zu Ende. Der Spieler hat verloren.")
    else:
        print("Herzlichen Glückwunsch! Der Spieler hat gewonnen.")

    # Spielerdaten speichern
    speichere_spielerdaten(spieler)

    # Frage, ob der Spieler erneut spielen möchte
    erneut_spielen = input("Möchtest du erneut spielen? (j/n): ")
    if erneut_spielen.lower() == 'j':
        starte_spiel()
    else:
        print("Danke fürs Spielen!")

# Spiel starten
starte_spiel()
