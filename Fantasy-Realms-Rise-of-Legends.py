from typing import Tuple, List, Optional, Dict
import random
import csv
import os
import json
from dataclasses import dataclass, field
"""
Erstellt von: Ralf Krümmel
Datum: 03.06.2024
Beschreibung: Dieser Code ist in 7 Tagen entstanden.
"""
# Zufällige Farbauswahl ohne Weiß
def zufallsfarbe():
    farben = ["\033[31m", "\033[32m", "\033[33m", "\033[34m", "\033[35m", "\033[36m"]
    return random.choice(farben)

# Konstanten
LEBENSPUNKTE = {'schwach': 150, 'mittel': 170, 'stark': 190, 'boss': 200}
MAX_SCHADEN = {'schwach': 60, 'mittel': 80, 'stark': 90, 'boss': 110}
GOLD_BELOHNUNG = {'schwach': (0, 0, 1), 'mittel': (0, 0, 3), 'stark': (0, 0, 5), 'boss': (0, 0, 10)}
SPIELFELD_GROESSE = 10000
GEGNER_TYPEN = ['schwach', 'mittel', 'stark']
BOSS_TYPEN = ['boss']
ANZAHL_GEGNER_PRO_TYP = 6000
ANZAHL_BOSSE = 3000
SPIELER_START_LEBENSPUNKTE = 300
SPIELER_MAX_SCHADEN = 55
SPIELER_START_MANA = 200
SPIELER_MAX_MANA = 300
CSV_DATEI = 'spielerdaten.csv'
START_GOLD = (0, 0, 1)  # (Kupfer, Silber, Gold)

# Dropraten for seltene Gegenstände
SELTENE_DROP_RATE = 0.15  # 15%
SEHR_SELTENE_DROP_RATE = 0.01  # 1%

class Farben:
    ROT = '\033[91m'
    GRUEN = '\033[92m'
    GELB = '\033[93m'
    BLAU = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WEISS = '\033[97m'
    ENDE = '\033[0m'

# Definieren der Ressourcenklasse
@dataclass
class Resource:
    name: str
    category: str

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

# Definieren der Ressourcen
wood = Resource("Holz", "Material")
stone = Resource("Stein", "Material")
iron = Resource("Eisen", "Metall")
herb = Resource("Kraut", "Pflanze")
magic_stone = Resource("Magischer Stein", "Magie")

# Liste der möglichen Namen für die Gegenstände
GEGENSTAND_NAMEN = [
    "Flammenzorn", "Eiswind", "Erdbeber", "Sturmbringer",
    "Schattenläufer", "Lichtbogen", "Naturgewalt", "Sternenfunkeln"
]

# Liste der Gegenstände, die ein Spieler benutzen kann
BENUTZBARE_GEGENSTAENDE = [
    # Waffen
    Waffe(name="Dämonenklinge", typ="Waffe", wert=100, schaden=45),
    Waffe(name="Kriegsbeil", typ="Waffe", wert=120, schaden=30),
    Waffe(name="Drachenschwert", typ="Waffe", wert=200, schaden=60),
    Waffe(name="Elfenbogen", typ="Waffe", wert=150, schaden=50),
    Waffe(name="Flammenaxt", typ="Waffe", wert=180, schaden=55),
    Waffe(name="Frostspeer", typ="Waffe", wert=140, schaden=40),
    Waffe(name="Blitzdolch", typ="Waffe", wert=160, schaden=45),
    Waffe(name="Sturmbrecher", typ="Waffe", wert=220, schaden=65),
    Waffe(name="Windklinge", typ="Waffe", wert=170, schaden=48),
    Waffe(name="Nachtstab", typ="Waffe", wert=130, schaden=35),
    Waffe(name="Höllenzepter", typ="Waffe", wert=190, schaden=58),
    Waffe(name="Vergeltungshammer", typ="Waffe", wert=210, schaden=70),
    Waffe(name="Giftpfeil", typ="Waffe", wert=140, schaden=38),
    Waffe(name="Schattenschwert", typ="Waffe", wert=180, schaden=52),
    Waffe(name="Blutklinge", typ="Waffe", wert=200, schaden=60),
    Waffe(name="Wellenbrecher", typ="Waffe", wert=150, schaden=45),
    Waffe(name="Donnerschlag", typ="Waffe", wert=220, schaden=70),
    Waffe(name="Schattenpike", typ="Waffe", wert=130, schaden=42),
    Waffe(name="Sonnenschwert", typ="Waffe", wert=170, schaden=48),
    Waffe(name="Nebellanze", typ="Waffe", wert=140, schaden=39),
    Waffe(name="Feuerklinge", typ="Waffe", wert=160, schaden=50),
    Waffe(name="Eisdolch", typ="Waffe", wert=130, schaden=34),
    Waffe(name="Erdbebenhammer", typ="Waffe", wert=180, schaden=56),
    Waffe(name="Lichtbogen", typ="Waffe", wert=190, schaden=60),
    Waffe(name="Sternenstab", typ="Waffe", wert=150, schaden=45),
    Waffe(name="Todesstachel", typ="Waffe", wert=200, schaden=65),
    Waffe(name="Nebelkrieger", typ="Waffe", wert=170, schaden=49),
    Waffe(name="Dämonenfaust", typ="Waffe", wert=210, schaden=68),
    Waffe(name="Engelschwert", typ="Waffe", wert=180, schaden=54),
    Waffe(name="Phantomklinge", typ="Waffe", wert=140, schaden=42),
    Waffe(name="Dunkelheitslanze", typ="Waffe", wert=200, schaden=63),
 
    Rüstung(name="Bronzehelm", typ="Helm", wert=30, verteidigung=10),
    Rüstung(name="Leinenrobe", typ="Robe", wert=25, verteidigung=5),
    Rüstung(name="Wollhandschuhe", typ="Handschuhe", wert=20, verteidigung=3),
    Rüstung(name="Baumwollmantel", typ="Mantel", wert=35, verteidigung=7),
    Rüstung(name="Strohhelm", typ="Helm", wert=10, verteidigung=2),
    Rüstung(name="Seidenstiefel", typ="Stiefel", wert=45, verteidigung=12),
    Rüstung(name="Leichtes Schild", typ="Schild", wert=50, verteidigung=15),
    Rüstung(name="Holzbrustpanzer", typ="Rüstung", wert=40, verteidigung=8),
    Rüstung(name="Ledergürtel", typ="Gürtel", wert=15, verteidigung=6),
    Rüstung(name="Samtcape", typ="Cape", wert=25, verteidigung=5),
    Rüstung(name="Plattenpanzer", typ="Rüstung", wert=100, verteidigung=50),
    Rüstung(name="Goldene Krone", typ="Helm", wert=75, verteidigung=20),
    Rüstung(name="Diamanthandschuhe", typ="Handschuhe", wert=90, verteidigung=25),
    Rüstung(name="Drachenrobe", typ="Robe", wert=85, verteidigung=30),
    Rüstung(name="Geistercape", typ="Cape", wert=60, verteidigung=18),
    Rüstung(name="Schattenstiefel", typ="Stiefel", wert=70, verteidigung=22),
    Rüstung(name="Mithrilschild", typ="Schild", wert=120, verteidigung=30),
    Rüstung(name="Kristallbrustpanzer", typ="Rüstung", wert=130, verteidigung=35),
    Rüstung(name="Eisengürtel", typ="Gürtel", wert=20, verteidigung=8),
    Rüstung(name="Feuerumhang", typ="Cape", wert=50, verteidigung=12),
    Rüstung(name="Silberhelm", typ="Helm", wert=55, verteidigung=16),
    Rüstung(name="Schlangenstiefel", typ="Stiefel", wert=65, verteidigung=19),
    Rüstung(name="Dunkelelfenrobe", typ="Robe", wert=80, verteidigung=25),
    Rüstung(name="Magierhut", typ="Helm", wert=40, verteidigung=10),
    Rüstung(name="Trollhandschuhe", typ="Handschuhe", wert=35, verteidigung=8),
    Rüstung(name="Dämonenmantel", typ="Mantel", wert=95, verteidigung=35),
    Rüstung(name="Zwergenrüstung", typ="Rüstung", wert=110, verteidigung=28),
    Rüstung(name="Schwarzstahlbrustpanzer", typ="Rüstung", wert=140, verteidigung=20),
    Rüstung(name="Titanhandschuhe", typ="Handschuhe", wert=85, verteidigung=28),
    Rüstung(name="Phantomrobe", typ="Robe", wert=75, verteidigung=22),
]


# Zuordnung von Namen zu speziellen Effekten
SPEZIELLE_EFFEKTE = {
    "Flammenzorn": {"schaden": 5, "effekt": "Feuer"},
    "Eiswind": {"verteidigung": 3, "effekt": "Eis"},
    "Erdbeber": {"schaden": 4, "verteidigung": 2, "effekt": "Erde"},
    "Sturmbringer": {"schaden": 6, "effekt": "Blitz"},
    "Schattenläufer": {"verteidigung": 4, "effekt": "Schatten"},
    "Lichtbogen": {"schaden": 5, "verteidigung": 1, "effekt": "Licht"},
    "Naturgewalt": {"schaden": 3, "verteidigung": 3, "effekt": "Natur"},
    "Sternenfunkeln": {"schaden": 2, "verteidigung": 4, "effekt": "Sterne"}
}

@dataclass
class MagischeSchriftrolle(Gegenstand):
    schaden: int
    kosten: int
    mana_kosten: int
    zauberart: str

MAGISCHE_SCHRIFTROLLEN = [
    MagischeSchriftrolle(name="Feuerball-Schriftrolle", typ="Schriftrolle", wert=100, schaden=50, kosten=100, mana_kosten=30, zauberart="Feuer"),
    MagischeSchriftrolle(name="Blitz-Schriftrolle", typ="Schriftrolle", wert=120, schaden=60, kosten=120, mana_kosten=40, zauberart="Blitz"),
    MagischeSchriftrolle(name="Eislanzen-Schriftrolle", typ="Schriftrolle", wert=80, schaden=40, kosten=80, mana_kosten=20, zauberart="Eis"),
    MagischeSchriftrolle(name="Feuersturm-Schriftrolle", typ="Schriftrolle", wert=150, schaden=70, kosten=150, mana_kosten=35, zauberart="Feuer"),
    MagischeSchriftrolle(name="Erdbeben-Schriftrolle", typ="Schriftrolle", wert=130, schaden=65, kosten=130, mana_kosten=45, zauberart="Erde"),
    MagischeSchriftrolle(name="Windstoß-Schriftrolle", typ="Schriftrolle", wert=90, schaden=50, kosten=90, mana_kosten=25, zauberart="Luft"),
    MagischeSchriftrolle(name="Wasserflut-Schriftrolle", typ="Schriftrolle", wert=110, schaden=55, kosten=110, mana_kosten=30, zauberart="Wasser"),
    MagischeSchriftrolle(name="Lichtstrahl-Schriftrolle", typ="Schriftrolle", wert=140, schaden=60, kosten=140, mana_kosten=40, zauberart="Licht"),
    MagischeSchriftrolle(name="Schattenklinge-Schriftrolle", typ="Schriftrolle", wert=160, schaden=70, kosten=160, mana_kosten=35, zauberart="Schatten"),
    MagischeSchriftrolle(name="Feuerschild-Schriftrolle", typ="Schriftrolle", wert=110, schaden=30, kosten=110, mana_kosten=25, zauberart="Feuer"),
    MagischeSchriftrolle(name="Blitznetz-Schriftrolle", typ="Schriftrolle", wert=130, schaden=50, kosten=130, mana_kosten=40, zauberart="Blitz"),
    MagischeSchriftrolle(name="Eiswand-Schriftrolle", typ="Schriftrolle", wert=100, schaden=20, kosten=100, mana_kosten=20, zauberart="Eis"),
    MagischeSchriftrolle(name="Erdfestung-Schriftrolle", typ="Schriftrolle", wert=120, schaden=40, kosten=120, mana_kosten=30, zauberart="Erde"),
    MagischeSchriftrolle(name="Luftstoß-Schriftrolle", typ="Schriftrolle", wert=80, schaden=30, kosten=80, mana_kosten=15, zauberart="Luft"),
    MagischeSchriftrolle(name="Wasserbarriere-Schriftrolle", typ="Schriftrolle", wert=90, schaden=35, kosten=90, mana_kosten=25, zauberart="Wasser"),
    MagischeSchriftrolle(name="Lichtblitz-Schriftrolle", typ="Schriftrolle", wert=130, schaden=50, kosten=130, mana_kosten=35, zauberart="Licht"),
    MagischeSchriftrolle(name="Schattenhieb-Schriftrolle", typ="Schriftrolle", wert=150, schaden=60, kosten=150, mana_kosten=40, zauberart="Schatten"),
    MagischeSchriftrolle(name="Feuerpfeil-Schriftrolle", typ="Schriftrolle", wert=100, schaden=40, kosten=100, mana_kosten=20, zauberart="Feuer"),
    MagischeSchriftrolle(name="Blitzsturm-Schriftrolle", typ="Schriftrolle", wert=160, schaden=70, kosten=160, mana_kosten=50, zauberart="Blitz"),
    MagischeSchriftrolle(name="Eishauch-Schriftrolle", typ="Schriftrolle", wert=90, schaden=35, kosten=90, mana_kosten=25, zauberart="Eis"),
    MagischeSchriftrolle(name="Erdbeben-Schriftrolle", typ="Schriftrolle", wert=140, schaden=65, kosten=140, mana_kosten=45, zauberart="Erde"),
    MagischeSchriftrolle(name="Windfaust-Schriftrolle", typ="Schriftrolle", wert=110, schaden=50, kosten=110, mana_kosten=30, zauberart="Luft"),
    MagischeSchriftrolle(name="Wasserspeer-Schriftrolle", typ="Schriftrolle", wert=120, schaden=55, kosten=120, mana_kosten=35, zauberart="Wasser"),
    MagischeSchriftrolle(name="Lichtschild-Schriftrolle", typ="Schriftrolle", wert=130, schaden=30, kosten=130, mana_kosten=25, zauberart="Licht"),
    MagischeSchriftrolle(name="Schattenfessel-Schriftrolle", typ="Schriftrolle", wert=150, schaden=40, kosten=150, mana_kosten=30, zauberart="Schatten"),
    MagischeSchriftrolle(name="Feuerkugel-Schriftrolle", typ="Schriftrolle", wert=110, schaden=60, kosten=110, mana_kosten=35, zauberart="Feuer"),
    MagischeSchriftrolle(name="Blitzkette-Schriftrolle", typ="Schriftrolle", wert=130, schaden=70, kosten=130, mana_kosten=50, zauberart="Blitz"),
    MagischeSchriftrolle(name="Eisstrahl-Schriftrolle", typ="Schriftrolle", wert=100, schaden=45, kosten=100, mana_kosten=30, zauberart="Eis"),
    MagischeSchriftrolle(name="Erdschock-Schriftrolle", typ="Schriftrolle", wert=120, schaden=50, kosten=120, mana_kosten=35, zauberart="Erde"),
    MagischeSchriftrolle(name="Luftwirbel-Schriftrolle", typ="Schriftrolle", wert=80, schaden=40, kosten=80, mana_kosten=20, zauberart="Luft"),
    MagischeSchriftrolle(name="Wasserpeitsche-Schriftrolle", typ="Schriftrolle", wert=90, schaden=45, kosten=90, mana_kosten=30, zauberart="Wasser"),
    MagischeSchriftrolle(name="Lichtstrahl-Schriftrolle", typ="Schriftrolle", wert=140, schaden=60, kosten=140, mana_kosten=40, zauberart="Licht"),
    MagischeSchriftrolle(name="Schattenflamme-Schriftrolle", typ="Schriftrolle", wert=160, schaden=70, kosten=160, mana_kosten=50, zauberart="Schatten"),
    MagischeSchriftrolle(name="Feuerpeitsche-Schriftrolle", typ="Schriftrolle", wert=110, schaden=50, kosten=110, mana_kosten=25, zauberart="Feuer"),
    MagischeSchriftrolle(name="Blitzsprung-Schriftrolle", typ="Schriftrolle", wert=130, schaden=60, kosten=130, mana_kosten=40, zauberart="Blitz"),
    MagischeSchriftrolle(name="Eisschild-Schriftrolle", typ="Schriftrolle", wert=100, schaden=20, kosten=100, mana_kosten=15, zauberart="Eis"),
    MagischeSchriftrolle(name="Erdriss-Schriftrolle", typ="Schriftrolle", wert=120, schaden=55, kosten=120, mana_kosten=35, zauberart="Erde"),
    MagischeSchriftrolle(name="Luftschnitt-Schriftrolle", typ="Schriftrolle", wert=80, schaden=35, kosten=80, mana_kosten=20, zauberart="Luft"),
    MagischeSchriftrolle(name="Wasserstoß-Schriftrolle", typ="Schriftrolle", wert=90, schaden=40, kosten=90, mana_kosten=25, zauberart="Wasser"),
    MagischeSchriftrolle(name="Lichtbann-Schriftrolle", typ="Schriftrolle", wert=130, schaden=50, kosten=130, mana_kosten=30, zauberart="Licht"),
    MagischeSchriftrolle(name="Schattenblitz-Schriftrolle", typ="Schriftrolle", wert=150, schaden=65, kosten=150, mana_kosten=40, zauberart="Schatten"),
    MagischeSchriftrolle(name="Feuersturm-Schriftrolle", typ="Schriftrolle", wert=160, schaden=75, kosten=160, mana_kosten=50, zauberart="Feuer"),
]

