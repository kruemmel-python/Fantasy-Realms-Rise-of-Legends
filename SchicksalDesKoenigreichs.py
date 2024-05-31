import random
import csv
import os
from dataclasses import dataclass, field
from typing import List, Optional

# Konstanten
LEBENSPUNKTE = {'schwach': 50, 'mittel': 70, 'stark': 90, 'boss': 200}
MAX_SCHADEN = {'schwach': 30, 'mittel': 40, 'stark': 50, 'boss': 75}
GOLD_BELOHNUNG = {'schwach': 10, 'mittel': 20, 'stark': 30, 'boss': 100}
SPIELFELD_GROESSE = 1000
GEGNER_TYPEN = ['schwach', 'mittel', 'stark']
BOSS_TYPEN = ['boss']
ANZAHL_GEGNER_PRO_TYP = 50
ANZAHL_BOSSE = 5
SPIELER_START_LEBENSPUNKTE = 300
SPIELER_MAX_SCHADEN = 35
CSV_DATEI = 'spielerdaten.csv'
START_GOLD = 100

@dataclass
class Gegenstand:
    name: str
    typ: str
    wert: int

@dataclass
class Waffe(Gegenstand):
    schaden: int

@dataclass
class Rüstung(Gegenstand):
    verteidigung: int

@dataclass
class Fähigkeit:
    name: str
    schaden: int
    kosten: int

@dataclass
class Zauber:
    name: str
    schaden: int
    kosten: int
    zauberart: str

@dataclass
class Quest:
    name: str
    beschreibung: str
    belohnung: int
    ziel_typ: str  # 'gegner' oder 'gegenstand'
    ziel_menge: int
    abgeschlossen: bool = False
    fortschritt: int = 0

    def fortschritt_anzeigen(self) -> str:
        return f"{self.fortschritt}/{self.ziel_menge}"

    def fortschritt_aktualisieren(self, menge: int = 1) -> None:
        self.fortschritt += menge
        if self.fortschritt >= self.ziel_menge:
            self.abgeschlossen = True

@dataclass
class Tagesquest(Quest):
    pass

@dataclass
class NPC:
    name: str
    quest: Quest

@dataclass
class LevelSystem:
    erfahrung: int
    level: int = 1

    def erfahrung_sammeln(self, punkte: int, spieler: 'Spieler') -> None:
        self.erfahrung += punkte
        if self.erfahrung >= self.level * 100:
            self.level_up(spieler)

    def level_up(self, spieler: 'Spieler') -> None:
        self.level += 1
        spieler.max_lebenspunkte += 10
        spieler.lebenspunkte = spieler.max_lebenspunkte
        print(f"Glückwunsch! Du hast Level {self.level} erreicht! Deine maximalen Lebenspunkte wurden um 10 erhöht und sind jetzt {spieler.max_lebenspunkte}.")
        spieler.gegner_multiplikator *= 1.15
        spieler.spielfeld = erstelle_spielfeld(spieler.gegner_multiplikator)

@dataclass
class Gegner:
    typ: str
    multiplikator: float = 1.0
    lebenspunkte: int = field(init=False)
    max_schaden: int = field(init=False)
    gold_belohnung: int = field(init=False)
    name: str = field(init=False)

    def __post_init__(self):
        self.lebenspunkte = int(LEBENSPUNKTE[self.typ] * self.multiplikator)
        self.max_schaden = int(MAX_SCHADEN[self.typ] * self.multiplikator)
        self.gold_belohnung = GOLD_BELOHNUNG[self.typ]
        self.name = generiere_gegnernamen(self.typ)

    def angreifen(self) -> int:
        return random.randint(1, self.max_schaden)

