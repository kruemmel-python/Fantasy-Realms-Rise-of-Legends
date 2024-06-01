from typing import Tuple, List, Optional
import random
import csv
import os
from dataclasses import dataclass, field

# Konstanten
LEBENSPUNKTE = {'schwach': 50, 'mittel': 70, 'stark': 90, 'boss': 200}
MAX_SCHADEN = {'schwach': 30, 'mittel': 40, 'stark': 50, 'boss': 75}
GOLD_BELOHNUNG = {'schwach': (0, 0, 10), 'mittel': (0, 0, 20), 'stark': (0, 0, 30), 'boss': (0, 0, 100)}
SPIELFELD_GROESSE = 1000
GEGNER_TYPEN = ['schwach', 'mittel', 'stark']
BOSS_TYPEN = ['boss']
ANZAHL_GEGNER_PRO_TYP = 100
ANZAHL_BOSSE = 50
SPIELER_START_LEBENSPUNKTE = 200
SPIELER_MAX_SCHADEN = 55
SPIELER_START_MANA = 100
SPIELER_MAX_MANA = 100
CSV_DATEI = 'spielerdaten.csv'
START_GOLD = (0, 0, 1)  # (Kupfer, Silber, Gold)

# Dropraten für seltene Gegenstände
SELTENE_DROP_RATE = 0.15  # 15%
SEHR_SELTENE_DROP_RATE = 0.01  # 1%

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