@dataclass
class Fähigkeit:
    name: str
    schaden: int
    kosten: int
    mana_kosten: int = 0

    def schaden_erhoehen(self, prozent: float) -> None:
        self.schaden = int(self.schaden * (1 + prozent / 100))
        print(f"Schaden der Fähigkeit {self.name} erhöht auf {self.schaden}")

@dataclass
class Quest:
    name: str
    beschreibung: str
    belohnung: Tuple[int, int, int]  # (Kupfer, Silber, Gold)
    ziel_typ: str
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
        self.erfahrung -= self.level * 100
        self.level += 1
        spieler.max_lebenspunkte += 50
        spieler.max_mana += 100
        spieler.lebenspunkte = spieler.max_lebenspunkte
        spieler.mana = spieler.max_mana
        print(f"{spieler.name} ist jetzt Level {self.level}!")
    
        # Erhöhe Leben und Schaden der Gegner um 10%
        for gegner in spieler.spielfeld:
            if gegner is not None:
                gegner.multiplikator *= 1.60
                gegner.lebenspunkte = int(LEBENSPUNKTE[gegner.typ] * gegner.multiplikator)
                gegner.max_schaden = int(MAX_SCHADEN[gegner.typ] * gegner.multiplikator)

        if self.level == 30:
            spieler.waehle_spezialisierung()


class Skill:
    def __init__(self, name, level=1, max_level=10, grundschaden=0, gold_cost=1):
        self.name = name
        self.level = level
        self.max_level = max_level
        self.grundschaden = grundschaden
        self.gold_cost = gold_cost

    def level_up(self, spieler, fähigkeit: Fähigkeit):
        if self.level < self.max_level:
            if spieler.gold >= self.gold_cost:
                spieler.gold -= self.gold_cost
                self.level += 1
                self.grundschaden = int(self.grundschaden * 1.4)  #40% Erhöhung des grundschadens
                fähigkeit.schaden_erhoehen(10)  # Erhöht den Schaden der Fähigkeit um 10%
                print(f"{self.name} hat Level {self.level} erreicht! Neuer grundschaden: {self.grundschaden}")
            else:
                raise ValueError("not genügend Gold")
        else:
            raise ValueError("Maximales Level erreicht")

    def berechne_schaden(self):
        return self.grundschaden + (self.level * 10)  # Beispiel: 5 Schaden pro Level

    def __repr__(self):
        return f"{self.name} (Level {self.level}/{self.max_level}, Gold-Kosten: {self.gold_cost})"

class Skillsystem:
    def __init__(self):
        self.skills = []

    def add_skill(self, skill):
        self.skills.append(skill)

    def level_up_skill(self, skill_name, spieler):
        for skill in self.skills:
            if skill.name == skill_name:
                fähigkeit = next((f for f in spieler.fähigkeiten if f.name == skill_name), None)
                if fähigkeit:
                    skill.level_up(spieler, fähigkeit)
                    return skill
        raise ValueError(f"Skill {skill_name} not gefanden")

    def zeige_skills(self):
        for skill in self.skills:
            print(skill)

    def __repr__(self):
        return "\n".join(str(skill) for skill in self.skills)

class KriegerSkillsystem(Skillsystem):
    def __init__(self):
        super().__init__()
        self.add_skill(Skill("Schwertkampf", gold_cost=100))
        self.add_skill(Skill("Schildnutzung", gold_cost=100))
        self.add_skill(Skill("Berserker-Rage", gold_cost=100))                                                       
        self.add_skill(Skill("Kampfgeschick", gold_cost=100))
        self.add_skill(Skill("Kriegerstärke", gold_cost=100))

class MagierSkillsystem(Skillsystem):
    def __init__(self):
        super().__init__()
        self.add_skill(Skill("Feuerball", gold_cost=100))
        self.add_skill(Skill("Eislanze", gold_cost=100))
        self.add_skill(Skill("Blitzschlag", gold_cost=100))
        self.add_skill(Skill("Magische Barriere", gold_cost=100))
        self.add_skill(Skill("Arkane Macht", gold_cost=100))

class SchurkeSkillsystem(Skillsystem):
    def __init__(self):
        super().__init__()
        self.add_skill(Skill("Schleichangriff", gold_cost=100))
        self.add_skill(Skill("Vergiften", gold_cost=100))
        self.add_skill(Skill("Doppelschlag", gold_cost=100))
        self.add_skill(Skill("Diebeskunst", gold_cost=100))
        self.add_skill(Skill("Meuchelmord", gold_cost=100))

class HeilerSkillsystem(Skillsystem):
    def __init__(self):
        super().__init__()
        self.add_skill(Skill("Heilung", gold_cost=100))
        self.add_skill(Skill("Heiliger Blitz", gold_cost=100))
        self.add_skill(Skill("Manaregeneration", gold_cost=100))
        self.add_skill(Skill("Heiliger Segen", gold_cost=100))
        self.add_skill(Skill("Göttliche Gnade", gold_cost=100))

# Spezialisierungen hinzufügen
class Krieger:
    def __init__(self):
        self.grandskills = [
            Fähigkeit("Schwertkampf", 50, 10, 50),
            Fähigkeit("Schildnutzung", 0, 20, 50),
            Fähigkeit("Berserker-Rage", 70, 25, 50),
            Fähigkeit("Kampfgeschick", 40, 15, 50),
            Fähigkeit("Kriegerstärke", 60, 20, 50)
        ]

class Magier:
    def __init__(self):
        self.grandskills = [
            Fähigkeit("Feuerball", 70, 30, 50),
            Fähigkeit("Eislanze", 50, 25, 50),
            Fähigkeit("Blitzschlag", 60, 30, 50),
            Fähigkeit("Magische Barriere", 40, 20, 50),
            Fähigkeit("Arkane Macht", 80, 40, 50)
        ]

class Schurke:
    def __init__(self):
        self.grandskills = [
            Fähigkeit("Schleichangriff", 60, 15, 50),
            Fähigkeit("Vergiften", 40, 10, 50),
            Fähigkeit("Doppelschlag", 50, 20, 50),
            Fähigkeit("Diebeskunst", 30, 10, 50),
            Fähigkeit("Meuchelmord", 70, 25, 50)
        ]

class Heiler:
    def __init__(self):
        self.grandskills = [
            Fähigkeit("Heilung", 0, 10, 50),
            Fähigkeit("Heiliger Blitz", 100, 15, 50),  # Geändert
            Fähigkeit("Manaregeneration", 0, 25, 50),  # Umbenannt
            Fähigkeit("Heiliger Segen", 0, 20, 50),
            Fähigkeit("Göttliche Gnade", 0, 30, 50)
        ]

    def anwenden_fähigkeit(self, fähigkeit_name: str, spieler: 'Spieler', gegner: Optional['Gegner'] = None):
        for fähigkeit in self.grandskills:
            if fähigkeit.name == fähigkeit_name:
                if fähigkeit.name == "Heilung":
                    geheilte_punkte = 50
                    spieler.lebenspunkte = min(spieler.lebenspunkte + geheilte_punkte, spieler.max_lebenspunkte)
                    print(f"Die Fähigkeit {fähigkeit.name} wurde angewendet. {geheilte_punkte} Lebenspunkte geheilt. Lebenspunkte: {spieler.lebenspunkte}/{spieler.max_lebenspunkte}")
                elif fähigkeit.name == "Heiliger Blitz":
                    if gegner:
                        gegner.lebenspunkte -= fähigkeit.schaden
                        print(f"Die Fähigkeit {fähigkeit.name} wurde angewendet und hat {fähigkeit.schaden} Schaden verursacht. {gegner.name} hat noch {gegner.lebenspunkte} Lebenspunkte.")
                elif fähigkeit.name == "Manaregeneration":
                    geheiltes_mana = 100
                    spieler.mana = min(spieler.mana + geheiltes_mana, spieler.max_mana)
                    print(f"Die Fähigkeit {fähigkeit.name} wurde angewendet. {geheiltes_mana} Mana regeneriert. Mana: {spieler.mana}/{spieler.max_mana}")
                elif fähigkeit.name == "Heiliger Segen":
                    geheilte_punkte = 30
                    spieler.lebenspunkte = min(spieler.lebenspunkte + geheilte_punkte, spieler.max_lebenspunkte)
                    print(f"Die Fähigkeit {fähigkeit.name} wurde angewendet. {geheilte_punkte} Lebenspunkte geheilt. Lebenspunkte: {spieler.lebenspunkte}/{spieler.max_lebenspunkte}")
                elif fähigkeit.name == "Göttliche Gnade":
                    geheilte_punkte = 100
                    spieler.lebenspunkte = min(spieler.lebenspunkte + geheilte_punkte, spieler.max_lebenspunkte)
                    print(f"Die Fähigkeit {fähigkeit.name} wurde angewendet. {geheilte_punkte} Lebenspunkte geheilt. Lebenspunkte: {spieler.lebenspunkte}/{spieler.max_lebenspunkte}")
                else:
                    print(f"Die Fähigkeit {fähigkeit.name} ist keine Heilungsfähigkeit.")
                return
        print(f"Die Fähigkeit {fähigkeit_name} wurde not gefunden.")