@dataclass
class Spieler:
    name: str
    lebenspunkte: int
    max_lebenspunkte: int
    erfahrung: int
    level: int
    gegenstände: List[Gegenstand]
    fähigkeiten: List[Fähigkeit]
    waffe: Optional[Waffe] = None
    rüstung: Optional[Rüstung] = None
    gold: int = START_GOLD
    gegner_multiplikator: float = 1.0
    spielfeld: List[Optional[Gegner]] = field(default_factory=list)
    zauber: List[Zauber] = field(default_factory=list)
    quests: List[Quest] = field(default_factory=list)
    tägliche_herausforderungen: List[Tagesquest] = field(default_factory=list)
    level_system: LevelSystem = field(init=False)

    def __post_init__(self):
        self.level_system = LevelSystem(self.erfahrung, self.level)
        self.spielfeld = erstelle_spielfeld(self.gegner_multiplikator)

    def inventar_anzeigen(self) -> None:
        print(f"Gold: {self.gold}")
        print(f"Lebenspunkte: {self.lebenspunkte}/{self.max_lebenspunkte}")
        print(f"Level: {self.level_system.level}")
        print(f"Erfahrung: {self.level_system.erfahrung}")
        
        if not self.gegenstände:
            print("Dein Inventar ist leer.")
        else:
            print("Du hast folgende Gegenstände in deinem Inventar:")
            for gegenstand in self.gegenstände:
                print(f"{gegenstand.name} - Typ: {gegenstand.typ}, Wert: {gegenstand.wert}")
        if self.waffe:
            print(f"Ausgerüstete Waffe: {self.waffe.name} - Schaden: {self.waffe.schaden}")
        if self.rüstung:
            print(f"Ausgerüstete Rüstung: {self.rüstung.name} - Verteidigung: {self.rüstung.verteidigung}")

    def angreifen(self) -> int:
        waffen_schaden = self.waffe.schaden if self.waffe else 0
        return random.randint(1, SPIELER_MAX_SCHADEN) + waffen_schaden

    def verteidigen(self, schaden: int) -> int:
        rüstung_schutz = self.rüstung.verteidigung if self.rüstung else 0
        reduzierter_schaden = max(schaden - rüstung_schutz, 0)
        self.lebenspunkte -= reduzierter_schaden
        return reduzierter_schaden

    def heilen(self) -> None:
        self.lebenspunkte = min(self.lebenspunkte + 30, self.max_lebenspunkte)
        print(f"Als Siegesbonus wurden die Lebenspunkte des Spielers um 30 erhöht und sind jetzt {self.lebenspunkte}/{self.max_lebenspunkte}.")

    def gegenstand_verwenden(self, gegenstand_name: str) -> None:
        gegenstand = next((g for g in self.gegenstände if g.name == gegenstand_name), None)
        if gegenstand:
            if gegenstand.typ == 'Heiltrank':
                self.lebenspunkte = min(self.lebenspunkte + gegenstand.wert, self.max_lebenspunkte)
                print(f"Du hast {gegenstand.name} verwendet. Lebenspunkte: {self.lebenspunkte}/{self.max_lebenspunkte}")
                self.gegenstände.remove(gegenstand)
            else:
                print(f"Der Gegenstand {gegenstand.name} kann nicht verwendet werden.")
        else:
            print(f"Der Gegenstand {gegenstand_name} ist nicht in deinem Inventar.")

    def heiltrank_nutzen(self) -> None:
        heiltränke = [g for g in self.gegenstände if g.typ == 'Heiltrank']
        if heiltränke:
            antwort = input("Möchtest du einen Heiltrank verwenden? (j/n): ")
            if antwort.lower() == 'j':
                heiltrank = heiltränke[0]
                self.lebenspunkte = min(self.lebenspunkte + heiltrank.wert, self.max_lebenspunkte)
                self.gegenstände.remove(heiltrank)
                print(f"Heiltrank verwendet. Lebenspunkte: {self.lebenspunkte}/{self.max_lebenspunkte}.")
            else:
                print("Heiltrank nicht verwendet.")
        else:
            print("Keine Heiltränke im Inventar.")
        
    def finde_heiltränke(self) -> None:
        anzahl_gefundene_heiltränke = random.randint(0, 2)
        if anzahl_gefundene_heiltränke > 0:
            for _ in range(anzahl_gefundene_heiltränke):
                heiltrank = Gegenstand('Heiltrank', 'Heiltrank', 20)
                self.add_gegenstand(heiltrank)
            print(f"Du hast {anzahl_gefundene_heiltränke} Heiltrank{'e' if anzahl_gefundene_heiltränke > 1 else ''} gefunden und deinem Inventar hinzugefügt.")
        else:
            print("Keine Heiltränke gefunden.")  

    def add_gegenstand(self, gegenstand: Gegenstand) -> None:
        self.gegenstände.append(gegenstand)
        print(f"{gegenstand.name} wurde dem Inventar hinzugefügt.")

    def add_fähigkeit(self, fähigkeit: Fähigkeit) -> None:
        self.fähigkeiten.append(fähigkeit)
        print(f"Fähigkeit {fähigkeit.name} wurde erlernt.")

    def add_zauber(self, zauber: Zauber) -> None:
        self.zauber.append(zauber)
        print(f"Zauber {zauber.name} wurde erlernt.")

    def erfahrung_sammeln(self, punkte: int) -> None:
        self.level_system.erfahrung_sammeln(punkte, self)
    
    def quest_hinzufügen(self, quest: Quest) -> None:
        self.quests.append(quest)
        print(f"Quest {quest.name} wurde hinzugefügt: {quest.beschreibung}")

    def tägliche_herausforderung_hinzufügen(self, herausforderung: Tagesquest) -> None:
        self.tägliche_herausforderungen.append(herausforderung)
        print(f"Tägliche Herausforderung hinzugefügt: {herausforderung.beschreibung}")

    def fähigkeit_auswählen(self) -> Optional[Fähigkeit]:
        if not self.fähigkeiten:
            print("Keine Fähigkeiten verfügbar.")
            return None
        print("Verfügbare Fähigkeiten:")
        for i, fähigkeit in enumerate(self.fähigkeiten):
            print(f"{i + 1}: {fähigkeit.name} - Schaden: {fähigkeit.schaden}, Kosten: {fähigkeit.kosten} Gold")
        wahl = int(input("Wähle die Nummer der Fähigkeit, die du verwenden möchtest: "))
        if 1 <= wahl <= len(self.fähigkeiten):
            return self.fähigkeiten[wahl - 1]
        else:
            print("Ungültige Wahl.")
            return None

    def zauber_auswählen(self) -> Optional[Zauber]:
        if not self.zauber:
            print("Keine Zauber verfügbar.")
            return None
        print("Verfügbare Zauber:")
        for i, zauber in enumerate(self.zauber):
            print(f"{i + 1}: {zauber.name} - Schaden: {zauber.schaden}, Kosten: {zauber.kosten}")
        wahl = int(input("Wähle die Nummer des Zaubers, den du verwenden möchtest: "))
        if 1 <= wahl <= len(self.zauber):
            return self.zauber[wahl - 1]
        else:
            print("Ungültige Wahl.")
            return None

    def zaubern(self, zauber: Zauber, gegner: Gegner) -> None:
        if self.gold >= zauber.kosten:
            self.gold -= zauber.kosten
            gegner.lebenspunkte -= zauber.schaden
            print(f"{zauber.name} wurde gewirkt und verursacht {zauber.schaden} Schaden. {gegner.name} hat noch {gegner.lebenspunkte} Lebenspunkte.")
        else:
            print("Nicht genug Gold, um den Zauber zu wirken.")
        
    def quest_abschließen(self, quest_name: str) -> None:
        quest = next((q for q in self.quests if q.name == quest_name), None)
        if quest and not quest.abgeschlossen:
            self.gold += quest.belohnung
            quest.abgeschlossen = True
            print(f"Quest {quest.name} abgeschlossen! Belohnung: {quest.belohnung} Gold")
        else:
            print(f"Quest {quest_name} nicht gefunden oder bereits abgeschlossen.")

    def tägliche_herausforderung_abschließen(self, herausforderung: Tagesquest) -> None:
        self.gold += herausforderung.belohnung
        print(f"Tägliche Herausforderung abgeschlossen! Belohnung: {herausforderung.belohnung} Gold")
        self.tägliche_herausforderungen.remove(herausforderung)