# Liste der Gegenstände, die ein Spieler benutzen kann
BENUTZBARE_GEGENSTAENDE = [
    Waffe(name="Dämonenklinge", typ="Waffe", wert=100, schaden=15),
    Waffe(name="Kriegsbeil", typ="Waffe", wert=120, schaden=20),
    Rüstung(name="Eisenhelm", typ="Helm", wert=80, verteidigung=10),
    Rüstung(name="Plattenpanzer", typ="Rüstung", wert=150, verteidigung=25),
    Rüstung(name="Schattenstiefel", typ="Stiefel", wert=70, verteidigung=8),
    Rüstung(name="Lederhandschuhe", typ="Handschuhe", wert=60, verteidigung=5),
    Waffe(name="Klinge des Zorns", typ="Waffe", wert=110, schaden=16),
    Waffe(name="Klinge der Weisheit", typ="Waffe", wert=120, schaden=17),
    Waffe(name="Klinge der Ehre", typ="Waffe", wert=130, schaden=18),
    Waffe(name="Klinge des Schicksals", typ="Waffe", wert=140, schaden=19),
    Waffe(name="Klinge des Königs", typ="Waffe", wert=150, schaden=20),
    Waffe(name="Klinge der Dunkelheit", typ="Waffe", wert=160, schaden=21),
    Waffe(name="Klinge des Lichts", typ="Waffe", wert=170, schaden=22),
    Waffe(name="Klinge des Sturms", typ="Waffe", wert=180, schaden=23),
    Waffe(name="Klinge des Drachen", typ="Waffe", wert=190, schaden=24),
    Waffe(name="Klinge des Chaos", typ="Waffe", wert=200, schaden=25),
    Waffe(name="Klinge der Ruhe", typ="Waffe", wert=210, schaden=26),
    Waffe(name="Klinge der Macht", typ="Waffe", wert=220, schaden=27),
    Waffe(name="Klinge der Gerechtigkeit", typ="Waffe", wert=230, schaden=28),
    Waffe(name="Klinge der Tapferkeit", typ="Waffe", wert=240, schaden=29),
    Waffe(name="Klinge der Wahrheit", typ="Waffe", wert=250, schaden=30),
    Waffe(name="Klinge der Legenden", typ="Waffe", wert=260, schaden=31),
    Waffe(name="Klinge der Eroberung", typ="Waffe", wert=270, schaden=32),
    Waffe(name="Klinge der Siege", typ="Waffe", wert=280, schaden=33),
    Waffe(name="Klinge der Rebellion", typ="Waffe", wert=290, schaden=34),
    Waffe(name="Klinge der Revolution", typ="Waffe", wert=300, schaden=35),
    Waffe(name="Beil des Zerstörers", typ="Waffe", wert=130, schaden=21),
    Waffe(name="Beil des Kriegers", typ="Waffe", wert=140, schaden=22),
    Waffe(name="Beil des Siegers", typ="Waffe", wert=150, schaden=23),
    Waffe(name="Beil des Berserkers", typ="Waffe", wert=160, schaden=24),
    Waffe(name="Beil des Vandalen", typ="Waffe", wert=170, schaden=25),
    Waffe(name="Beil des Eroberers", typ="Waffe", wert=180, schaden=26),
    Waffe(name="Beil des Tyrannen", typ="Waffe", wert=190, schaden=27),
    Waffe(name="Beil des Barbaren", typ="Waffe", wert=200, schaden=28),
    Waffe(name="Beil des Schlächters", typ="Waffe", wert=210, schaden=29),
    Waffe(name="Beil des Henkers", typ="Waffe", wert=220, schaden=30),
    Waffe(name="Beil des Anführers", typ="Waffe", wert=230, schaden=31),
    Waffe(name="Beil des Pioniers", typ="Waffe", wert=240, schaden=32),
    Waffe(name="Beil des Entdeckers", typ="Waffe", wert=250, schaden=33),
    Waffe(name="Beil des Eindringlings", typ="Waffe", wert=260, schaden=34),
    Waffe(name="Beil des Avantgardisten", typ="Waffe", wert=270, schaden=35),
    Waffe(name="Beil des Innovators", typ="Waffe", wert=280, schaden=36),
    Waffe(name="Beil des Neuerers", typ="Waffe", wert=290, schaden=37),
    Waffe(name="Beil des Erneuerers", typ="Waffe", wert=300, schaden=38),
    Waffe(name="Beil des Reformators", typ="Waffe", wert=310, schaden=39),
    Waffe(name="Beil des Umgestalters", typ="Waffe", wert=320, schaden=40),
    Rüstung(name="Helm des Wächters", typ="Helm", wert=85, verteidigung=11),
    Rüstung(name="Helm des Beschützers", typ="Helm", wert=90, verteidigung=12),
    Rüstung(name="Helm des Verteidigers", typ="Helm", wert=95, verteidigung=13),
    Rüstung(name="Helm des Hüters", typ="Helm", wert=100, verteidigung=14),
    Rüstung(name="Helm des Bewahrers", typ="Helm", wert=105, verteidigung=15),
    Rüstung(name="Helm des Schildwächters", typ="Helm", wert=110, verteidigung=16),
    Rüstung(name="Helm des Patrons", typ="Helm", wert=115, verteidigung=17),
    Rüstung(name="Helm des Förderers", typ="Helm", wert=120, verteidigung=18),
    Rüstung(name="Helm des Meisters", typ="Helm", wert=125, verteidigung=19),
    Rüstung(name="Helm des Experten", typ="Helm", wert=130, verteidigung=20),
    Rüstung(name="Helm des Profis", typ="Helm", wert=135, verteidigung=21),
    Rüstung(name="Helm des Virtuosen", typ="Helm", wert=140, verteidigung=22),
    Rüstung(name="Helm des Künstlers", typ="Helm", wert=145, verteidigung=23),
    Rüstung(name="Helm des Handwerkers", typ="Helm", wert=150, verteidigung=24),
    Rüstung(name="Helm des Fachmanns", typ="Helm", wert=155, verteidigung=25),
    Rüstung(name="Helm des Spezialisten", typ="Helm", wert=160, verteidigung=26),
    Rüstung(name="Helm des Gelehrten", typ="Helm", wert=165, verteidigung=27),
    Rüstung(name="Helm des Akademikers", typ="Helm", wert=170, verteidigung=28),
    Rüstung(name="Helm des Dozenten", typ="Helm", wert=175, verteidigung=29),
    Rüstung(name="Helm des Professors", typ="Helm", wert=180, verteidigung=30),
    Rüstung(name="Panzer des Kriegers", typ="Rüstung", wert=160, verteidigung=26),
    Rüstung(name="Panzer des Soldaten", typ="Rüstung", wert=170, verteidigung=27),
    Rüstung(name="Panzer des Kämpfers", typ="Rüstung", wert=180, verteidigung=28),
    Rüstung(name="Panzer des Streiters", typ="Rüstung", wert=190, verteidigung=29),
    Rüstung(name="Panzer des Kämpen", typ="Rüstung", wert=200, verteidigung=30),
    Rüstung(name="Panzer des Gladiators", typ="Rüstung", wert=210, verteidigung=31),
    Rüstung(name="Panzer des Zenturios", typ="Rüstung", wert=220, verteidigung=32),
    Rüstung(name="Panzer des Champions", typ="Rüstung", wert=230, verteidigung=33),
    Rüstung(name="Panzer des Siegers", typ="Rüstung", wert=240, verteidigung=34),
    Rüstung(name="Panzer des Helden", typ="Rüstung", wert=250, verteidigung=35),
    Rüstung(name="Panzer des Eroberers", typ="Rüstung", wert=260, verteidigung=36),
    Rüstung(name="Panzer des Imperators", typ="Rüstung", wert=270, verteidigung=37),
    Rüstung(name="Panzer des Monarchen", typ="Rüstung", wert=280, verteidigung=38),
    Rüstung(name="Panzer des Herrschers", typ="Rüstung", wert=290, verteidigung=39),
    Rüstung(name="Panzer des Kaisers", typ="Rüstung", wert=300, verteidigung=40),
    Rüstung(name="Panzer des Übermenschen", typ="Rüstung", wert=310, verteidigung=41),
    Rüstung(name="Panzer des Titanen", typ="Rüstung", wert=320, verteidigung=42),
    Rüstung(name="Panzer des Giganten", typ="Rüstung", wert=330, verteidigung=43),
    Rüstung(name="Panzer des Kolosses", typ="Rüstung", wert=340, verteidigung=44),
    Rüstung(name="Panzer des Olympiers", typ="Rüstung", wert=350, verteidigung=45),
    Rüstung(name="Stiefel des Wanderers", typ="Stiefel", wert=75, verteidigung=9),
    Rüstung(name="Stiefel des Pfadfinders", typ="Stiefel", wert=80, verteidigung=10),
    Rüstung(name="Stiefel des Spähers", typ="Stiefel", wert=85, verteidigung=11),
    Rüstung(name="Stiefel des Entdeckers", typ="Stiefel", wert=90, verteidigung=12),
    Rüstung(name="Stiefel des Abenteurers", typ="Stiefel", wert=95, verteidigung=13),
    Rüstung(name="Stiefel des Eroberers", typ="Stiefel", wert=100, verteidigung=14),
    Rüstung(name="Stiefel des Triumphators", typ="Stiefel", wert=105, verteidigung=15),
    Rüstung(name="Stiefel des Siegers", typ="Stiefel", wert=110, verteidigung=16),
    Rüstung(name="Stiefel des Meisters", typ="Stiefel", wert=115, verteidigung=17),
    Rüstung(name="Stiefel des Experten", typ="Stiefel", wert=120, verteidigung=18),
    Rüstung(name="Handschuhe des Handwerkers", typ="Handschuhe", wert=65, verteidigung=6),
    Rüstung(name="Handschuhe des Künstlers", typ="Handschuhe", wert=70, verteidigung=7),
    Rüstung(name="Handschuhe des Meisters", typ="Handschuhe", wert=75, verteidigung=8),
    Rüstung(name="Handschuhe des Experten", typ="Handschuhe", wert=80, verteidigung=9),
    Rüstung(name="Handschuhe des Virtuosen", typ="Handschuhe", wert=85, verteidigung=10),
    Rüstung(name="Handschuhe des Profis", typ="Handschuhe", wert=90, verteidigung=11),
    Rüstung(name="Handschuhe des Spezialisten", typ="Handschuhe", wert=95, verteidigung=12),
    Rüstung(name="Handschuhe des Gelehrten", typ="Handschuhe", wert=100, verteidigung=13),
    Rüstung(name="Handschuhe des Akademikers", typ="Handschuhe", wert=105, verteidigung=14),
    Rüstung(name="Handschuhe des Dozenten", typ="Handschuhe", wert=110, verteidigung=15)
]