@dataclass
class Gegner:
    typ: str
    multiplikator: float
    name: str = field(init=False)
    lebenspunkte: int = field(init=False)
    max_schaden: int = field(init=False)
    kupfer: int = field(init=False)
    silber: int = field(init=False)
    gold: int = field(init=False)
    seltene_gegenstände: List[Gegenstand] = field(default_factory=list)
    benutzbare_gegenstände: List[Gegenstand] = field(default_factory=list)
    resourcen_drop: Dict[str, int] = field(default_factory=dict)
    grandskills: List[Fähigkeit] = field(default_factory=list)
    hat_angriff_durchgefuehrt: bool = field(default=False, init=False)

    def __post_init__(self):
        self.name = generiere_gegnernamen(self.typ)
        self.lebenspunkte = int(LEBENSPUNKTE[self.typ] * self.multiplikator)
        self.max_schaden = int(MAX_SCHADEN[self.typ] * self.multiplikator)
        self.kupfer, self.silber, self.gold = GOLD_BELOHNUNG[self.typ]
        self.drop_seltene_gegenstände()
        self.drop_benutzbare_gegenstände()
        self.drop_resourcen()
        self.initialisiere_grandskills()

    def initialisiere_grandskills(self):
        if self.typ == 'schwach':
            self.grandskills = [
                Fähigkeit("Beinschnitt", 50, 0),
                Fähigkeit("Ducken", 0, 5),
                Fähigkeit("Kratzen", 20, 0),
                Fähigkeit("Ausweichen", 0, 5),
                Fähigkeit("Leichter Tritt", 7, 0),
                Fähigkeit("Schwacher Schlag", 9, 0),
                Fähigkeit("Hinterhalt", 12, 0),
                Fähigkeit("Tarnung", 0, 3),
                Fähigkeit("Schneller Schlag", 6, 0),
                Fähigkeit("Verstecken", 0, 4),
                Fähigkeit("Fintenangriff", 11, 0),
                Fähigkeit("Schattenhieb", 10, 0),
                Fähigkeit("Schleichangriff", 13, 0),
                Fähigkeit("Verwirrung", 0, 6),
                Fähigkeit("Kleiner Hieb", 5, 0),
                Fähigkeit("Klingenwirbel", 9, 0),
                Fähigkeit("Rückzug", 0, 2),
                Fähigkeit("Fehltritt", 8, 0),
                Fähigkeit("Täuschung", 0, 4),
                Fähigkeit("Knieschlag", 7, 0),
                Fähigkeit("Abwehrhaltung", 0, 5)
            ]
        elif self.typ == 'mittel':
            self.grandskills = [
                Fähigkeit("Bruststich", 20, 0),
                Fähigkeit("Schwertverteidigung", 0, 10),
                Fähigkeit("Schmetterschlag", 18, 0),
                Fähigkeit("Parieren", 0, 7),
                Fähigkeit("Hieb", 22, 0),
                Fähigkeit("Block", 0, 8),
                Fähigkeit("Starker Tritt", 15, 0),
                Fähigkeit("Deckung", 0, 9),
                Fähigkeit("Seitenschlag", 19, 0),
                Fähigkeit("Ausweichrolle", 0, 6),
                Fähigkeit("Kraftstoß", 25, 0),
                Fähigkeit("Sturmangriff", 23, 0),
                Fähigkeit("Verteidigungshaltung", 0, 12),
                Fähigkeit("Schildstoß", 20, 0),
                Fähigkeit("Kampfkunst", 0, 8),
                Fähigkeit("Hieb und Stich", 21, 0),
                Fähigkeit("Abwehrschlag", 0, 11),
                Fähigkeit("Schulterwurf", 18, 0),
                Fähigkeit("Taktischer Rückzug", 0, 10),
                Fähigkeit("Schwertwirbel", 24, 0),
                Fähigkeit("Abwehrmanöver", 0, 9)
            ]
        elif self.typ == 'stark':
            self.grandskills = [
                Fähigkeit("Doppelstich", 40, 0),
                Fähigkeit("Schild", 0, 15),
                Fähigkeit("Mächtiger Hieb", 35, 0),
                Fähigkeit("Rüstungsschutz", 0, 12),
                Fähigkeit("Schmetterschlag", 38, 0),
                Fähigkeit("Verteidigungsposition", 0, 14),
                Fähigkeit("Klingensturm", 45, 0),
                Fähigkeit("Schildwall", 0, 16),
                Fähigkeit("Raserei", 50, 0),
                Fähigkeit("Unverwundbarkeit", 0, 18),
                Fähigkeit("Erderschütterer", 42, 0),
                Fähigkeit("Steinhaut", 0, 17),
                Fähigkeit("Kampfeswut", 47, 0),
                Fähigkeit("Magischer Schutz", 0, 20),
                Fähigkeit("Übermacht", 48, 0),
                Fähigkeit("Gegenangriff", 0, 15),
                Fähigkeit("Zertrümmerer", 46, 0),
                Fähigkeit("Eiserner Wille", 0, 16),
                Fähigkeit("Sturmschlag", 44, 0),
                Fähigkeit("Standhaftigkeit", 0, 19),
                Fähigkeit("Tödlicher Stoß", 49, 0),
                Fähigkeit("Schild des Glaubens", 0, 18)
            ]
        elif self.typ == 'boss':
            self.grandskills = [
                Fähigkeit("Spezial Hieb Schlechter", 70, 0),
                Fähigkeit("Riesenschild", 0, 25),
                Fähigkeit("Wutangriff", 60, 0),
                Fähigkeit("Unbezwingbar", 0, 20),
                Fähigkeit("Feueratem", 80, 0),
                Fähigkeit("Mächtige Barriere", 0, 30),
                Fähigkeit("Todeshieb", 75, 0),
                Fähigkeit("Unverwundbar", 0, 35),
                Fähigkeit("Drachenklauen", 65, 0),
                Fähigkeit("Magieschild", 0, 28),
                Fähigkeit("Klingenwirbel", 85, 0),
                Fähigkeit("Titanenhaut", 0, 40),
                Fähigkeit("Donnerschlag", 90, 0),
                Fähigkeit("Götterschutz", 0, 45),
                Fähigkeit("Höllenfeuer", 95, 0),
                Fähigkeit("Unzerstörbar", 0, 50),
                Fähigkeit("Schattenhieb", 88, 0),
                Fähigkeit("Aegis", 0, 38),
                Fähigkeit("Blutsturm", 92, 0),
                Fähigkeit("Felsblock", 0, 32),
                Fähigkeit("Weltenspalter", 100, 0),
                Fähigkeit("Lichtmauer", 0, 42)
            ]


    def anwenden_grandskill(self, spieler: 'Spieler'):
        if not self.hat_angriff_durchgefuehrt and self.grandskills:
            fähigkeit = random.choice(self.grandskills)
            if fähigkeit.schaden > 0:  # Angriffsfähigkeit
                spieler.lebenspunkte -= fähigkeit.schaden
                print(f"{self.name} hat {fähigkeit.name} angewendet und {fähigkeit.schaden} Schaden verursacht.")
            elif fähigkeit.kosten > 0:  # Verteidigungsfähigkeit
                spieler.lebenspunkte = max(spieler.lebenspunkte - fähigkeit.kosten, 0)
                print(f"{self.name} hat {fähigkeit.name} angewendet und seine Verteidigung um {fähigkeit.kosten} erhöht.")
            self.hat_angriff_durchgefuehrt = True

    def drop_resourcen(self) -> None:
        resource_names = ["Holz", "Stein", "Eisen", "Kraut", "Magischer Stein"]
        for res in resource_names:
            if random.random() < 0.25:  # 25% chance to drop each resource
                self.resourcen_drop[res] = random.randint(1, 5)
                print(f"{self.name} hat {self.resourcen_drop[res]} Einheiten {res} gedroppt.")

    def angreifen(self) -> int:
        return random.randint(1, self.max_schaden)


    def drop_seltene_gegenstände(self) -> None:
        if random.random() < SELTENE_DROP_RATE:
            self.seltene_gegenstände.append(Gegenstand(name="Seltenes Artefakt", typ="Verkauf", wert=200))
            print(f"Seltenes Artefakt von {self.name} gedroppt")
        if random.random() < SEHR_SELTENE_DROP_RATE:
            self.seltene_gegenstände.append(Gegenstand(name="Sehr seltenes Artefakt", typ="Verkauf", wert=500))
            print(f"Sehr seltenes Artefakt von {self.name} gedroppt")

    def drop_benutzbare_gegenstände(self) -> None:
        if random.random() < 0.10:  # 10% Chance, einen benutzbaren Gegenstand zu droppen
            benutzbarer_gegenstand = random.choice(BENUTZBARE_GEGENSTAENDE)
            self.benutzbare_gegenstände.append(benutzbarer_gegenstand)
            print(f"Benutzbarer Gegenstand {benutzbarer_gegenstand.name} von {self.name} gedroppt")

        if random.random() < 0.10:  # 10% Chance, eine magische Schriftrolle zu droppen
            magische_schriftrolle = random.choice(MAGISCHE_SCHRIFTROLLEN)
            self.benutzbare_gegenstände.append(magische_schriftrolle)
            print(f"Magische Schriftrolle {magische_schriftrolle.name} von {self.name} gedroppt")
      