def speichere_spielerdaten(spieler: Spieler) -> None:
    daten = [spieler.name, spieler.lebenspunkte, spieler.max_lebenspunkte,
             spieler.level_system.erfahrung, spieler.level_system.level,
             ';'.join([gegenstand.name for gegenstand in spieler.gegenstände]),
             ';'.join([fähigkeit.name for fähigkeit in spieler.fähigkeiten]),
             spieler.gold, spieler.waffe.name if spieler.waffe else '', spieler.rüstung.name if spieler.rüstung else '']

    vorhandene_daten = []
    if os.path.exists(CSV_DATEI):
        with open(CSV_DATEI, 'r', newline='') as file:
            reader = csv.reader(file)
            vorhandene_daten = list(reader)

    mit_kopfzeile = False
    if len(vorhandene_daten) == 0 or vorhandene_daten[0] != ['Name', 'Lebenspunkte', 'MaxLebenspunkte', 'Erfahrung', 'Level', 'Gegenstände', 'Fähigkeiten', 'Gold', 'Waffe', 'Rüstung']:
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
            writer.writerow(['Name', 'Lebenspunkte', 'MaxLebenspunkte', 'Erfahrung', 'Level', 'Gegenstände', 'Fähigkeiten', 'Gold', 'Waffe', 'Rüstung'])
        writer.writerows(vorhandene_daten)