@dataclass
class Fähigkeit:
    name: str
    schaden: int
    kosten: int
    mana_kosten: int = 0

@dataclass
class Zauber:
    name: str
    schaden: int
    kosten: int
    mana_kosten: int
    zauberart: str

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
        spieler.max_lebenspunkte += 10
        spieler.max_mana += 20
        spieler.lebenspunkte = spieler.max_lebenspunkte
        spieler.mana = spieler.max_mana
        print(f"{spieler.name} ist jetzt Level {self.level}!")
        if self.level == 10:
            spieler.waehle_spezialisierung()

class Skill:
    def __init__(self, name, level=1, max_level=10, xp_cost=20000, grundschaden=0):
        self.name = name
        self.level = level
        self.max_level = max_level
        self.xp_cost = xp_cost
        self.grundschaden = grundschaden

    def level_up(self, xp):
        if self.level < self.max_level:
            if xp >= self.xp_cost:
                self.level += 1
                print(f"{self.name} hat Level {self.level} erreicht!")
                return xp - self.xp_cost
            else:
                raise ValueError("Nicht genügend Erfahrungspunkte")
        else:
            raise ValueError("Maximales Level erreicht")

    def berechne_schaden(self):
        return self.grundschaden + (self.level * 5)  # Beispiel: 5 Schaden pro Level

    def __repr__(self):
        return f"{self.name} (Level {self.level}/{self.max_level}, XP-Kosten: {self.xp_cost})"

class Skillsystem:
    def __init__(self):
        self.skills = []

    def add_skill(self, skill):
        self.skills.append(skill)

    def level_up_skill(self, skill_name, xp):
        for skill in self.skills:
            if skill.name == skill_name:
                remaining_xp = skill.level_up(xp)
                return skill, remaining_xp
        raise ValueError(f"Skill {skill_name} nicht gefunden")

    def verteile_xp(self, xp):
        for skill in self.skills:
            try:
                xp = skill.level_up(xp)
            except ValueError:
                continue  # Ignoriere, wenn ein Skill bereits maximales Level erreicht hat
        return xp

    def __repr__(self):
        return "\n".join(str(skill) for skill in self.skills)

class KriegerSkillsystem(Skillsystem):
    def __init__(self):
        super().__init__()
        self.add_skill(Skill("Schwertkampf", xp_cost=15000))
        self.add_skill(Skill("Schildnutzung", xp_cost=10000))
        self.add_skill(Skill("Berserker-Rage", xp_cost=20000))
        self.add_skill(Skill("Kampfgeschick", xp_cost=12000))
        self.add_skill(Skill("Kriegerstärke", xp_cost=18000))

class MagierSkillsystem(Skillsystem):
    def __init__(self):
        super().__init__()
        self.add_skill(Skill("Feuerball", xp_cost=15000))
        self.add_skill(Skill("Eislanze", xp_cost=12000))
        self.add_skill(Skill("Blitzschlag", xp_cost=18000))
        self.add_skill(Skill("Magische Barriere", xp_cost=10000))
        self.add_skill(Skill("Arkane Macht", xp_cost=20000))

class SchurkeSkillsystem(Skillsystem):
    def __init__(self):
        super().__init__()
        self.add_skill(Skill("Schleichangriff", xp_cost=14000))
        self.add_skill(Skill("Vergiften", xp_cost=10000))
        self.add_skill(Skill("Doppelschlag", xp_cost=15000))
        self.add_skill(Skill("Diebeskunst", xp_cost=8000))
        self.add_skill(Skill("Meuchelmord", xp_cost=20000))