@dataclass
class Spieler:
    name: str
    klasse: str
    lebenspunkte: int
    max_lebenspunkte: int
    erfahrung: int
    level: int
    gegenstände: List[Gegenstand]
    fähigkeiten: List[Fähigkeit]
    waffeninventar: List[Waffe] = field(default_factory=list)
    rüstungsinventar: List[Rüstung] = field(default_factory=list)
    waffe: Optional[Waffe] = None
    rüstung: Optional[Rüstung] = None
    handschuhe: Optional[Rüstung] = None
    stiefel: Optional[Rüstung] = None
    helm: Optional[Rüstung] = None
    kupfer: int = START_GOLD[0]
    silber: int = START_GOLD[1]
    gold: int = START_GOLD[2]
    gegner_multiplikator: float = 1.0
    spielfeld: List[Optional[Gegner]] = field(default_factory=list)
    magische_schriftrollen: List[MagischeSchriftrolle] = field(default_factory=list)
    quests: List[Quest] = field(default_factory=list)
    tägliche_herausforderungen: List[Tagesquest] = field(default_factory=list)
    level_system: LevelSystem = field(init=False)
    max_mana: int = SPIELER_MAX_MANA
    mana: int = SPIELER_START_MANA
    manaregeneration_aktiv: bool = False
    manaregeneration_zaehler: int = 0
    vergiftet: bool = False
    skillsystem: Skillsystem = field(init=False)
    spezialisierung: Optional[object] = field(default=None, init=False)
    ressourceninventar: Dict[str, int] = field(default_factory=lambda: {
        "Holz": 10,
        "Stein": 8,
        "Eisen": 5,
        "Kraut": 12,
        "Magischer Stein": 3
    })
    position: int = 0  # Hinzufügen des position-Attributs

    def __post_init__(self):
        self.level_system = LevelSystem(self.erfahrung, self.level)
        self.spielfeld = erstelle_spielfeld(self.gegner_multiplikator)
        self.set_klasse(self.klasse)

    def set_klasse(self, klasse: str):
        if klasse == "Krieger":
            self.skillsystem = KriegerSkillsystem()
            self.spezialisierung = Krieger()
        elif klasse == "Magier":
            self.skillsystem = MagierSkillsystem()
            self.spezialisierung = Magier()
        elif klasse == "Schurke":
            self.skillsystem = SchurkeSkillsystem()
            self.spezialisierung = Schurke()
        elif klasse == "Heiler":
            self.skillsystem = HeilerSkillsystem()
            self.spezialisierung = Heiler()
        else:
            print("Unbekannte Klasse, Standardklasse Krieger wird verwendet.")
            self.skillsystem = KriegerSkillsystem()
            self.spezialisierung = Krieger()
        self.fähigkeiten = self.spezialisierung.grandskills
    
    def wuerfeln_und_bewegen(self) -> None:
        eingabe = input("Drücke Enter, um zu würfeln...")
        if eingabe == '':
            wurf = random.randint(1, 6)
            self.aktuelles_feld += wurf
            if self.aktuelles_feld > 100:
                self.aktuelles_feld = 100
            print(f"Der Spieler würfelt eine {wurf} und bewegt sich auf Feld {self.aktuelles_feld}.")
        

    def add_ressourcen(self, ressource: str, menge: int) -> None:
        if ressource in self.ressourceninventar:
            self.ressourceninventar[ressource] += menge
        else:
            self.ressourceninventar[ressource] = menge
        print(f"Du hast {menge} Einheiten {ressource} erhalten. Insgesamt: {self.ressourceninventar[ressource]}")


    def erfahrung_sammeln(self, xp):
        self.level_system.erfahrung_sammeln(xp, self)

    def skill_level_up(self, skill_name):
        try:
            skill = self.skillsystem.level_up_skill(skill_name, self)
            return skill
        except ValueError as e:
            print(e)

    def skills_anzeigen(self):
        print("\033[34m**** Aktuelle Skills: ****\033[0m")
        self.skillsystem.zeige_skills()
        return self.skill_menue()

    def skill_level_up_menue(self):
        print("\033[34m**** Wähle einen Skill zum Leveln: ****\033[0m")
        for i, skill in enumerate(self.skillsystem.skills):
            print(f"{i + 1}: {skill.name} (Level {skill.level}/{skill.max_level}, Gold-Kosten: {skill.gold_cost})")

        choice = int(input("Wähle einen Skill (Nummer eingeben): "))
        if 1 <= choice <= len(self.skillsystem.skills):
            ausgewählter_skill = self.skillsystem.skills[choice - 1]
            try:
                self.skill_level_up(ausgewählter_skill.name)
            except ValueError as e:
                print(e)
        else:
            print("Ungültige Wahl.")
        return self.skill_menue()

    def skill_menue(self):
        print("\033[34m**** Skill-Menü ****\033[0m")
        print("1: Skills anzeigen")
        print("2: Skill leveln")
        print("3: Zum Hauptmenü zurückkehren")

        choice = input("Wähle eine Option: ")

        if choice == '1':
            self.skills_anzeigen()
        elif choice == '2':
            self.skill_level_up_menue()
        elif choice == '3':
            return zeige_menü(self)
        else:
            print("Ungültige Wahl. Bitte versuche es erneut.")
            return self.skill_menue()

    def quest_fortschritt_aktualisieren(self, ziel_typ: str, menge: int = 1) -> None:
        for quest in self.quests:
            if quest.ziel_typ == ziel_typ and not quest.abgeschlossen:
                quest.fortschritt_aktualisieren(menge)
                print(f"Fortschritt bei Quest {quest.name}: {quest.fortschritt_anzeigen()}")
                if quest.abgeschlossen:
                    self.add_muenzen(*quest.belohnung)
                    print(f"Quest {quest.name} abgeschlossen! Belohnung: {quest.belohnung[0]} Gold, {quest.belohnung[1]} Silber, {quest.belohnung[2]} Kupfer")

        for tagesquest in self.tägliche_herausforderungen:
            if tagesquest.ziel_typ == ziel_typ and not tagesquest.abgeschlossen:
                tagesquest.fortschritt_aktualisieren(menge)
                print(f"Fortschritt bei Tagesquest {tagesquest.name}: {tagesquest.fortschritt_anzeigen()}")
                if tagesquest.abgeschlossen:
                    self.add_muenzen(*tagesquest.belohnung)
                    print(f"Tagesquest {tagesquest.name} abgeschlossen! Belohnung: {tagesquest.belohnung[0]} Gold, {tagesquest.belohnung[1]} Silber, {tagesquest.belohnung[2]} Kupfer")


    def tagesquest_hinzufügen(self, quest: Tagesquest) -> None:
        self.tägliche_herausforderungen.append(quest)
        print(f"Tagesquest hinzugefügt: {quest.name} - {quest.beschreibung}")

    def tagesquests_anzeigen(self) -> None:
        if not self.tägliche_herausforderungen:
            print("Keine Tagesquests verfügbar.")
        else:
            print("\033[34m**** Aktuelle Tagesquests: ****\033[0m")
            for quest in self.tägliche_herausforderungen:
                status = "Abgeschlossen" if quest.abgeschlossen else f"Fortschritt: {quest.fortschritt_anzeigen()}"
                gold, silber, kupfer = quest.belohnung
                print(f"{quest.name}: {quest.beschreibung} - Belohnung: {gold} Gold, {silber} Silber, {kupfer} Kupfer - Status: {status}")

    def inventar_anzeigen(self) -> None:
        print(f"\033[33mName: {self.name}\033[0m")
        print(f"\033[33mKlasse: {self.klasse}\033[0m")
        print(f"\033[33mGold: {self.gold}, Silber: {self.silber}, Kupfer: {self.kupfer}\033[0m")
        print(f"\033[33mLebenspunkte: {self.lebenspunkte}/{self.max_lebenspunkte}\033[0m")
        print(f"\033[33mMana: {self.mana}/{self.max_mana}\033[0m")
        print(f"\033[33mLevel: {self.level}\033[0m")
        print(f"\033[33mErfahrung: {self.erfahrung}\033[0m")
        grundschaden = 55
        print(f"\033[33mGrundschaden: {grundschaden}\033[0m")
        waffen_schaden = getattr(self.waffe, 'schaden', 0) if isinstance(self.waffe, Waffe) else 0
        gesamt_schaden = grundschaden + waffen_schaden
        print(f"\033[33mGesamtschaden: {gesamt_schaden}\033[0m")
        print(f"\033[33mAktuelle Position: {self.position}\033[0m") 
        # Display resources
        print("\033[34m**** Ressourceninventar: ****\033[0m")
        for ressource, menge in self.ressourceninventar.items():
            print(f"{zufallsfarbe()}{ressource}: {menge}\033[0m")
        gegenstand_anzahl = {}
        for gegenstand in self.gegenstände:
            if gegenstand.name in gegenstand_anzahl:
                gegenstand_anzahl[gegenstand.name] += 1
            else:
                gegenstand_anzahl[gegenstand.name] = 1

        if not self.gegenstände:
            print("Dein Inventar ist leer.")
        else:
            print("\033[34m**** Du hast folgende Gegenstände in deinem Inventar: ****\033[0m")
            for name, anzahl in gegenstand_anzahl.items():
                print(f"{zufallsfarbe()}{name} - Anzahl: {anzahl}\033[0m")
        if self.rüstungsinventar:
            print("\033[34m**** Rüstungen im Inventar: ****\033[0m")
            for i, rüstung in enumerate(self.rüstungsinventar, 1):
                print(f"{zufallsfarbe()}{i}: {rüstung.name} - Verteidigung: {rüstung.verteidigung}, Wert: {rüstung.wert} Kupfer\033[0m")
        # Anzeigen des Waffeninventars
        if self.waffeninventar:
            print("\033[34m**** Waffen im Inventar: ****\033[0m")
            for i, waffe in enumerate(self.waffeninventar, 1):
                print(f"{zufallsfarbe()}{i}: {waffe.name} - Schaden: {waffe.schaden}, Wert: {waffe.wert} Kupfer\033[0m")
        # Zeigen der ausgerüsteten Waffen und Rüstungen
        print("\033[34m**** Ausgerüstete Waffen und Rüstungen: ****\033[0m")
        if self.waffe:
            print(f"{zufallsfarbe()}Waffe: {self.waffe.name} - Schaden: {self.waffe.schaden}, Wert: {self.waffe.wert} Kupfer\033[0m")
        if self.rüstung:
            print(f"{zufallsfarbe()}Rüstung: {self.rüstung.name} - Verteidigung: {self.rüstung.verteidigung}, Wert: {self.rüstung.wert} Kupfer\033[0m")
        if self.handschuhe:
            print(f"{zufallsfarbe()}Handschuhe: {self.handschuhe.name} - Verteidigung: {self.handschuhe.verteidigung}, Wert: {self.handschuhe.wert} Kupfer\033[0m")
        if self.stiefel:
            print(f"{zufallsfarbe()}Stiefel: {self.stiefel.name} - Verteidigung: {self.stiefel.verteidigung}, Wert: {self.stiefel.wert} Kupfer\033[0m")
        if self.helm:
            print(f"{zufallsfarbe()}Helm: {self.helm.name} - Verteidigung: {self.helm.verteidigung}, Wert: {self.helm.wert} Kupfer\033[0m")

        if self.fähigkeiten:
            print("\033[34m**** Fähigkeiten: ****\033[0m")
            for fähigkeit in self.fähigkeiten:
                print(f"{zufallsfarbe()}{fähigkeit.name} - Schaden: {fähigkeit.schaden}, Mana-Kosten: {fähigkeit.mana_kosten}\033[0m")

        if self.magische_schriftrollen:
            print("\033[34m**** Magische Schriftrollen: ****\033[0m")
            for schriftrolle in self.magische_schriftrollen:
                print(f"{zufallsfarbe()}{schriftrolle.name} - Schaden: {schriftrolle.schaden}, Mana-Kosten: {schriftrolle.mana_kosten}\033[0m")

        print("1: Waffen ausrüsten")
        print("2: Rüstungen ausrüsten")
        print("3: Zum Hauptmenü zurückkehren")
        choice = input("Wähle eine Option: ")
        if choice == '1':
            self.waffe_ausrüsten()
        elif choice == '2':
            self.rüstung_ausrüsten()

    def waffe_ausrüsten(self):
        if not self.waffeninventar:
            print("Keine Waffen im Inventar.")
            return
        print("\033[34m**** Wähle eine Waffe zum Ausrüsten: ****\033[0m")
        for i, waffe in enumerate(self.waffeninventar, 1):
            print(f"{i}: {waffe.name} - Schaden: {waffe.schaden}, Wert: {waffe.wert} Kupfer")
        choice = int(input("Wähle eine Waffe (Nummer eingeben): "))
        if 1 <= choice <= len(self.waffeninventar):
            neue_waffe = self.waffeninventar.pop(choice - 1)
            if self.waffe:
                self.waffeninventar.append(self.waffe)
            self.waffe = neue_waffe
            print(f"Waffe {self.waffe.name} ausgerüstet.")


    def rüstung_ausrüsten(self):
        if not self.rüstungsinventar:
            print("Keine Rüstungen im Inventar.")
            return
        print("\033[34m**** Wähle eine Rüstung zum Ausrüsten: ****\033[0m")
        for i, rüstung in enumerate(self.rüstungsinventar, 1):
            print(f"{i}: {rüstung.name} - Verteidigung: {rüstung.verteidigung}, Wert: {rüstung.wert} Kupfer")
        choice = int(input("Wähle eine Rüstung (Nummer eingeben): "))
        if 1 <= choice <= len(self.rüstungsinventar):
            ausgewählte_rüstung = self.rüstungsinventar.pop(choice - 1)
            if ausgewählte_rüstung.typ == 'Rüstung':
                if self.rüstung:
                    self.rüstungsinventar.append(self.rüstung)
                self.rüstung = ausgewählte_rüstung
            elif ausgewählte_rüstung.typ == 'Handschuhe':
                if self.handschuhe:
                    self.rüstungsinventar.append(self.handschuhe)
                self.handschuhe = ausgewählte_rüstung
            elif ausgewählte_rüstung.typ == 'Stiefel':
                if self.stiefel:
                    self.rüstungsinventar.append(self.stiefel)
                self.stiefel = ausgewählte_rüstung
            elif ausgewählte_rüstung.typ == 'Helm':
                if self.helm:
                    self.rüstungsinventar.append(self.helm)
                self.helm = ausgewählte_rüstung
            print(f"Rüstung {ausgewählte_rüstung.name} ausgerüstet.")



    def angreifen(self) -> int:
        waffen_schaden = getattr(self.waffe, 'schaden', 0) if isinstance(self.waffe, Waffe) else 0
        grand_schaden = random.randint(1, SPIELER_MAX_SCHADEN)
        skill_schaden = sum(skill.berechne_schaden() for skill in self.skillsystem.skills)
        gesamtschaden = grand_schaden + waffen_schaden + skill_schaden
        zufälliger_schaden = random.randint(grand_schaden, gesamtschaden)
        return zufälliger_schaden

    def verteidigen(self, schaden: int) -> int:
        rüstung_schutz = (self.rüstung.verteidigung if self.rüstung else 0) + \
                         (self.handschuhe.verteidigung if self.handschuhe else 0) + \
                         (self.stiefel.verteidigung if self.stiefel else 0) + \
                         (self.helm.verteidigung if self.helm else 0)
        reduzierter_schaden = max(schaden - rüstung_schutz, 0)
        self.lebenspunkte -= reduzierter_schaden
        return reduzierter_schaden

    def heilen(self) -> None:
        self.lebenspunkte = min(self.lebenspunkte + 30, self.max_lebenspunkte)
        print(f"{zufallsfarbe()}Als Siegesbonus wurden die Lebenspunkte des Spielers um 30 erhöht und sind jetzt {self.lebenspunkte}/{self.max_lebenspunkte}.\033[0m")

    def gegenstand_verwenden(self, gegenstand_name: str) -> None:
        gegenstand = next((g for g in self.gegenstände if g.name == gegenstand_name), None)
        if gegenstand:
            if gegenstand.typ == 'Heiltrank':
                self.lebenspunkte = min(self.lebenspunkte + gegenstand.wert, self.max_lebenspunkte)
                print(f"Du hast {gegenstand.name} verwendet. Lebenspunkte: {self.lebenspunkte}/{self.max_lebenspunkte}")
            elif gegenstand.typ == 'Mana-Trank':
                self.mana = min(self.mana + gegenstand.wert, self.max_mana)
                print(f"Du hast {gegenstand.name} verwendet. Mana: {self.mana}/{self.max_mana}")
            elif gegenstand.typ == 'Gift':
                gegner = random.choice(self.spielfeld)  # Beispiel: Zufälliger Gegner wird vergiftet
                gegner.lebenspunkte -= gegenstand.wert
                print(f"Du hast {gegenstand.name} verwendet. {gegner.name} hat noch {gegner.lebenspunkte} Lebenspunkte.")
            elif gegenstand.typ == 'Antidot':
                self.vergiftet = False
                print(f"Du hast {gegenstand.name} verwendet. Du bist not mehr vergiftet.")
            elif gegenstand.typ == 'Elixier':
                self.lebenspunkte = min(self.lebenspunkte + 50, self.max_lebenspunkte)
                self.mana = min(self.mana + 50, self.max_mana)
                print(f"Du hast {gegenstand.name} verwendet. Lebenspunkte: {self.lebenspunkte}/{self.max_lebenspunkte}, Mana: {self.mana}/{self.max_mana}")
            elif gegenstand.typ == 'Sprengstoff':
                if gegenstand.name == 'Feuerbombe':
                    gegner = random.choice(self.spielfeld)  # Beispiel: Zufälliger Gegner wird getroffen
                    gegner.lebenspunkte -= gegenstand.wert
                    print(f"Du hast {gegenstand.name} verwendet. {gegner.name} hat noch {gegner.lebenspunkte} Lebenspunkte.")
                elif gegenstand.name == 'Rauchbombe':
                    print(f"Du hast {gegenstand.name} verwendet. Deine Fluchtchance ist erhöht.")
                elif gegenstand.name == 'Blendgranate':
                    print(f"Du hast {gegenstand.name} verwendet. Gegner sind geblendet.")
                elif gegenstand.name == 'Frostbombe':
                    gegner = random.choice(self.spielfeld)  # Beispiel: Zufälliger Gegner wird getroffen
                    gegner.lebenspunkte -= gegenstand.wert
                    print(f"Du hast {gegenstand.name} verwendet. {gegner.name} hat noch {gegner.lebenspunkte} Lebenspunkte und ist verlangsamt.")
            elif gegenstand.typ == 'Magischer Gegenstand':
                if gegenstand.name == 'Teleportationsrolle':
                    print(f"Du hast {gegenstand.name} verwendet. Du bist zu einem sicheren Ort teleportiert.")
                elif gegenstand.name == 'Unsichtbarkeitsumhang':
                    print(f"Du hast {gegenstand.name} verwendet. Du bist for eine gewisse Zeit unsichtbar.")
            else:
                print(f"Der Gegenstand {gegenstand.name} kann not verwendet werden.")
            self.gegenstände.remove(gegenstand)
        else:
            print(f"Der Gegenstand {gegenstand_name} ist not in deinem Inventar.")

    def heiltrank_nutzen(self) -> None:
        heiltränke = [g for g in self.gegenstände if g.typ == 'Heiltrank']
        if heiltränke:
            antwort = input("Möchtest du einen Heiltrank verwenden? (j/n): ")
            if antwort.lower() == 'j':
                heiltrank = heiltränke[0]
                self.lebenspunkte = min(self.lebenspunkte + int(heiltrank.wert), self.max_lebenspunkte)  # Wert in int konvertieren
                self.gegenstände.remove(heiltrank)
                print(f"Heiltrank verwendet. Lebenspunkte: {self.lebenspunkte}/{self.max_lebenspunkte}.")
            else:
                print("Heiltrank not verwendet.")
        else:
            print("Keine Heiltränke im Inventar.")

    def mana_trank_nutzen(self) -> None:
        mana_tränke = [g for g in self.gegenstände if g.typ == 'Mana-Trank']
        if mana_tränke:
            antwort = input("Möchtest du einen Mana-Trank verwenden? (j/n): ")
            if antwort.lower() == 'j':
                mana_trank = mana_tränke[0]
                self.mana = min(self.mana + int(mana_trank.wert), self.max_mana)  # Wert in int konvertieren
                self.gegenstände.remove(mana_trank)
                print(f"Mana-Trank verwendet. Mana: {self.mana}/{self.max_mana}.")
            else:
                print("Mana-Trank not verwendet.")
        else:
            print("Keine Mana-Tränke im Inventar.")

    def finde_heiltränke(self) -> None:
        anzahl_gefandene_heiltränke = random.randint(0, 2)
        if anzahl_gefandene_heiltränke > 0:
            for _ in range(anzahl_gefandene_heiltränke):
                heiltrank = Gegenstand('Heiltrank', 'Heiltrank', 20)
                self.add_gegenstand(heiltrank)
            print(f"Du hast {anzahl_gefandene_heiltränke} Heiltrank{'e' if anzahl_gefandene_heiltränke > 1 else ''} gefunden und deinem Inventar hinzugefügt.")
        else:
            print(f"{zufallsfarbe()}Keine Heiltränke gefunden.\033[0m")

    def finde_mana_tränke(self) -> None:
        anzahl_gefandene_mana_tränke = random.randint(0, 2)
        if anzahl_gefandene_mana_tränke > 0:
            for _ in range(anzahl_gefandene_mana_tränke):
                mana_trank = Gegenstand('Mana-Trank', 'Mana-Trank', 20)
                self.add_gegenstand(mana_trank)
            print(f"Du hast {anzahl_gefandene_mana_tränke} Mana-Trank{'e' if anzahl_gefandene_mana_tränke > 1 else ''} gefunden und deinem Inventar hinzugefügt.")
        else:
            print(f"{zufallsfarbe()}Keine Mana-Tränke gefunden.\033[0m")

    def add_gegenstand(self, gegenstand: Gegenstand) -> None:
        if isinstance(gegenstand, Waffe):
            self.waffeninventar.append(gegenstand)
        elif isinstance(gegenstand, Rüstung):
            self.rüstungsinventar.append(gegenstand)
        else:
            self.gegenstände.append(gegenstand)
            print(f"{zufallsfarbe()}{gegenstand.name} wurde dem Inventar hinzugefügt.\033[0m")

    def add_fähigkeit(self, fähigkeit: Fähigkeit) -> None:
        self.fähigkeiten.append(fähigkeit)
        print(f"Fähigkeit {fähigkeit.name} wurde erlernt.")

    def add_magische_schriftrolle(self, schriftrolle: MagischeSchriftrolle) -> None:
        if len(self.magische_schriftrollen) < 2:
            self.magische_schriftrollen.append(schriftrolle)
            print(f"Magische Schriftrolle {schriftrolle.name} wurde erlernt.")
        else:
            print("Du kannst nur 2 magische Schriftrollen erlernen.")

    def quest_abschließen(self, quest_name: str) -> None:
        for quest in self.quests:
            if quest.name == quest_name and quest.abgeschlossen:
                self.add_muenzen(*quest.belohnung)
                print(f"Quest {quest.name} abgeschlossen! Belohnung: {quest.belohnung[0]} Kupfer, {quest.belohnung[1]} Silber, {quest.belohnung[2]} Gold")
                self.quests.remove(quest)
                return
        print(f"Quest {quest_name} konnte nicht abgeschlossen werden, entweder existiert sie nicht oder ist noch nicht abgeschlossen.")


    def schriftrolle_auswählen(self) -> Optional[MagischeSchriftrolle]:
        if not self.magische_schriftrollen:
            print("Keine magischen Schriftrollen verfügbar.")
            return None
        print("\033[34m**** Verfügbare magische Schriftrollen: ****\033[0m")
        for i, schriftrolle in enumerate(self.magische_schriftrollen):
            print(f"{i + 1}: {schriftrolle.name} - Schaden: {schriftrolle.schaden}, Mana-Kosten: {schriftrolle.mana_kosten}")
        wahl = int(input("Wähle eine magische Schriftrolle (Nummer eingeben): "))
        if 1 <= wahl <= len(self.magische_schriftrollen):
            ausgewählte_schriftrolle = self.magische_schriftrollen[wahl - 1]
            if self.mana >= ausgewählte_schriftrolle.mana_kosten:
                return ausgewählte_schriftrolle
            else:
                print("not genügend Mana.")
                return None
        else:
            print("Ungültige Wahl.")
            return None

    def schriftrolle_verwenden(self, schriftrolle: MagischeSchriftrolle, gegner: Gegner) -> None:
        gegner.lebenspunkte -= schriftrolle.schaden
        self.mana -= schriftrolle.mana_kosten
        print(f"Magische Schriftrolle {schriftrolle.name} verwendet und {schriftrolle.schaden} Schaden verursacht. {gegner.name} hat noch {gegner.lebenspunkte} Lebenspunkte.")

    def erfahrung_sammeln(self, punkte: int) -> None:
        self.level_system.erfahrung_sammeln(punkte, self)
        self.quest_fortschritt_aktualisieren('erfahrung', punkte)
        if self.level_system.level > self.level:
            self.level = self.level_system.level
            self.quest_fortschritt_aktualisieren('level', self.level)

    def quest_hinzufügen(self, quest: Quest) -> None:
        self.quests.append(quest)
        print(f"\033[34mQuest {quest.name} wurde hinzugefügt: {quest.beschreibung}\033[0m")

    def tägliche_herausforderung_abschließen(self, herausforderung: Tagesquest) -> None:
        self.add_muenzen(*herausforderung.belohnung)
        print(f"Tägliche Herausforderung abgeschlossen! Belohnung: {herausforderung.belohnung} Kupfer, Silber und Gold")
        self.tägliche_herausforderungen.remove(herausforderung)

    def add_muenzen(self, kupfer: int, silber: int, gold: int) -> None:
        self.kupfer += kupfer
        self.silber += silber
        self.gold += gold
        while self.kupfer >= 100:
            self.kupfer -= 100
            self.silber += 1
        while self.silber >= 100:
            self.silber -= 100
            self.gold += 1

    def remove_muenzen(self, kupfer: int = 0, silber: int = 0, gold: int = 0) -> None:
        total_kupfer = self.kupfer + self.silber * 100 + self.gold * 10000
        kosten_kupfer = kupfer + silber * 100 + gold * 10000

        if kosten_kupfer > total_kupfer:
            print("not genügend Kupfer, Silber oder Gold.")
            return

        total_kupfer -= kosten_kupfer

        self.gold = total_kupfer // 10000
        self.silber = (total_kupfer % 10000) // 100
        self.kupfer = total_kupfer % 100

    def fähigkeit_auswählen(self) -> Optional[Fähigkeit]:
        if not self.fähigkeiten:
            print("Keine Fähigkeiten verfügbar.")
            return None
        print("\033[34m**** Verfügbare Fähigkeiten: ****\033[0m")
        for i, fähigkeit in enumerate(self.fähigkeiten):
            print(f"{i + 1}: {fähigkeit.name} - Schaden: {fähigkeit.schaden}, Mana-Kosten: {fähigkeit.mana_kosten}")
        wahl = int(input("Wähle eine Fähigkeit (Nummer eingeben): "))
        if 1 <= wahl <= len(self.fähigkeiten):
            ausgewählte_fähigkeit = self.fähigkeiten[wahl - 1]
            if self.mana >= ausgewählte_fähigkeit.mana_kosten:
                return ausgewählte_fähigkeit
            else:
                print("not genügend Mana.")
                return None
        else:
            print("Ungültige Wahl.")
            return None

    def anwenden_fähigkeit(self, fähigkeit_name: str):
        if isinstance(self.spezialisierung, Heiler):
            self.spezialisierung.anwenden_fähigkeit(fähigkeit_name, self)
        else:
            fähigkeit = next((f for f in self.fähigkeiten if f.name == fähigkeit_name), None)
            if fähigkeit:
                if fähigkeit.schaden > 0:
                    gegner = random.choice([gegner for gegner in self.spielfeld if gegner is not None])
                    gegner.lebenspunkte -= fähigkeit.schaden
                    self.mana -= fähigkeit.mana_kosten
                    print(f"Die Fähigkeit {fähigkeit.name} wurde angewendet und hat {fähigkeit.schaden} Schaden verursacht. {gegner.name} hat noch {gegner.lebenspunkte} Lebenspunkte.")
                else:
                    geheilte_punkte = 30  # Beispielwert for Heilung
                    self.lebenspunkte = min(self.lebenspunkte + geheilte_punkte, self.max_lebenspunkte)
                    self.mana -= fähigkeit.mana_kosten
                    print(f"Die Fähigkeit {fähigkeit.name} wurde angewendet. {geheilte_punkte} Lebenspunkte geheilt. Lebenspunkte: {self.lebenspunkte}/{self.max_lebenspunkte}")

    def angriff_verarbeiten(self):
        if self.manaregeneration_aktiv:
            self.mana = min(self.mana + 20, self.max_mana)
            self.manaregeneration_zaehler -= 1
            if self.manaregeneration_zaehler <= 0:
                self.manaregeneration_aktiv = False
                print("Die Manaregeneration ist not mehr aktiv.")