def lade_spielerdaten(name: str) -> Optional[Spieler]:
    if not os.path.exists(CSV_DATEI):
        return None

    with open(CSV_DATEI, 'r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Name'] == name:
                max_lebenspunkte = int(row['MaxLebenspunkte'])
                lebenspunkte = max_lebenspunkte
                erfahrung = int(row['Erfahrung'])
                level = int(row['Level'])
                gegenstände = [Gegenstand(name, '', 0) for name in row['Gegenstände'].split(';') if name]
                fähigkeiten = [Fähigkeit(name, 0, 0) for name in row['Fähigkeiten'].split(';') if name]
                gold = int(row['Gold'])
                waffe = Waffe(row['Waffe'], 0, 0) if row['Waffe'] else None
                rüstung = Rüstung(row['Rüstung'], 0, 0) if row['Rüstung'] else None
                return Spieler(name, lebenspunkte, max_lebenspunkte, erfahrung, level, gegenstände, fähigkeiten, waffe, rüstung, gold)
    return None

def erstelle_spielfeld(multiplikator: float = 1.0) -> List[Optional[Gegner]]:
    spielfeld = [None] * SPIELFELD_GROESSE
    verfügbare_positionen = list(range(SPIELFELD_GROESSE))

    for typ in GEGNER_TYPEN:
        for _ in range(ANZAHL_GEGNER_PRO_TYP):
            position = random.choice(verfügbare_positionen)
            verfügbare_positionen.remove(position)
            spielfeld[position] = Gegner(typ, multiplikator)

    for _ in range(ANZAHL_BOSSE):
        position = random.choice(verfügbare_positionen)
        verfügbare_positionen.remove(position)
        spielfeld[position] = Gegner('boss', multiplikator)

    return spielfeld

def generiere_gegnernamen(typ: str) -> str:
    namen = {
        'schwach': ['Kobold', 'Goblin', 'Wicht'],
        'mittel': ['Ork', 'Troll', 'Werwolf'],
        'stark': ['Drache', 'Dämon', 'Riese'],
        'boss': ['Minotaurus', 'Hydra', 'Drachenlord']
    }
    return random.choice(namen[typ])

def kampfeinleitung(gegner: Gegner) -> None:
    einleitungen = {
        'schwach': f"Achtung! Du bist auf einen {gegner.name} gestoßen. Bereite dich auf einen Kampf vor!",
        'mittel': f"Vorsicht! Ein wilder {gegner.name} kreuzt deinen Weg. Zeige ihm deine Stärke!",
        'stark': f"Ein mächtiger {gegner.name} erscheint! Dies wird eine wahre Herausforderung!",
        'boss': f"Ein epischer Kampf steht bevor! Der {gegner.name} fordert dich heraus!"
    }
    print(einleitungen[gegner.typ])