class HeilerSkillsystem(Skillsystem):
    def __init__(self):
        super().__init__()
        self.add_skill(Skill("Heilung", xp_cost=10000))
        self.add_skill(Skill("Schutzschild", xp_cost=12000))
        self.add_skill(Skill("Wiederbelebung", xp_cost=15000))
        self.add_skill(Skill("Heiliger Segen", xp_cost=8000))
        self.add_skill(Skill("Göttliche Gnade", xp_cost=20000))

# Spezialisierungen hinzufügen
class Krieger:
    def __init__(self):
        self.grundskills = [
            Fähigkeit("Schwertkampf", 50, 10, 50),
            Fähigkeit("Schildnutzung", 0, 20, 50),
            Fähigkeit("Berserker-Rage", 70, 25, 50),
            Fähigkeit("Kampfgeschick", 40, 15, 50),
            Fähigkeit("Kriegerstärke", 60, 20, 50)
        ]

class Magier:
    def __init__(self):
        self.grundskills = [
            Fähigkeit("Feuerball", 70, 30, 50),
            Fähigkeit("Eislanze", 50, 25, 50),
            Fähigkeit("Blitzschlag", 60, 30, 50),
            Fähigkeit("Magische Barriere", 40, 20, 50),
            Fähigkeit("Arkane Macht", 80, 40, 50)
        ]

class Schurke:
    def __init__(self):
        self.grundskills = [
            Fähigkeit("Schleichangriff", 60, 15, 50),
            Fähigkeit("Vergiften", 40, 10, 50),
            Fähigkeit("Doppelschlag", 50, 20, 50),
            Fähigkeit("Diebeskunst", 30, 10, 50),
            Fähigkeit("Meuchelmord", 70, 25, 50)
        ]