# Add these functions near the top of your script, after the class definitions
def zeige_gelernte_schriftrollen(spieler: Spieler):
    if not spieler.magische_schriftrollen:
        print("Keine magischen Schriftrollen gelernt.")
        return
    print("\033[34m**** Gelernte magische Schriftrollen: ****\033[0m")
    for i, schriftrolle in enumerate(spieler.magische_schriftrollen):
        print(f"{i + 1}: {schriftrolle.name} - Schaden: {schriftrolle.schaden}, Mana-Kosten: {schriftrolle.mana_kosten}")

def vergessen_schriftrolle(spieler: Spieler):
    zeige_gelernte_schriftrollen(spieler)
    try:
        choice = int(input("Wähle eine zu vergessende Schriftrolle (Nummer eingeben) oder 0, um zurückzukehren: "))
        if choice == 0:
            return
        elif 1 <= choice <= len(spieler.magische_schriftrollen):
            vergessene_schriftrolle = spieler.magische_schriftrollen.pop(choice - 1)
            print(f"Du hast die magische Schriftrolle {vergessene_schriftrolle.name} vergessen.")
        else:
            print("Ungültige Wahl. Bitte wähle eine gültige Nummer.")
    except ValueError:
        print("Ungültige Eingabe. Bitte gib eine Zahl ein.")

def int_schriftrolle_erlernen(spieler: Spieler) -> None:
    print("\033[34m**** Verfügbare magische Schriftrollen: ****\033[0m")
    for i, schriftrolle in enumerate(MAGISCHE_SCHRIFTROLLEN):
        print(f"{i + 1}: {schriftrolle.name} - Schaden: {schriftrolle.schaden}, Mana-Kosten: {schriftrolle.mana_kosten}")
    try:
        choice = int(input("Wähle eine magische Schriftrolle (Nummer eingeben) oder 0, um zurückzukehren: "))
        if choice == 0:
            return
        elif 1 <= choice <= len(MAGISCHE_SCHRIFTROLLEN):
            schriftrolle = MAGISCHE_SCHRIFTROLLEN[choice - 1]
            if schriftrolle.typ == "Schriftrolle":
                spieler.magische_schriftrollen.append(schriftrolle)
                print(f"Du hast die magische Schriftrolle {schriftrolle.name} erlernt.")
            else:
                print("Du kannst diese Schriftrolle nicht erlernen.")
        else:
            print("Ungültige Wahl. Bitte wähle eine gültige Nummer.")
    except ValueError:
        print("Ungültige Eingabe. Bitte gib eine Zahl ein.")

def magische_schriftrolle_erlernen(spieler: Spieler) -> None:
    while True:
        print("\033[34m**** Magische Schriftrollen-Menü ****\033[0m")
        print("1: Gelernte Schriftrollen anzeigen")
        print("2: Neue Schriftrolle erlernen")
        print("3: Gelernte Schriftrolle vergessen")
        print("0: Zurückkehren")

        try:
            choice = int(input("Wähle eine Option (Nummer eingeben): "))
            if choice == 0:
                return
            elif choice == 1:
                zeige_gelernte_schriftrollen(spieler)
            elif choice == 2:
                if len(spieler.magische_schriftrollen) >= 2:
                    print("Du kannst nicht mehr als 2 magische Schriftrollen gleichzeitig erlernen.")
                else:
                    int_schriftrolle_erlernen(spieler)
            elif choice == 3:
                vergessen_schriftrolle(spieler)
            else:
                print("Ungültige Wahl. Bitte wähle eine gültige Nummer.")
        except ValueError:
            print("Ungültige Eingabe. Bitte gib eine Zahl ein.")