def kampf(spieler: Spieler, gegner: Gegner) -> None:
    kampfeinleitung(gegner)
    while spieler.lebenspunkte > 0 and gegner.lebenspunkte > 0:
        print("\nKampfmenü")
        print("1: Angriff")
        print("2: Fähigkeit verwenden")
        print("3: Zauber verwenden")
        print("4: Heiltrank verwenden")
        print("5: Kampf abbrechen und ins Hauptmenü zurückkehren")

        wahl = input("Wähle eine Option: ")

        if wahl == '1':
            schaden = spieler.angreifen()
            gegner.lebenspunkte -= schaden
            print(f"Du verursachst {schaden} Schaden. {gegner.name} hat noch {gegner.lebenspunkte} Lebenspunkte.")
        elif wahl == '2':
            fähigkeit = spieler.fähigkeit_auswählen()
            if fähigkeit and spieler.gold >= fähigkeit.kosten:
                spieler.gold -= fähigkeit.kosten
                gegner.lebenspunkte -= fähigkeit.schaden
                print(f"Fähigkeit {fähigkeit.name} verwendet und {fähigkeit.schaden} Schaden verursacht. {gegner.name} hat noch {gegner.lebenspunkte} Lebenspunkte.")
            elif fähigkeit:
                print("Nicht genug Gold, um die Fähigkeit zu verwenden.")
        elif wahl == '3':
            zauber = spieler.zauber_auswählen()
            if zauber and spieler.gold >= zauber.kosten:
                spieler.zaubern(zauber, gegner)
            elif zauber:
                print("Nicht genug Gold, um den Zauber zu wirken.")
        elif wahl == '4':
            spieler.heiltrank_nutzen()
        elif wahl == '5':
            print("Du hast den Kampf abgebrochen und kehrst ins Hauptmenü zurück.")
            return zeige_menü(spieler)   # Hier kehren wir zum Hauptmenü zurück
        else:
            print("Ungültige Wahl. Bitte wähle eine Option aus dem Menü.")

        if gegner.lebenspunkte <= 0:
            print(f"{gegner.name} wurde besiegt!")
            spieler.gold += gegner.gold_belohnung
            print(f"Du hast {gegner.gold_belohnung} Gold erhalten.")
            spieler.erfahrung_sammeln(50)
            spieler.heilen()
            spieler.finde_heiltränke()
            for quest in spieler.quests:
                if quest.ziel_typ == 'gegner' and not quest.abgeschlossen:
                    quest.fortschritt_aktualisieren()
                    print(f"Fortschritt bei Quest {quest.name}: {quest.fortschritt_anzeigen()}")
            speichere_spielerdaten(spieler)
            return

        gegner_schaden = gegner.angreifen()
        reduzierter_schaden = spieler.verteidigen(gegner_schaden)
        if spieler.lebenspunkte <= 0:
            print(f"{gegner.name} verursacht {gegner_schaden} Schaden. Der Spieler wurde besiegt.")
            break
        else:
            print(f"{gegner.name} verursacht {gegner_schaden} Schaden. Nach Verteidigung hat der Spieler noch {spieler.lebenspunkte} Lebenspunkte.")
            spieler.heiltrank_nutzen()

def erzähle_geschichte() -> None:
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

def starte_spiel() -> None:
    name = input("Gib deinen Spielernamen ein: ")
    erzähle_geschichte()
    spieler = lade_spielerdaten(name)

    if spieler is None:
        spieler = Spieler(name, SPIELER_START_LEBENSPUNKTE, SPIELER_START_LEBENSPUNKTE, 0, 1, [], [])
    else:
        spieler.lebenspunkte = spieler.max_lebenspunkte
        print(f"Willkommen zurück, {spieler.name}! Level: {spieler.level_system.level}, Erfahrungspunkte: {spieler.level_system.erfahrung}, Lebenspunkte: {spieler.lebenspunkte}/{spieler.max_lebenspunkte}")

    while True:
        zeige_menü(spieler)