class Heiler:
    def __init__(self):
        self.grundskills = [
            Fähigkeit("Heilung", 0, 10, 50),
            Fähigkeit("Schutzschild", 0, 15, 50),
            Fähigkeit("Wiederbelebung", 0, 25, 50),
            Fähigkeit("Heiliger Segen", 0, 20, 50),
            Fähigkeit("Göttliche Gnade", 0, 30, 50)
        ]

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

    def __post_init__(self):
        self.name = generiere_gegnernamen(self.typ)
        self.lebenspunkte = int(LEBENSPUNKTE[self.typ] * self.multiplikator)
        self.max_schaden = int(MAX_SCHADEN[self.typ] * self.multiplikator)
        self.kupfer, self.silber, self.gold = GOLD_BELOHNUNG[self.typ]
        self.drop_seltene_gegenstände()
        self.drop_benutzbare_gegenstände()

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
        if random.random() < 0.40:  # 40% Chance, einen benutzbaren Gegenstand zu droppen
            benutzbarer_gegenstand = random.choice(BENUTZBARE_GEGENSTAENDE)
            self.benutzbare_gegenstände.append(benutzbarer_gegenstand)
            print(f"Benutzbarer Gegenstand {benutzbarer_gegenstand.name} von {self.name} gedroppt")

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
    zauber: List[Zauber] = field(default_factory=list)
    quests: List[Quest] = field(default_factory=list)
    tägliche_herausforderungen: List[Tagesquest] = field(default_factory=list)
    level_system: LevelSystem = field(init=False)
    max_mana: int = SPIELER_MAX_MANA
    mana: int = SPIELER_START_MANA
    vergiftet: bool = False
    skillsystem: Skillsystem = field(init=False)
    spezialisierung: Optional[object] = field(default=None, init=False)

    def __post_init__(self):
        self.level_system = LevelSystem(self.erfahrung, self.level)
        self.spielfeld = erstelle_spielfeld(self.gegner_multiplikator)
        self.set_klasse(self.klasse)
        self.xp_fuer_skills = 0

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
        elif klasse == "Unbekannt":
            print("Unbekannte Klasse, Standardklasse Krieger wird verwendet.")
            self.skillsystem = KriegerSkillsystem()
            self.spezialisierung = Krieger()
        else:
            raise ValueError("Unbekannte Klasse")
        self.fähigkeiten = self.spezialisierung.grundskills

    def erfahrung_sammeln(self, xp):
        self.level_system.erfahrung_sammeln(xp, self)
        self.xp_fuer_skills += xp
        self.xp_fuer_skills = self.skillsystem.verteile_xp(self.xp_fuer_skills)

    def skill_level_up(self, skill_name):
        skill, remaining_xp = self.skillsystem.level_up_skill(skill_name, self.level_system.erfahrung)
        self.level_system.erfahrung = remaining_xp
        return skill

    def skills_anzeigen(self):
        print("Aktuelle Skills:")
        print(self.skillsystem)
        return zeige_menü

    def quest_fortschritt_aktualisieren(self, ziel_typ: str, menge: int = 1) -> None:
        for quest in self.quests:
            if quest.ziel_typ == ziel_typ and not quest.abgeschlossen:
                quest.fortschritt_aktualisieren(menge)
                print(f"Fortschritt bei Quest {quest.name}: {quest.fortschritt_anzeigen()}")
                if quest.abgeschlossen:
                    self.add_muenzen(*quest.belohnung)
                    print(f"Quest {quest.name} abgeschlossen! Belohnung: {quest.belohnung} Kupfer, Silber und Gold")

    def tagesquest_fortschritt_aktualisieren(self, ziel_typ: str, menge: int = 1) -> None:
        for quest in self.tägliche_herausforderungen:
            if quest.ziel_typ == ziel_typ and not quest.abgeschlossen:
                quest.fortschritt_aktualisieren(menge)
                print(f"Fortschritt bei Tagesquest {quest.name}: {quest.fortschritt_anzeigen()}")
                if quest.abgeschlossen:
                    self.add_muenzen(*quest.belohnung)
                    print(f"Tagesquest {quest.name} abgeschlossen! Belohnung: {quest.belohnung} Kupfer, Silber und Gold")

    def tagesquest_hinzufügen(self, quest: Tagesquest) -> None:
        self.tägliche_herausforderungen.append(quest)
        print(f"Tagesquest hinzugefügt: {quest.name} - {quest.beschreibung}")

    def tagesquests_anzeigen(self) -> None:
        if not self.tägliche_herausforderungen:
            print("Keine Tagesquests verfügbar.")
        else:
            print("Aktuelle Tagesquests:")
            for quest in self.tägliche_herausforderungen:
                status = "Abgeschlossen" if quest.abgeschlossen else f"Fortschritt: {quest.fortschritt_anzeigen()}"
                print(f"{quest.name}: {quest.beschreibung} - Belohnung: {quest.belohnung} Kupfer, Silber und Gold - Status: {status}")

    def inventar_anzeigen(self) -> None:
        print(f"Name: {self.name}")
        print(f"Klasse: {self.klasse}")
        print(f"Gold: {self.gold}, Silber: {self.silber}, Kupfer: {self.kupfer}")
        print(f"Lebenspunkte: {self.lebenspunkte}/{self.max_lebenspunkte}")
        print(f"Mana: {self.mana}/{self.max_mana}")
        print(f"Level: {self.level_system.level}")
        print(f"Erfahrung: {self.level_system.erfahrung}")

        grundschaden = SPIELER_MAX_SCHADEN
        print(f"Grundschaden: {grundschaden}")

        waffen_schaden = getattr(self.waffe, 'schaden', 0) if isinstance(self.waffe, Waffe) else 0

        gesamt_schaden = grundschaden + waffen_schaden
        print(f"Gesamtschaden: {gesamt_schaden}")

        if not self.gegenstände:
            print("Dein Inventar ist leer.")
        else:
            print("Du hast folgende Gegenstände in deinem Inventar:")
            for i, gegenstand in enumerate(self.gegenstände, 1):
                print(f"{i}: {gegenstand.name} - Typ: {gegenstand.typ}, Wert: {gegenstand.wert} Kupfer")

        if self.waffeninventar:
            print("Waffen im Inventar:")
            for i, waffe in enumerate(self.waffeninventar, 1):
                print(f"{i}: {waffe.name} - Schaden: {waffe.schaden}, Wert: {waffe.wert} Kupfer")

        if self.rüstungsinventar:
            print("Rüstungen im Inventar:")
            for i, rüstung in enumerate(self.rüstungsinventar, 1):
                print(f"{i}: {rüstung.name} - Verteidigung: {rüstung.verteidigung}, Wert: {rüstung.wert} Kupfer")

        if self.waffe:
            if isinstance(self.waffe, Waffe):
                print(f"Ausgerüstete Waffe: {self.waffe.name} - Schaden: {self.waffe.schaden}")
        else:
            print("Keine Waffe ausgerüstet")

        if self.rüstung:
            print(f"Ausgerüstete Rüstung: {self.rüstung.name} - Verteidigung: {self.rüstung.verteidigung}")

        if self.handschuhe:
            print(f"Ausgerüstete Handschuhe: {self.handschuhe.name} - Verteidigung: {self.handschuhe.verteidigung}")

        if self.stiefel:
            print(f"Ausgerüstete Stiefel: {self.stiefel.name} - Verteidigung: {self.stiefel.verteidigung}")

        if self.helm:
            print(f"Ausgerüsteter Helm: {self.helm.name} - Verteidigung: {self.helm.verteidigung}")

        if self.fähigkeiten:
            print("Fähigkeiten:")
            for fähigkeit in self.fähigkeiten:
                print(f"{fähigkeit.name} - Schaden: {fähigkeit.schaden}, Mana-Kosten: {fähigkeit.mana_kosten}")

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
            return zeige_menü
        print("Wähle eine Waffe zum Ausrüsten:")
        for i, waffe in enumerate(self.waffeninventar, 1):
            print(f"{i}: {waffe.name} - Schaden: {waffe.schaden}, Wert: {waffe.wert} Kupfer")
        choice = int(input("Wähle eine Waffe (Nummer eingeben): "))
        if 1 <= choice <= len(self.waffeninventar):
            self.waffe = self.waffeninventar[choice - 1]
            print(f"Waffe {self.waffe.name} ausgerüstet.")
            return zeige_menü

    def rüstung_ausrüsten(self):
        if not self.rüstungsinventar:
            print("Keine Rüstungen im Inventar.")
            return zeige_menü
        print("Wähle eine Rüstung zum Ausrüsten:")
        for i, rüstung in enumerate(self.rüstungsinventar, 1):
            print(f"{i}: {rüstung.name} - Verteidigung: {rüstung.verteidigung}, Wert: {rüstung.wert} Kupfer")
        choice = int(input("Wähle eine Rüstung (Nummer eingeben): "))
        if 1 <= choice <= len(self.rüstungsinventar):
            ausgewählte_rüstung = self.rüstungsinventar[choice - 1]
            if ausgewählte_rüstung.typ == 'Rüstung':
                self.rüstung = ausgewählte_rüstung
            elif ausgewählte_rüstung.typ == 'Handschuhe':
                self.handschuhe = ausgewählte_rüstung
            elif ausgewählte_rüstung.typ == 'Stiefel':
                self.stiefel = ausgewählte_rüstung
            elif ausgewählte_rüstung.typ == 'Helm':
                self.helm = ausgewählte_rüstung
            print(f"Rüstung {ausgewählte_rüstung.name} ausgerüstet.")
            return zeige_menü

    def angreifen(self) -> int:
        waffen_schaden = getattr(self.waffe, 'schaden', 0) if isinstance(self.waffe, Waffe) else 0
        grund_schaden = random.randint(1, SPIELER_MAX_SCHADEN)
        skill_schaden = sum(skill.berechne_schaden() for skill in self.skillsystem.skills)
        gesamtschaden = grund_schaden + waffen_schaden + skill_schaden
        zufälliger_schaden = random.randint(grund_schaden, gesamtschaden)
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
        print(f"Als Siegesbonus wurden die Lebenspunkte des Spielers um 30 erhöht und sind jetzt {self.lebenspunkte}/{self.max_lebenspunkte}.")

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
                print(f"Du hast {gegenstand.name} verwendet. Du bist nicht mehr vergiftet.")
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
                    print(f"Du hast {gegenstand.name} verwendet. Du bist für eine gewisse Zeit unsichtbar.")
            else:
                print(f"Der Gegenstand {gegenstand.name} kann nicht verwendet werden.")
            self.gegenstände.remove(gegenstand)
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
        if isinstance(gegenstand, Waffe):
            self.waffeninventar.append(gegenstand)
        elif isinstance(gegenstand, Rüstung):
            self.rüstungsinventar.append(gegenstand)
        else:
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
        self.quest_fortschritt_aktualisieren('erfahrung', punkte)
        if self.level_system.level > self.level:
            self.level = self.level_system.level
            self.quest_fortschritt_aktualisieren('level', self.level)

    def quest_hinzufügen(self, quest: Quest) -> None:
        self.quests.append(quest)
        print(f"Quest {quest.name} wurde hinzugefügt: {quest.beschreibung}")

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
            print("Nicht genügend Kupfer, Silber oder Gold.")
            return

        total_kupfer -= kosten_kupfer

        self.gold = total_kupfer // 10000
        self.silber = (total_kupfer % 10000) // 100
        self.kupfer = total_kupfer % 100

    def fähigkeit_auswählen(self) -> Optional[Fähigkeit]:
        if not self.fähigkeiten:
            print("Keine Fähigkeiten verfügbar.")
            return None
        print("Verfügbare Fähigkeiten:")
        for i, fähigkeit in enumerate(self.fähigkeiten):
            print(f"{i + 1}: {fähigkeit.name} - Schaden: {fähigkeit.schaden}, Mana-Kosten: {fähigkeit.mana_kosten}")
        wahl = int(input("Wähle eine Fähigkeit (Nummer eingeben): "))
        if 1 <= wahl <= len(self.fähigkeiten):
            ausgewählte_fähigkeit = self.fähigkeiten[wahl - 1]
            if self.mana >= ausgewählte_fähigkeit.mana_kosten:
                return ausgewählte_fähigkeit
            else:
                print("Nicht genügend Mana.")
                return None
        else:
            print("Ungültige Wahl.")
            return None

    def zauber_auswählen(self) -> Optional[Zauber]:
        if not self.zauber:
            print("Keine Zauber verfügbar.")
            return None
        print("Verfügbare Zauber:")
        for i, zauber in enumerate(self.zauber):
            print(f"{i + 1}: {zauber.name} - Schaden: {zauber.schaden}, Mana-Kosten: {zauber.mana_kosten}")
        wahl = int(input("Wähle einen Zauber (Nummer eingeben): "))
        if 1 <= wahl <= len(self.zauber):
            ausgewählter_zauber = self.zauber[wahl - 1]
            if self.mana >= ausgewählter_zauber.mana_kosten:
                return ausgewählter_zauber
            else:
                print("Nicht genügend Mana.")
                return None
        else:
            print("Ungültige Wahl.")
            return None

    def zaubern(self, zauber: Zauber, gegner: Gegner) -> None:
        gegner.lebenspunkte -= zauber.schaden
        self.mana -= zauber.mana_kosten
        print(f"Zauber {zauber.name} verwendet und {zauber.schaden} Schaden verursacht. {gegner.name} hat noch {gegner.lebenspunkte} Lebenspunkte.")