def speichere_spielerdaten(spieler: Spieler) -> None:
    spieler_data = {
        "name": spieler.name,
        "klasse": spieler.klasse,
        "lebenspunkte": spieler.lebenspunkte,
        "max_lebenspunkte": spieler.max_lebenspunkte,
        "erfahrung": spieler.erfahrung,
        "level": spieler.level,
        "kupfer": spieler.kupfer,
        "silber": spieler.silber,
        "gold": spieler.gold,
        "mana": spieler.mana,
        "max_mana": spieler.max_mana,
        "waffeninventar": [(waffe.name, waffe.schaden, waffe.wert, waffe.typ) for waffe in spieler.waffeninventar],
        "rüstungsinventar": [(rüstung.name, rüstung.verteidigung, rüstung.wert, rüstung.typ) for rüstung in spieler.rüstungsinventar],
        "gegenstände": [(gegenstand.name, gegenstand.typ, getattr(gegenstand, 'wert', 0)) for gegenstand in spieler.gegenstände],
        "fähigkeiten": [(fähigkeit.name, fähigkeit.schaden, fähigkeit.mana_kosten, fähigkeit.kosten) for fähigkeit in spieler.fähigkeiten],
        "magische_schriftrollen": [(schriftrolle.name, schriftrolle.schaden, schriftrolle.mana_kosten, schriftrolle.typ, schriftrolle.wert, schriftrolle.kosten, schriftrolle.zauberart) for schriftrolle in spieler.magische_schriftrollen],
        "ressourceninventar": spieler.ressourceninventar,
        "quests": [(quest.name, quest.beschreibung, quest.belohnung, quest.ziel_typ, quest.ziel_menge) for quest in spieler.quests],
        "tägliche_herausforderungen": [(tagesquest.name, tagesquest.beschreibung, tagesquest.belohnung, tagesquest.ziel_typ, tagesquest.ziel_menge) for tagesquest in spieler.tägliche_herausforderungen],
        "position": spieler.position  # Hinzugefügt
    }

    with open(f"{spieler.name}_data.json", "w") as file:
        json.dump(spieler_data, file)
    print("Das Spiel wurde gespeichert!")

def lade_spielerdaten(name: str) -> Optional[Spieler]:
    try:
        with open(f"{name}_data.json", "r") as file:
            spieler_data = json.load(file)

        spieler = Spieler(
            name=spieler_data["name"],
            klasse=spieler_data["klasse"],
            lebenspunkte=spieler_data["lebenspunkte"],
            max_lebenspunkte=spieler_data["max_lebenspunkte"],
            erfahrung=spieler_data["erfahrung"],
            level=spieler_data["level"],
            gegenstände=[],
            fähigkeiten=[],
            kupfer=spieler_data["kupfer"],
            silber=spieler_data["silber"],
            gold=spieler_data["gold"],
            mana=spieler_data["mana"],
            max_mana=spieler_data["max_mana"]
        )

        spieler.waffeninventar = [Waffe(name=w[0], schaden=w[1], wert=w[2], typ=w[3]) for w in spieler_data["waffeninventar"]]
        spieler.rüstungsinventar = [Rüstung(name=r[0], verteidigung=r[1], wert=r[2], typ=r[3]) for r in spieler_data["rüstungsinventar"]]
        spieler.gegenstände = [Gegenstand(name=g[0], typ=g[1], wert=g[2]) for g in spieler_data["gegenstände"]]
        spieler.fähigkeiten = [Fähigkeit(name=f[0], schaden=f[1], mana_kosten=f[2], kosten=f[3]) for f in spieler_data["fähigkeiten"]]
        spieler.magische_schriftrollen = [MagischeSchriftrolle(name=ms[0], schaden=ms[1], mana_kosten=ms[2], typ=ms[3], wert=ms[4], kosten=ms[5], zauberart=ms[6]) for ms in spieler_data["magische_schriftrollen"]]
        spieler.ressourceninventar = spieler_data["ressourceninventar"]
        spieler.quests = [Quest(name=q[0], beschreibung=q[1], belohnung=q[2], ziel_typ=q[3], ziel_menge=q[4]) for q in spieler_data["quests"]]
        spieler.tägliche_herausforderungen = [Tagesquest(name=tq[0], beschreibung=tq[1], belohnung=tq[2], ziel_typ=tq[3], ziel_menge=tq[4]) for tq in spieler_data["tägliche_herausforderungen"]]
        spieler.position = spieler_data["position"] 
        print(f"{spieler.name} wurde geladen.")
        return spieler

    except FileNotFoundError:
        print("Keine gespeicherten Daten gefunden. Starte ein neues Spiel.")
        return None





def erstelle_spielfeld(multiplikator: float = 1.0) -> List[Optional[Gegner]]:
    spielfeld = [None] * SPIELFELD_GROESSE
    verfügbare_positionen = list(range(SPIELFELD_GROESSE))

    for typ in GEGNER_TYPEN:
        for _ in range(ANZAHL_GEGNER_PRO_TYP):
            if not verfügbare_positionen:
                position = 1
            else:
                position = random.choice(verfügbare_positionen)
            if position in verfügbare_positionen:
                verfügbare_positionen.remove(position)
            spielfeld[position] = Gegner(typ, multiplikator)

    for _ in range(ANZAHL_BOSSE):
        if not verfügbare_positionen:
            position = 1
        else:
            position = random.choice(verfügbare_positionen)
        if position in verfügbare_positionen:
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


import random


def kampf_einleitung(gegner: Gegner) -> None:
    # Allgemeine Warnung
    einleitungen = {
        'schwach': f"\033[31mAchtung! Du bist auf einen {gegner.name} gestoßen. Bereite dich auf einen Kampf vor!\033[0m",
        'mittel': f"\033[31mVorsicht! Ein wilder {gegner.name} kreuzt deinen Weg. Zeige ihm deine Stärke!\033[0m",
        'stark': f"\033[31mEin mächtiger {gegner.name} erscheint! Dies wird eine wahre Herausforderung!\033[0m",
        'boss': f"\033[31mEin epischer Kampf steht bevor! Der {gegner.name} fordert dich heraus!\033[0m"
    }

    # Detaillierte Einführungsgeschichte
    einleitungen_geschichte = {
    'schwach': [
        "Ein kleiner, aber gefährlicher {name} steht dir im Weg. Bereite dich auf den Kampf vor!",
        "Ein {name} kreuzt deinen Weg und schaut dich feindselig an. Zeit für einen Kampf!",
        "Ein {name} springt aus dem Gebüsch und greift an. Sei auf der Hut!",
        "Plötzlich springt ein kleiner, aber gefährlicher {name} aus dem Unterholz und blockiert deinen Weg. Seine Augen glühen rot vor Bosheit. 'Ein kleiner, aber gefährlicher Kobold steht dir im Weg. Bereite dich auf den Kampf vor!', rufst du aus, während du dein Schwert ziehst."
    ],
    'mittel': [
        "Ein bedrohlicher {name} nähert sich. Du spürst die Gefahr in der Luft.",
        "Ein {name} steht vor dir, bereit für einen Kampf. Zeige, was du kannst!",
        "Ein {name} erscheint und fordert dich heraus. Zeige deine Stärke!",
        "Kaum hast du den {name} besiegt, da spürst du eine bedrohlichere Präsenz. Ein riesiger {name} tritt aus dem Schatten, seine Muskeln spielen unter der zerlumpten Rüstung. 'Ein bedrohlicher {name} nähert sich. Du spürst die Gefahr in der Luft.', denkst du, während du dich in Kampfstellung bringst."
    ],
    'stark': [
        "Ein mächtiger {name} erhebt sich vor dir. Dies wird eine echte Herausforderung.",
        "Ein {name} kommt auf dich zu, seine Augen funkeln vor Kampfeslust. Bereite dich vor!",
        "Ein {name} stellt sich dir in den Weg. Dies wird kein einfacher Kampf.",
        "Der {name} fällt mit einem Grollen, doch die Erde bebt weiter. Ein {name}, dessen Schuppen im Mondlicht schimmern, landet vor dir. Sein Brüllen erschüttert die Nacht. 'Ein mächtiger Drache erhebt sich vor dir. Dies wird eine echte Herausforderung.', flüsterst du."
    ],
    'boss': [
        "Ein epischer Kampf steht bevor! Der {name} fordert dich heraus.",
        "Der {name} erscheint, seine Macht ist überwältigend. Nur die Stärksten überleben diesen Kampf.",
        "Ein {name} brüllt herausfordernd. Dies ist der Moment, den Helden fürchten.",
        "Mit einem letzten, kraftvollen Schrei fordert der {name} dich zum ultimativen Kampf heraus. 'Ein epischer Kampf steht bevor! Der mächtige {name} fordert dich heraus.', rufst du, während das Feuer deiner Entschlossenheit in deinen Augen lodert."
    ]
}


    # Ausgabe der allgemeinen Warnung
    if gegner.typ in einleitungen:
        print(einleitungen[gegner.typ])

    # Ausgabe der detaillierten Einführungsgeschichte
    if gegner.typ in einleitungen_geschichte:
        einleitung = random.choice(einleitungen_geschichte[gegner.typ]).format(name=gegner.name)
        print(f"\033[31m{einleitung}\033[0m")
                                                                                

  
def kampf(spieler: Spieler, gegner: Gegner) -> None:
    kampf_einleitung(gegner)
    print("\033[31m******\033[0m")
    while spieler.lebenspunkte > 0 and gegner.lebenspunkte > 0:
        print("\033[34m**** Kampfmenü ****\033[0m")
        print("1: Angriff")
        print("2: Fähigkeit verwenden")
        print("3: Magische Schriftrolle verwenden")
        print("4: Heiltrank verwenden")
        print("5: Mana-Trank verwenden")
        print("6: Kampf abbrechen und ins Hauptmenü zurückkehren")

        choice = input("Wähle eine Option: ")

        if choice == '1':
            schaden = spieler.angreifen()
            spieler.angriff_verarbeiten()  # Verarbeite Manaregeneration nach dem Angriff
            gegner.lebenspunkte -= schaden
            print(f"\033[32mDu verursachst {schaden} Schaden. {gegner.name} hat noch {gegner.lebenspunkte} Lebenspunkte.\033[0m")
        elif choice == '2':
            fähigkeit = spieler.fähigkeit_auswählen()
            if fähigkeit:
                if fähigkeit.schaden > 0:
                    gegner.lebenspunkte -= fähigkeit.schaden
                    print(f"\033[35mFähigkeit {fähigkeit.name} verwendet und {fähigkeit.schaden} Schaden verursacht. {gegner.name} hat noch {gegner.lebenspunkte} Lebenspunkte.\033[0m")
                else:
                    geheilte_punkte = 30  # Beispielwert für Heilung
                    spieler.lebenspunkte = min(spieler.lebenspunkte + geheilte_punkte, spieler.max_lebenspunkte)
                    print(f"\033[35mFähigkeit {fähigkeit.name} verwendet. {geheilte_punkte} Lebenspunkte geheilt. Lebenspunkte: {spieler.lebenspunkte}/{spieler.max_lebenspunkte}.\033[0m")
                spieler.mana -= fähigkeit.mana_kosten
        elif choice == '3':
            schriftrolle = spieler.schriftrolle_auswählen()
            if schriftrolle:
                spieler.schriftrolle_verwenden(schriftrolle, gegner)
        elif choice == '4':
            spieler.heiltrank_nutzen()
        elif choice == '5':
            spieler.mana_trank_nutzen()
        elif choice == '6':
            print("Du hast den Kampf abgebrochen und kehrst ins Hauptmenü zurück.")
            return zeige_menü(spieler)
        else:
            print("Ungültige Wahl. Bitte wähle eine Option aus dem Menü.")
        # Gegner führt einmal pro Kampf einen Angriff durch
        if not gegner.hat_angriff_durchgefuehrt:
            gegner.anwenden_grandskill(spieler)

        if gegner.lebenspunkte <= 0:
            print(f"\033[32m{gegner.name} wurde besiegt!\033[0m")
            spieler.add_muenzen(gegner.kupfer, gegner.silber, gegner.gold)
            print(f"\033[33mDu hast {gegner.kupfer} Kupfer, {gegner.silber} Silber und {gegner.gold} Gold erhalten.\033[0m")
            if gegner.seltene_gegenstände:
                for gegenstand in gegner.seltene_gegenstände:
                    farbe = random.choice(["\033[31m", "\033[32m", "\033[33m", "\033[34m", "\033[35m", "\033[36m"])
                    print(f"{farbe}Du hast einen seltenen Gegenstand gefunden: {gegenstand.name} - Wert: {gegenstand.wert} Kupfer\033[0m")
                    spieler.add_gegenstand(gegenstand)
            if gegner.benutzbare_gegenstände:
                for gegenstand in gegner.benutzbare_gegenstände:
                    farbe = random.choice(["\033[31m", "\033[32m", "\033[33m", "\033[34m", "\033[35m", "\033[36m"])
                    print(f"{farbe}Du hast einen benutzbaren Gegenstand gefunden: {gegenstand.name} - Wert: {gegenstand.wert if hasattr(gegenstand, 'wert') else 'N/A'} Kupfer\033[0m")
                    spieler.add_gegenstand(gegenstand)
            # Drop a random magical scroll
            if random.random() < 0.1:  # 10% Chance, eine magische Schriftrolle zu droppen
                magische_schriftrolle = random.choice(MAGISCHE_SCHRIFTROLLEN)
                print(f"\033[35mDu hast eine magische Schriftrolle gefunden: {magische_schriftrolle.name} - Schaden: {magische_schriftrolle.schaden}, Mana-Kosten: {magische_schriftrolle.mana_kosten}\033[0m")
                spieler.add_magische_schriftrolle(magische_schriftrolle)
            # Drop resources
            if gegner.resourcen_drop:
                for ressource, menge in gegner.resourcen_drop.items():
                    print(f"\033[33mDu hast {menge} Einheiten {ressource} erhalten.\033[0m")
                    spieler.add_ressourcen(ressource, menge)
            spieler.erfahrung_sammeln(50)
            if spieler.level_system.level > spieler.level:
                spieler.level = spieler.level_system.level
                print(f"\033[32m{spieler.name} ist jetzt Level {spieler.level}!\033[0m")
            spieler.heilen()
            spieler.finde_heiltränke()
            spieler.finde_mana_tränke()
            spieler.quest_fortschritt_aktualisieren('gegner', 1)
            speichere_spielerdaten(spieler)
            print(f"\033[32mAls Siegesbonus wurden die Lebenspunkte des Spielers um 30 erhöht und sind jetzt {spieler.lebenspunkte}/{spieler.max_lebenspunkte}.\033[0m")
            return

        gegner_schaden = gegner.angreifen()
        reduzierter_schaden = spieler.verteidigen(gegner_schaden)
        if spieler.lebenspunkte <= 0:
            print(f"\033[31m{gegner.name} verursacht {gegner_schaden} Schaden. Der Spieler wurde besiegt.\033[0m")
            break
        else:
            print(f"\033[31m{gegner.name} verursacht {gegner_schaden} Schaden. Nach Verteidigung hat der Spieler noch {spieler.lebenspunkte} Lebenspunkte.\033[0m")
            spieler.heiltrank_nutzen()
    print("\033[31m******\033[0m")