def zeige_menü(spieler: Spieler) -> None:
    print("\nHauptmenü")
    print("1: Erkunden")
    print("2: Inventar anzeigen")
    print("3: Fähigkeiten lernen")
    print("4: Zauber wirken")
    print("5: Quests anzeigen")
    print("6: Tägliche Herausforderung abschließen")
    print("7: Händler besuchen")
    print("8: Spiel speichern")
    print("9: Spiel beenden")

    wahl = input("Wähle eine Option: ")

    if wahl == '1':
        erkunden(spieler)
    elif wahl == '2':
        spieler.inventar_anzeigen()
    elif wahl == '3':
        fähigkeiten_lernen(spieler)
    elif wahl == '4':
        zauber_wirken(spieler)
    elif wahl == '5':
        quests_anzeigen(spieler)
    elif wahl == '6':
        tägliche_herausforderung_abschließen(spieler)
    elif wahl == '7':
        händler_besuchen(spieler)
    elif wahl == '8':
        speichere_spielerdaten(spieler)
    elif wahl == '9':
        spiel_beenden()
    else:
        print("Ungültige Wahl. Bitte versuche es erneut.")

def erkunden(spieler: Spieler) -> None:
    position = 0
    while position < SPIELFELD_GROESSE and spieler.lebenspunkte > 0:
        input("Drücke Enter, um zu würfeln...")
        wurf = random.randint(1, 6)
        position += wurf
        position = min(position, SPIELFELD_GROESSE - 1)
        print(f"Der Spieler würfelt eine {wurf} und bewegt sich auf Feld {position}.")
        if spieler.spielfeld[position] is not None:
            kampf(spieler, spieler.spielfeld[position])
            if spieler.lebenspunkte <= 0:
                print("Der Spieler hat keine Lebenspunkte mehr und verliert das Spiel.")
                break
        else:
            npc_treffen(spieler)
        if position >= SPIELFELD_GROESSE - 1:
            print("Der Spieler hat das Ziel erreicht und gewinnt das Spiel!")
            break

    if spieler.lebenspunkte <= 0:
        print("Das Spiel ist zu Ende. Der Spieler hat verloren.")
    else:
        print("Herzlichen Glückwunsch! Der Spieler hat gewonnen.")

    speichere_spielerdaten(spieler)

    erneut_spielen = input("Möchtest du erneut spielen? (j/n): ")
    if erneut_spielen.lower() == 'j':
        starte_spiel()
    else:
        print("Danke fürs Spielen!")

def fähigkeiten_lernen(spieler: Spieler) -> None:
    verfügbare_fähigkeiten = [
        Fähigkeit("Feuerball", 50, 20),
        Fähigkeit("Eissplitter", 40, 15),
        Fähigkeit("Blitzschlag", 60, 25),
        Fähigkeit("Heilung", 0, 10)
    ]
    
    print("Verfügbare Fähigkeiten zum Lernen:")
    for i, fähigkeit in enumerate(verfügbare_fähigkeiten):
        print(f"{i + 1}: {fähigkeit.name} - Schaden: {fähigkeit.schaden}, Kosten: {fähigkeit.kosten} Gold")
    
    wahl = int(input("Wähle die Nummer der Fähigkeit, die du lernen möchtest (oder 0, um abzubrechen): "))
    
    if 1 <= wahl <= len(verfügbare_fähigkeiten):
        ausgewählte_fähigkeit = verfügbare_fähigkeiten[wahl - 1]
        if spieler.gold >= ausgewählte_fähigkeit.kosten:
            spieler.gold -= ausgewählte_fähigkeit.kosten
            spieler.add_fähigkeit(ausgewählte_fähigkeit)
            print(f"Du hast die Fähigkeit {ausgewählte_fähigkeit.name} gelernt.")
        else:
            print("Du hast nicht genug Gold, um diese Fähigkeit zu lernen.")
    else:
        print("Abgebrochen.")

def zauber_wirken(spieler: Spieler) -> None:
    zauber = spieler.zauber_auswählen()
    if zauber:
        gegner = Gegner('mittel')  # Beispielgegner
        spieler.zaubern(zauber, gegner)