def speichere_spielerdaten(spieler: Spieler) -> None:
    daten = [
        spieler.name,
        spieler.lebenspunkte,
        spieler.max_lebenspunkte,
        spieler.level_system.erfahrung,
        spieler.level_system.level,
        ';'.join([gegenstand.name for gegenstand in spieler.gegenstände]),
        ';'.join([fähigkeit.name for fähigkeit in spieler.fähigkeiten]),
        spieler.kupfer,
        spieler.silber,
        spieler.gold,
        spieler.waffe.name if spieler.waffe else '',
        spieler.rüstung.name if spieler.rüstung else '',
        spieler.__class__.__name__
    ]

    vorhandene_daten = []
    if os.path.exists(CSV_DATEI):
        with open(CSV_DATEI, 'r', newline='') as file:
            reader = csv.reader(file)
            vorhandene_daten = list(reader)

    mit_kopfzeile = False
    expected_headers = [
        'Name', 'Lebenspunkte', 'MaxLebenspunkte', 'Erfahrung', 'Level',
        'Gegenstände', 'Fähigkeiten', 'Kupfer', 'Silber', 'Gold', 'Waffe', 'Rüstung', 'Klasse'
    ]
    if len(vorhandene_daten) == 0 or vorhandene_daten[0] != expected_headers:
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
            writer.writerow(expected_headers)
        writer.writerows(vorhandene_daten)