def zauber_wirken(spieler: Spieler) -> None:
    zauber = spieler.schriftrolle_auswählen()
    if zauber:
        gegner = Gegner('mittel', 1.0)  # Beispielgegner
        spieler.schriftrolle_verwenden(zauber, gegner)

def quests_anzeigen(spieler: Spieler) -> None:
    if not spieler.quests:
        print("Keine Quests verfügbar.")
    else:
        print("Aktuelle Quests:")
        for i, quest in enumerate(spieler.quests):
            status = "Abgeschlossen" if quest.abgeschlossen else f"Fortschritt: {quest.fortschritt_anzeigen()}"
            print(f"{i + 1}: {quest.name} - {quest.beschreibung} - Belohnung: {quest.belohnung} - Status: {status}")

        while True:
            choice = input("Wähle die Nummer der Quest, die du abschließen möchtest (oder 0, um ins Hauptmenü zurückzukehren): ")
            if choice.isdigit():
                choice = int(choice)
                break
            else:
                print("Ungültige Eingabe. Bitte eine Zahl eingeben.")

        if 1 <= choice <= len(spieler.quests):
            ausgewählte_quest = spieler.quests[choice - 1]
            if ausgewählte_quest.abgeschlossen:
                spieler.quest_abschließen(ausgewählte_quest.name)
                return zeige_menü(spieler)
            else:
                print(f"Die Quest {ausgewählte_quest.name} ist noch not abgeschlossen.")
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
    if random.random() < 0.1:  # 20% Chance, einen NPC zu treffen
        npc_name = random.choice(["Gandalf", "Aragorn", "Legolas", "Gimli"])
        quest_name = f"{npc_name}s Quest"
        quest_beschreibung = f"Hilf {npc_name}, die Dunkelheit zu vertreiben."
        quest_belohnung = (random.randint(50, 100), random.randint(5, 10), random.randint(0, 2))  # Kupfer, Silber, Gold
        npc = NPC(npc_name, Quest(quest_name, quest_beschreibung, quest_belohnung, 'gegner', random.randint(1, 5)))

        print(f"\033[35mDu triffst {npc.name}. Er bietet dir eine Quest an: {npc.quest.name} - {npc.quest.beschreibung} - Belohnung: {npc.quest.belohnung[0]} Kupfer, {npc.quest.belohnung[1]} Silber and {npc.quest.belohnung[2]} Gold\033[0m")
        accept = input("Möchtest du die Quest annehmen? (j/n): ")
        if accept.lower() == 'j':
            spieler.quest_hinzufügen(npc.quest)
        else:
            print("Quest abgelehnt.")

def händler_besuchen(spieler: Spieler) -> None:
    angebote = [
        Waffe(name="Schwert", typ="Waffe", wert=50, schaden=10),
        Waffe(name="Axt", typ="Waffe", wert=70, schaden=15),
        Rüstung(name="Lederpanzer", typ="Rüstung", wert=60, verteidigung=5),
        Rüstung(name="Kettenhemd", typ="Rüstung", wert=100, verteidigung=10),
        Rüstung(name="Samtrobe", typ="Rüstung", wert=70, verteidigung=7),
        Gegenstand(name="Heiltrank", typ="Heiltrank", wert=20),
        Gegenstand(name="Mana-Trank", typ="Mana-Trank", wert=30),
        Gegenstand(name="Gift", typ="Trank", wert=90),
        Gegenstand(name="Antidot", typ="Trank", wert=40),
        Gegenstand(name="Elixier", typ="Trank", wert=120),
        Gegenstand(name="Feuerbombe", typ="Sprengstoff", wert=150),
        Gegenstand(name="Rauchbombe", typ="Sprengstoff", wert=50),
        Gegenstand(name="Blendgranate", typ="Sprengstoff", wert=70),
        Gegenstand(name="Frostbombe", typ="Sprengstoff", wert=150),
        Gegenstand(name="Teleportationsrolle", typ="Magischer Gegenstand", wert=200),
        Gegenstand(name="Unsichtbarkeitsumhang", typ="Magischer Gegenstand", wert=250)
    ]

    print("\033[34m**** Willkommen beim Händler! Hier sind die verfügbaren Gegenstände: ****\033[0m")
    for i, angebot in enumerate(angebote):
        print(f"{i + 1}: {angebot.name} - Typ: {angebot.typ}, Wert: {angebot.wert} Kupfer")

    print(f"{len(angebote) + 1}: Einzelne Gegenstände verkaufen")
    print(f"{len(angebote) + 2}: Alle Gegenstände verkaufen")
    print(f"{len(angebote) + 3}: Zum Hauptmenü zurückkehren")
    while True:
        choice = input("Wähle die Nummer des Gegenstands, den du kaufen oder verkaufen möchtest (oder 0, um abzubrechen): ")
        if not choice.isdigit():
            print("Bitte eine gültige Zahl eingeben.")
            continue
        choice = int(choice)
        if choice == 0:
            return
        elif 1 <= choice <= len(angebote):
            auswahl = angebote[choice - 1]
            if spieler.kupfer + spieler.silber * 100 + spieler.gold * 10000 >= auswahl.wert:
                spieler.remove_muenzen(auswahl.wert)
                if isinstance(auswahl, Waffe):
                    spieler.waffe = auswahl
                elif isinstance(auswahl, Rüstung):
                    spieler.rüstung = auswahl
                else:
                    spieler.add_gegenstand(auswahl)
                print(f"Du hast {auswahl.name} gekauft.")
            else:
                print("Du hast nicht genug Kupfer, Silber oder Gold.")
        elif choice == len(angebote) + 1:
            verkaufe_gegenstände(spieler)
        elif choice == len(angebote) + 2:
            verkaufe_alle_gegenstände(spieler)
        elif choice == len(angebote) + 3:
            return zeige_menü(spieler)
        else:
            print("Ungültige Wahl. Bitte versuche es erneut.")

def verkaufe_alle_gegenstände(spieler: Spieler) -> None:
    if not spieler.gegenstände:
        print("Keine Gegenstände zum Verkauf.")
        return zeige_menü(spieler)

    gesamt_wert = sum(gegenstand.wert for gegenstand in spieler.gegenstände)
    spieler.kupfer += int(gesamt_wert)  # Wert in int konvertieren

    # Umwandlung von Kupfer in Silber und Gold
    while spieler.kupfer >= 100:
        spieler.kupfer -= 100
        spieler.silber += 1
    while spieler.silber >= 100:
        spieler.silber -= 100
        spieler.gold += 1

    print(f"Du hast alle Gegenstände für {gesamt_wert} Kupfer verkauft.")
    spieler.gegenstände.clear()
    return zeige_menü(spieler)



def verkaufe_gegenstände(spieler: Spieler) -> None:
    if not spieler.gegenstände:
        print("Keine Gegenstände zum Verkauf.")
        return zeige_menü(spieler)

    print("Gegenstände in deinem Inventar:")
    for i, gegenstand in enumerate(spieler.gegenstände, 1):
        print(f"{i}: {gegenstand.name} - Typ: {gegenstand.typ}, Wert: {gegenstand.wert} Kupfer")

    choice = int(input("Wähle die Nummer des Gegenstands, den du verkaufen möchtest (oder 0, um abzubrechen): "))

    if 1 <= choice <= len(spieler.gegenstände):
        ausgewählter_gegenstand = spieler.gegenstände.pop(choice - 1)
        spieler.kupfer += int(ausgewählter_gegenstand.wert)  # Wert in int konvertieren

        # Umwandlung von Kupfer in Silber und Gold
        while spieler.kupfer >= 100:
            spieler.kupfer -= 100
            spieler.silber += 1
        while spieler.silber >= 100:
            spieler.silber -= 100
            spieler.gold += 1

        print(f"Du hast {ausgewählter_gegenstand.name} für {ausgewählter_gegenstand.wert} Kupfer verkauft.")
        return zeige_menü(spieler)
    else:
        print("Abgebrochen.")
        return zeige_menü(spieler)


def spiel_beenden() -> None:
    print("Das Spiel wird beendet. Danke fors Spielen!")
    exit()

def tagesquests_anzeigen(spieler: Spieler) -> None:
    spieler.tagesquests_anzeigen()

def tagesquests_generieren(spieler: Spieler) -> None:
    tagesquests = [
        Tagesquest(name="Besiege 10 schwache Gegner", beschreibung="Besiege 10 schwache Gegner", belohnung=(50, 0, 0), ziel_typ='gegner', ziel_menge=10),
        Tagesquest(name="Sammle 5 Heiltränke", beschreibung="Sammle 5 Heiltränke", belohnung=(30, 0, 0), ziel_typ='gegenstand', ziel_menge=5),
        Tagesquest(name="Lerne 2 Fähigkeiten", beschreibung="Lerne 2 Fähigkeiten", belohnung=(40, 0, 0), ziel_typ='fähigkeit', ziel_menge=2),
        Tagesquest(name="Erreiche 500 Erfahrungspunkte", beschreibung="Erreiche 500 Erfahrungspunkte", belohnung=(50, 0, 0), ziel_typ='erfahrung', ziel_menge=500),
        Tagesquest(name="Erreiche Level 5", beschreibung="Erreiche Level 5", belohnung=(0, 0, 100), ziel_typ='level', ziel_menge=5),
    ]
    for tagesquest in tagesquests:
        spieler.tagesquest_hinzufügen(tagesquest)

def starte_tagesquests(spieler: Spieler) -> None:
    tagesquests_generieren(spieler)
    tagesquests_anzeigen(spieler)

def zeige_menü(spieler: Spieler) -> None:
    print("\033[34m**** Hauptmenü ****\033[0m")
    print("1: erkunden")
    print("2: Inventar anzeigen")
    print("3: Magische Schriftrolle verwalten")
    print("4: Quests anzeigen")
    print("5: Tägliche Herausforderung anzeigen")
    print("6: Händler besuchen")
    print("7: Skills anzeigen")
    print("8: Spiel speichern")
    print("9: Spiel laden")
    print("10: Gegenstand Herstellen")
    print("11: Spiel beenden")

    choice = input("Wähle eine Option: ")

    if choice == '1':
        erkunden(spieler)
    elif choice == '2':
        spieler.inventar_anzeigen()
    elif choice == '3':
        magische_schriftrolle_erlernen(spieler)  # Änderung hier
    elif choice == '4':
        quests_anzeigen(spieler)
    elif choice == '5':
        tagesquests_anzeigen(spieler)
    elif choice == '6':
        händler_besuchen(spieler)
    elif choice == '7':
        spieler.skill_menue()
    elif choice == '8':
        speichere_spielerdaten(spieler)
        print("Das Spiel wurde gespeichert!")
    elif choice == '9':
        name = input("Gib deinen Spielernamen ein: ")
        spieler = lade_spielerdaten(name)
        if spieler:
            print(f"Willkommen zurück, {spieler.name}!")
            return zeige_menü(spieler)
        else:
            print("Spieler nicht gefunden. Neues Spiel starten.")
            return starte_spiel()
    elif choice == '10':
        herstellen(spieler)  # Pass the spieler argument
    elif choice == '11':
        spiel_beenden()
    else:
        print("Ungültige Wahl. Bitte versuche es erneut.")
        return zeige_menü(spieler)



def herstellen(spieler: Spieler):
    resourcen_mengen = {}
    verwendete_ressourcen = set()
    ressource_used = False  # Flag to check if any resource is used

    for ressource, menge in spieler.ressourceninventar.items():
        while True:
            try:
                verwendete_menge = int(input(f"Wieviel {ressource} möchten Sie verwenden? Verfügbar: {menge}: "))
                if verwendete_menge > menge:
                    print(f"Sie haben nicht genug {ressource}.")
                elif verwendete_menge < 0:
                    print("Bitte geben Sie eine gültige Zahl ein.")
                elif verwendete_menge == 0:
                    break  # Skip this resource
                elif verwendete_menge < 2:
                    print(f"Sie müssen mindestens 2 Einheiten von {ressource} verwenden, außer wenn Sie 0 eingeben, um es zu überspringen.")
                else:
                    ressource_used = True
                    resourcen_mengen[ressource] = verwendete_menge
                    verwendete_ressourcen.add(ressource)
                    break
            except ValueError:
                print("Bitte eine gültige Zahl eingeben.")

    if not ressource_used:
        print("Keine Ressourcen verwendet. Kein Gegenstand wurde hergestellt.")
        return

    print("Geben Sie 'herstellen' ein, um den Gegenstand herzustellen.")
    confirmation = input("Bestätigen: ")
    if confirmation.lower() != 'herstellen':
        print("Herstellung abgebrochen.")
        return

    name = random.choice(GEGENSTAND_NAMEN)
    gegenstand = random.choice(BENUTZBARE_GEGENSTAENDE)

    if isinstance(gegenstand, Waffe):
        gegenstand.schaden += random.randint(0, 10)  # Beispielwert
    elif isinstance(gegenstand, Rüstung):
        gegenstand.verteidigung += random.randint(0, 5)  # Beispielwert

    if name in SPEZIELLE_EFFEKTE:
        effekte = SPEZIELLE_EFFEKTE[name]
        if isinstance(gegenstand, Waffe):
            gegenstand.schaden += effekte.get("schaden", 0)
        elif isinstance(gegenstand, Rüstung):
            gegenstand.verteidigung += effekte.get("verteidigung", 0)
        print(f"Spezieller Effekt: {effekte.get('effekt', 'Kein')}")

    # Zusätzliche Effekte bei Verwendung von mindestens vier verschiedenen Ressourcen
    if len(verwendete_ressourcen) >= 4:
        extra_effekte = random.sample(list(SPEZIELLE_EFFEKTE.values()), 2)
        for eff in extra_effekte:
            if isinstance(gegenstand, Waffe):
                gegenstand.schaden += eff.get("schaden", 0)
            elif isinstance(gegenstand, Rüstung):
                gegenstand.verteidigung += eff.get("verteidigung", 0)
            print(f"Zusätzlicher Effekt: {eff.get('effekt', 'Kein')}")

    print(f"Du hast {name} hergestellt mit Schaden: {getattr(gegenstand, 'schaden', 'N/A')} und Verteidigung: {getattr(gegenstand, 'verteidigung', 'N/A')}")

    for ressource, menge in resourcen_mengen.items():
        spieler.ressourceninventar[ressource] -= menge

    if isinstance(gegenstand, Waffe):
        spieler.waffeninventar.append(gegenstand)
        print(f"{gegenstand.name} wurde dem Waffeninventar hinzugefügt.")
    elif isinstance(gegenstand, Rüstung):
        spieler.rüstungsinventar.append(gegenstand)
        print(f"{gegenstand.name} wurde dem Rüstungsinventar hinzugefügt.")