def quests_anzeigen(spieler: Spieler) -> None:
    if not spieler.quests:
        print("Keine Quests verfügbar.")
    else:
        print("Aktuelle Quests:")
        for i, quest in enumerate(spieler.quests):
            status = "Abgeschlossen" if quest.abgeschlossen else f"Fortschritt: {quest.fortschritt_anzeigen()}"
            print(f"{i + 1}: {quest.name} - {quest.beschreibung} - Belohnung: {quest.belohnung} Gold - Status: {status}")
        
        wahl = int(input("Wähle die Nummer der Quest, die du abschließen möchtest (oder 0, um ins Hauptmenü zurückzukehren): "))
        if 1 <= wahl <= len(spieler.quests):
            ausgewählte_quest = spieler.quests[wahl - 1]
            if ausgewählte_quest.abgeschlossen:
                spieler.quest_abschließen(ausgewählte_quest.name)
                return zeige_menü(spieler)
            else:
                print(f"Die Quest {ausgewählte_quest.name} ist noch nicht abgeschlossen.")
                return zeige_menü(spieler)
        else:
            print("Zurück zum Hauptmenü.")

def tägliche_herausforderung_abschließen(spieler: Spieler) -> None:
    if not spieler.tägliche_herausforderungen:
        print("Keine täglichen Herausforderungen verfügbar.")
        return zeige_menü(spieler)
    else:
        herausforderung = spieler.tägliche_herausforderungen[0]
        spieler.tägliche_herausforderung_abschließen(herausforderung)
        return zeige_menü(spieler)

def npc_treffen(spieler: Spieler) -> None:
    if random.random() < 0.2:  # 20% Chance, einen NPC zu treffen
        npc_name = random.choice(["Gandalf", "Aragorn", "Legolas", "Gimli"])
        quest_name = f"{npc_name}s Quest"
        quest_beschreibung = f"Hilf {npc_name}, die Dunkelheit zu vertreiben."
        quest_belohnung = random.randint(50, 100)
        ziel_typ = random.choice(['gegner', 'gegenstand'])
        ziel_menge = random.randint(1, 5)
        npc = NPC(npc_name, Quest(quest_name, quest_beschreibung, quest_belohnung, ziel_typ, ziel_menge))
        
        print(f"Du triffst {npc.name}. Er bietet dir eine Quest an: {npc.quest.name} - {npc.quest.beschreibung} - Belohnung: {npc.quest.belohnung} Gold")
        annehmen = input("Möchtest du die Quest annehmen? (j/n): ")
        if annehmen.lower() == 'j':
            spieler.quest_hinzufügen(npc.quest)
        else:
            print("Quest abgelehnt.")

def händler_besuchen(spieler: Spieler) -> None:
    angebote = [
        Waffe(name="Schwert", typ="Waffe", wert=50, schaden=10),
        Waffe(name="Axt", typ="Waffe", wert=70, schaden=15),
        Rüstung(name="Lederpanzer", typ="Rüstung", wert=60, verteidigung=5),
        Rüstung(name="Kettenhemd", typ="Rüstung", wert=100, verteidigung=10),
        Gegenstand(name="Heiltrank", typ="Heiltrank", wert=20)
    ]
    
    print("Willkommen beim Händler! Hier sind die verfügbaren Gegenstände:")
    for i, angebot in enumerate(angebote):
        print(f"{i + 1}: {angebot.name} - Typ: {angebot.typ}, Wert: {angebot.wert}, Preis: {angebot.wert} Gold")
    
    wahl = int(input("Wähle die Nummer des Gegenstands, den du kaufen möchtest (oder 0, um abzubrechen): "))
    
    if 1 <= wahl <= len(angebote):
        auswahl = angebote[wahl - 1]
        if spieler.gold >= auswahl.wert:
            spieler.gold -= auswahl.wert
            if isinstance(auswahl, Waffe):
                spieler.waffe = auswahl
            elif isinstance(auswahl, Rüstung):
                spieler.rüstung = auswahl
            else:
                spieler.add_gegenstand(auswahl)
            print(f"Du hast {auswahl.name} gekauft.")
        else:
            print("Du hast nicht genug Gold.")
    else:
        print("Abgebrochen.")


def spiel_beenden() -> None:
    print("Das Spiel wird beendet. Danke fürs Spielen!")
    exit()

starte_spiel()