def lade_spielerdaten(name: str) -> Optional[Spieler]:
    if not os.path.exists(CSV_DATEI):
        return None

    with open(CSV_DATEI, 'r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Name'] == name:
                max_lebenspunkte = int(row['MaxLebenspunkte'])
                lebenspunkte = int(row['Lebenspunkte'])
                erfahrung = int(row['Erfahrung'])
                level = int(row['Level'])
                gegenstände = [Gegenstand(name, 'Gegenstand', 0) for name in row['Gegenstände'].split(';') if name]
                fähigkeiten = [Fähigkeit(name, 0, 0, 0) for name in row['Fähigkeiten'].split(';') if name]
                kupfer = int(row['Kupfer'])
                silber = int(row['Silber'])
                gold = int(row['Gold'])
                waffe = next((w for w in BENUTZBARE_GEGENSTAENDE if isinstance(w, Waffe) and w.name == row['Waffe']), None)
                rüstung = next((r for r in BENUTZBARE_GEGENSTAENDE if isinstance(r, Rüstung) and r.name == row['Rüstung']), None)
                klasse = row['Klasse']

                # Instanz der entsprechenden Klasse erstellen
                klassen_dict = {
                    "Krieger": Krieger,
                    "Magier": Magier,
                    "Schurke": Schurke,
                    "Heiler": Heiler
                }

                # Überprüfen, ob die Klasse bekannt ist, andernfalls Standardklasse setzen
                if klasse not in klassen_dict:
                    print(f"Unbekannte Klasse '{klasse}', Standardklasse Krieger wird verwendet.")
                    klasse = "Krieger"

                # Erstelle die Instanz der entsprechenden Klasse
                spieler = Spieler(name, klasse, lebenspunkte, max_lebenspunkte, erfahrung, level, gegenstände, fähigkeiten)
                
                # Setze die zusätzlichen Attribute des Spielers
                spieler.kupfer = kupfer
                spieler.silber = silber
                spieler.gold = gold
                spieler.waffe = waffe
                spieler.rüstung = rüstung

                return spieler
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

        choice = input("Wähle eine Option: ")

        if choice == '1':
            schaden = spieler.angreifen()
            gegner.lebenspunkte -= schaden
            print(f"Du verursachst {schaden} Schaden. {gegner.name} hat noch {gegner.lebenspunkte} Lebenspunkte.")
        elif choice == '2':
            fähigkeit = spieler.fähigkeit_auswählen()
            if fähigkeit:
                gegner.lebenspunkte -= fähigkeit.schaden
                spieler.mana -= fähigkeit.mana_kosten
                print(f"Fähigkeit {fähigkeit.name} verwendet und {fähigkeit.schaden} Schaden verursacht. {gegner.name} hat noch {gegner.lebenspunkte} Lebenspunkte.")
        elif choice == '3':
            zauber = spieler.zauber_auswählen()
            if zauber:
                spieler.zaubern(zauber, gegner)
        elif choice == '4':
            spieler.heiltrank_nutzen()
        elif choice == '5':
            print("Du hast den Kampf abgebrochen und kehrst ins Hauptmenü zurück.")
            return zeige_menü(spieler)
        else:
            print("Ungültige Wahl. Bitte wähle eine Option aus dem Menü.")

        if gegner.lebenspunkte <= 0:
            print(f"{gegner.name} wurde besiegt!")
            spieler.add_muenzen(gegner.kupfer, gegner.silber, gegner.gold)
            print(f"Du hast {gegner.kupfer} Kupfer, {gegner.silber} Silber und {gegner.gold} Gold erhalten.")
            if gegner.seltene_gegenstände:
                for gegenstand in gegner.seltene_gegenstände:
                    spieler.add_gegenstand(gegenstand)
                    print(f"Du hast einen seltenen Gegenstand gefunden: {gegenstand.name} - Wert: {gegenstand.wert} Kupfer")
            if gegner.benutzbare_gegenstände:
                for gegenstand in gegner.benutzbare_gegenstände:
                    spieler.add_gegenstand(gegenstand)
                    print(f"Du hast einen benutzbaren Gegenstand gefunden: {gegenstand.name} - Wert: {gegenstand.wert} Kupfer")
            spieler.erfahrung_sammeln(50)
            spieler.heilen()
            spieler.finde_heiltränke()
            spieler.quest_fortschritt_aktualisieren('gegner', 1)
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