def erkunden(spieler: Spieler) -> None:
    while spieler.position < SPIELFELD_GROESSE and spieler.lebenspunkte > 0:
        input("\033[33mDrücke Enter, um zu würfeln...\033[0m")
        wurf = random.randint(1, 6)
        spieler.position += wurf
        spieler.position = min(spieler.position, SPIELFELD_GROESSE - 1)
        print(f"Der Spieler würfelt eine {wurf} und bewegt sich auf Feld {spieler.position}.")
        if spieler.spielfeld[spieler.position] is not None:
            kampf(spieler, spieler.spielfeld[spieler.position])
            if spieler.lebenspunkte <= 0:
                print("Der Spieler hat keine Lebenspunkte mehr und verliert das Spiel.")
                break
        else:
            npc_treffen(spieler)
        if spieler.position >= SPIELFELD_GROESSE - 1:
            print("Der Spieler hat das Ziel erreicht and gewinnt das Spiel!")
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
        print("Danke fors Spielen!")
# Funktion, um die Geschichte basierend auf der Klasse auszugeben
def erzaehle_geschichte(klasse):
    if klasse == "Krieger":
        print(f"{Farben.ROT}Du bist nun Krieger und das ist die Geschichte deiner Spezialfähigkeiten:{Farben.ENDE}\n"
      f"{Farben.GRUEN}    - Schwertkampf:{Farben.ENDE} Die ersten Krieger waren einfache Dorfbewohner, die ihre Heimat vor wilden Tieren und feindlichen Stämmen schützen mussten. Sie lernten den Schwertkampf, um sich zu verteidigen. Eines Tages fand ein alter Krieger ein uraltes Schwert in einer Höhle. Als er es berührte, spürte er die Kraft des Schwertes in seinen Adern. Von diesem Moment an wurde der Schwertkampf zu einer Kunst, die von Generation zu Generation weitergegeben wurde.\n"
      f"{Farben.BLAU}    - Schildnutzung:{Farben.ENDE} Ein tapferer Krieger namens Galdor rettete einst ein Dorf vor einer Horde Orks. Er benutzte einen Schild, um die Dorfbewohner zu schützen. Die Dorfbewohner waren so beeindruckt von seiner Tapferkeit, dass sie begannen, die Kunst der Schildnutzung zu erlernen.\n"
      f"{Farben.MAGENTA}    - Berserker-Rage:{Farben.ENDE} In den eisigen Bergen lebte ein Krieger namens Ragnar. Er war bekannt für seine unbändige Wut im Kampf. Eines Tages wurde er von einem Bären angegriffen und überlebte nur knapp. Seitdem kanalisiert er seine Wut, um übermenschliche Kraft und Geschwindigkeit zu erlangen.\n"
      f"{Farben.CYAN}    - Kampfgeschick:{Farben.ENDE} Der legendäre Krieger Aric wurde von einem alten Meister in den Wäldern ausgebildet. Dieser Meister lehrte ihn, die Bewegungen der Gegner zu antizipieren und ihre Schwächen auszunutzen. Aric wurde zum Meister des Kampfgeschicks.\n"
      f"{Farben.GELB}    - Kriegerstärke:{Farben.ENDE} Ein Krieger namens Thrain trainierte sein ganzes Leben lang, um die stärksten Waffen tragen zu können. Er trank einen Trank aus dem Herz eines Drachen und erlangte dadurch übermenschliche Stärke.")
    elif klasse == "Magier":
        print(f"{Farben.ROT}Du bist nun Magier und das ist die Geschichte deiner Spezialfähigkeiten:{Farben.ENDE}\n"
      f"{Farben.GRUEN}    - Feuerball:{Farben.ENDE} Der Magier Elowen studierte die alten Schriften und entdeckte ein uraltes Ritual, das es ihm ermöglichte, Feuerbälle zu erschaffen. Er fand einen versteckten Tempel und vollzog das Ritual, um die Macht des Feuers zu beherrschen.\n"
      f"{Farben.BLAU}    - Eislanze:{Farben.ENDE} Die Magierin Isolde lebte in einem eisigen Reich. Sie beobachtete die eisigen Stürme und lernte, ihre Magie zu nutzen, um tödliche Eislanzen zu formen. Diese Fähigkeit wurde von den Magiern weiterentwickelt und verfeinert.\n"
      f"{Farben.MAGENTA}    - Blitzschlag:{Farben.ENDE} Ein Magier namens Thalos wurde von einem Blitz getroffen und überlebte. Er erkannte, dass der Blitz eine mächtige Energiequelle war. Er studierte die Naturgewalten und lernte, den Blitz zu kontrollieren.\n"
      f"{Farben.CYAN}    - Magische Barriere:{Farben.ENDE} Die Magierin Selene lebte in einer Stadt, die von feindlichen Armeen belagert wurde. Sie erschuf eine magische Barriere, die die Stadt vor Angriffen schützte. Diese Fähigkeit wurde von den Magiern weiterentwickelt, um ganze Städte zu schützen.\n"
      f"{Farben.GELB}    - Arkane Macht:{Farben.ENDE} Ein alter Magier namens Alaric entdeckte eine uralte Bibliothek, die verbotene Schriften über die Arkane Macht enthielt. Er studierte diese Schriften und wurde zu einem der mächtigsten Magier aller Zeiten.")
    elif klasse == "Schurke":
        print(f"{Farben.ROT}Du bist nun Schurke und das ist die Geschichte deiner Spezialfähigkeiten:{Farben.ENDE}\n"
      f"{Farben.GRUEN}    - Schleichangriff:{Farben.ENDE} Der Dieb Corwin war ein Meister des Schleichens. Er konnte sich lautlos an seine Opfer heranschleichen und tödliche Angriffe ausführen. Seine Fähigkeiten wurden von den Schurken weiterentwickelt, um in den Schatten zu agieren.\n"
      f"{Farben.BLAU}    - Vergiften:{Farben.ENDE} Die Assassine Lyra war berüchtigt für ihre vergifteten Dolche. Sie sammelte seltene Kräuter und mischte tödliche Gifte. Ihre Kunst wurde von den Schurken weitergegeben.\n"
      f"{Farben.MAGENTA}    - Doppelschlag:{Farben.ENDE} Ein Schurke namens Raven war ein Meister des schnellen Angriffs. Er konnte seine Dolche so geschickt führen, dass es schien, als hätte er zwei Paar Hände. Eines Nachts, während er in den Schatten einer alten Eiche lauerte, wurde er von einem mysteriösen Fremden angesprochen. Dieser Fremde, ein alter Dieb namens Silas, enthüllte ihm das Geheimnis des Doppelschlags. Silas hatte einst einen Pakt mit einem uralten Geist geschlossen, der ihm die Fähigkeit verlieh, blitzschnell zuzuschlagen. Raven lernte von Silas und wurde zu einem legendären Schurken, der seine Gegner mit einem Doppelschlag überraschte.")
    elif klasse == "Heiler":
        print(f"{Farben.ROT}Du bist nun Heiler und das ist die Geschichte deiner Spezialfähigkeiten:{Farben.ENDE}\n"
      f"{Farben.GRUEN}    - Heilung:{Farben.ENDE} Die Heilerin Elara lebte in einem abgelegenen Tempel. Eines Tages fand sie eine uralte Schriftrolle, die die Kunst der Heilung beschrieb. Sie lernte die geheimen Gebete und Rituale, um Wunden zu heilen und Krankheiten zu lindern. Elara wurde zur Hüterin des Lebens.\n"
      f"{Farben.BLAU}    - Heiliger Blitz:{Farben.ENDE} Ein junger Heiler namens Caelan wurde von einem Blitz getroffen, als er versuchte, einen verletzten Reisenden zu retten. Anstatt zu sterben, spürte er die Energie des Blitzes in sich. Er konnte nun heilende Blitze beschwören, um seine Verbündeten zu stärken und Feinde zu schwächen.\n"
      f"{Farben.MAGENTA}    - Manaregeneration:{Farben.ENDE} Die weise Heilerin Lysandra meditierte jahrelang in den Bergen. Sie entdeckte einen verborgenen Wasserfall, der von einer Quelle gespeist wurde, die Mana enthielt. Lysandra trank von diesem Wasser und erlangte die Fähigkeit, ihre magische Energie schneller zu regenerieren.\n"
      f"{Farben.CYAN}    - Heiliger Segen:{Farben.ENDE} Ein alter Priester namens Eamon wurde von den Göttern auserwählt. Er konnte heilige Symbole auf die Stirn seiner Schützlinge zeichnen und ihnen göttlichen Schutz verleihen. Sein Segen heilte nicht nur den Körper, sondern auch die Seele.\n"
      f"{Farben.GELB}    - Göttliche Gnade:{Farben.ENDE} Die Heilerin Seraphina hatte eine Vision von einer strahlenden Göttin. Diese Göttin lehrte sie, wie man die göttliche Energie kanalisiert, um Wunder zu vollbringen. Seraphina konnte Wunden schließen, Krankheiten heilen und sogar Tote wiederbeleben.")

def starte_spiel() -> None:
    name = input("Gib deinen Spielernamen ein: ")
    erzähle_geschichte()
    spieler = lade_spielerdaten(name)

    if spieler is None:
        print("Wähle deine Klasse:")
        print("1: Krieger")
        print("2: Magier")
        print("3: Schurke")
        print("4: Heiler")
        while True:
            try:
                wahl = int(input("Gib die Nummer deiner Klasse ein: "))
                if wahl not in [1, 2, 3, 4]:
                    print("Ungültige Wahl. Bitte eine Zahl zwischen 1 und 4 eingeben.")
                    continue
                break
            except ValueError:
                print("Ungültige Eingabe. Bitte eine gültige Zahl eingeben.")
        
        if wahl == 1:
            klasse = "Krieger"
        elif wahl == 2:
            klasse = "Magier"
        elif wahl == 3:
            klasse = "Schurke"
        elif wahl == 4:
            klasse = "Heiler"
        spieler = Spieler(name, klasse, SPIELER_START_LEBENSPUNKTE, SPIELER_START_LEBENSPUNKTE, 0, 1, [], [])
        
    else:
        klasse = spieler.klasse  # Hier die Klasse aus dem geladenen Spieler übernehmen
        spieler.lebenspunkte = spieler.max_lebenspunkte
        print(f"Willkommen zurück, {spieler.name}! Level: {spieler.level_system.level}, Erfahrungspunkte: {spieler.level_system.erfahrung}, Lebenspunkte: {spieler.lebenspunkte}/{spieler.max_lebenspunkte}")

    starte_tagesquests(spieler)
    erzaehle_geschichte(klasse)

    while True:
        zeige_menü(spieler)



def erzähle_geschichte() -> None:
    geschichte = """
    Herz der Mutigen: Das Schicksal des Königreichs
    In einer Welt, die von dunklen Mächten heimgesucht wird, liegt das Schicksal aller Lebewesen in den Händen eines mutigen Abenteurers - dir.
    Vor langer Zeit wurde das Land in Stücke gerissen and von furchterregenden Kreaturen überrannt, die aus den Tiefen der Unterwelt kamen.
    Die Legende besagt, dass nur derjenige, der das sagenumwobene Artefakt 'Herz der Mutigen' findet and die vier Elementwächter besiegt,
    das Land vereinen and den Frieden wiederherstellen kann. Dieses Artefakt verleiht seinem Besitzer unvorstellbare Macht and die Fähigkeit,
    die Dunkelheit zu vertreiben. Doch der Weg ist gefährlich and nur die Tapfersten wagen es, ihn zu beschreiten.

    Dein Abenteuer beginnt in den Ruinen des alten Königreichs, wo die ersten Hinweise auf das Artefakt versteckt sind.
    Mit jedem Gegner, den du besiegst, and jedem Rätsel, das du löst, kommst du dem Ziel näher. Aber sei gewarnt:
    Die Elementwächter werden not kampflos aufgeben. Sie werden alles in ihrer Macht Stehende tun, um dich aufzuhalten.

    Am Ende des Weges, if du alle Prüfungen bestanden and die Wächter besiegt hast, wartet das 'Herz der Mutigen' auf dich.
    Mit ihm kannst du die Welt retten and als Held in die Geschichte eingehen. Bist du bereit, dein Schicksal anzunehmen and das größte Abenteuer deines Lebens zu beginnen?
    """
    print(geschichte)

starte_spiel()