def zauber_wirken(spieler: Spieler) -> None:
    zauber = spieler.zauber_auswählen()
    if zauber:
        gegner = Gegner('mittel', 1.0)  # Beispielgegner
        spieler.zaubern(zauber, gegner)

def quests_anzeigen(spieler: Spieler) -> None:
    if not spieler.quests:
        print("Keine Quests verfügbar.")
    else:
        print("Aktuelle Quests:")
        for i, quest in enumerate(spieler.quests):
            status = "Abgeschlossen" if quest.abgeschlossen else f"Fortschritt: {quest.fortschritt_anzeigen()}"
            print(f"{i + 1}: {quest.name} - {quest.beschreibung} - Belohnung: {quest.belohnung} Kupfer, Silber und Gold - Status: {status}")

        choice = int(input("Wähle die Nummer der Quest, die du abschließen möchtest (oder 0, um ins Hauptmenü zurückzukehren): "))
        if 1 <= choice <= len(spieler.quests):
            ausgewählte_quest = spieler.quests[choice - 1]
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
        quest_belohnung = (random.randint(50, 100), random.randint(5, 10), random.randint(0, 2))  # Kupfer, Silber, Gold
        ziel_typ = random.choice(['gegner', 'gegenstand'])
        ziel_menge = random.randint(1, 5)
        npc = NPC(npc_name, Quest(quest_name, quest_beschreibung, quest_belohnung, ziel_typ, ziel_menge))

        print(f"Du triffst {npc.name}. Er bietet dir eine Quest an: {npc.quest.name} - {npc.quest.beschreibung} - Belohnung: {npc.quest.belohnung[0]} Kupfer, {npc.quest.belohnung[1]} Silber und {npc.quest.belohnung[2]} Gold")
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
        Gegenstand(name="Mana-Trank", typ="Trank", wert=30),
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

    print("Willkommen beim Händler! Hier sind die verfügbaren Gegenstände:")
    for i, angebot in enumerate(angebote):
        print(f"{i + 1}: {angebot.name} - Typ: {angebot.typ}, Wert: {angebot.wert} Kupfer")

    print(f"{len(angebote) + 1}: Gegenstände verkaufen")

    choice = int(input("Wähle die Nummer des Gegenstands, den du kaufen oder verkaufen möchtest (oder 0, um abzubrechen): "))

    if 1 <= choice <= len(angebote):
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
            return zeige_menü(spieler)
        else:
            print("Du hast nicht genug Kupfer, Silber oder Gold.")
            return zeige_menü(spieler)
    elif choice == len(angebote) + 1:
        verkaufe_gegenstände(spieler)
    else:
        print("Abgebrochen.")
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
        spieler.kupfer += ausgewählter_gegenstand.wert
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
    print("Das Spiel wird beendet. Danke fürs Spielen!")
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
    print("\nHauptmenü")
    print("1: Erkunden")
    print("2: Inventar anzeigen")
    print("3: Zauber wirken")
    print("4: Quests anzeigen")
    print("5: Tägliche Herausforderung anzeigen")
    print("6: Händler besuchen")
    print("7: Skills anzeigen")
    print("8: Spiel speichern")
    print("9: Spiel laden")
    print("10: Spiel beenden")

    choice = input("Wähle eine Option: ")

    if choice == '1':
        erkunden(spieler)
    elif choice == '2':
        spieler.inventar_anzeigen()
    elif choice == '3':
        zauber_wirken(spieler)
    elif choice == '4':
        quests_anzeigen(spieler)
    elif choice == '5':
        tagesquests_anzeigen(spieler)
    elif choice == '6':
        händler_besuchen(spieler)
    elif choice == '7':
        spieler.skills_anzeigen()
    elif choice == '8':
        speichere_spielerdaten(spieler)
        print("Das Spiel wurde gespeichert!")
        return zeige_menü(spieler)
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
        spiel_beenden()
    else:
        print("Ungültige Wahl. Bitte versuche es erneut.")
        return zeige_menü(spieler)

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
        wahl = int(input("Gib die Nummer deiner Klasse ein: "))
        if wahl == 1:
            klasse = "Krieger"
        elif wahl == 2:
            klasse = "Magier"
        elif wahl == 3:
            klasse = "Schurke"
        elif wahl == 4:
            klasse = "Heiler"
        else:
            print("Ungültige Wahl. Standardmäßig wird die Klasse 'Krieger' gewählt.")
            klasse = "Krieger"
        spieler = Spieler(name, klasse, SPIELER_START_LEBENSPUNKTE, SPIELER_START_LEBENSPUNKTE, 0, 1, [], [])
    else:
        spieler.lebenspunkte = spieler.max_lebenspunkte
        print(f"Willkommen zurück, {spieler.name}! Level: {spieler.level_system.level}, Erfahrungspunkte: {spieler.level_system.erfahrung}, Lebenspunkte: {spieler.lebenspunkte}/{spieler.max_lebenspunkte}")

    starte_tagesquests(spieler)

    while True:
        zeige_menü(spieler)

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

starte_spiel()

