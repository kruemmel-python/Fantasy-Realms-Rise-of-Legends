from typing import Tuple, List, Optional
import random
import csv
import os
from dataclasses import dataclass, field
from colorama import Fore, Style


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
    # Weitere Gegenstände...
]

@dataclass
class Fähigkeit:
    name: str
    schaden: int
    kosten: int
    mana_kosten: int = 0

@dataclass
class MagischeSchriftrolle(Gegenstand):
    schaden: int
    kosten: int
    mana_kosten: int
    zauberart: str

# Magische Schriftrollen hinzufügen
MAGISCHE_SCHRIFTROLLEN = [
    MagischeSchriftrolle(name="Feuerball-Schriftrolle", schaden=70, kosten=100, mana_kosten=50, zauberart="Feuer", wert=150, typ="Magische Schriftrolle"),
    MagischeSchriftrolle(name="Eislanze-Schriftrolle", schaden=60, kosten=90, mana_kosten=40, zauberart="Eis", wert=130, typ="Magische Schriftrolle"),
    MagischeSchriftrolle(name="Blitzschlag-Schriftrolle", schaden=80, kosten=120, mana_kosten=60, zauberart="Blitz", wert=170, typ="Magische Schriftrolle"),
    MagischeSchriftrolle(name="Erdbeben-Schriftrolle", schaden=100, kosten=150, mana_kosten=70, zauberart="Erde", wert=200, typ="Magische Schriftrolle"),
    MagischeSchriftrolle(name="Windstoß-Schriftrolle", schaden=50, kosten=70, mana_kosten=30, zauberart="Luft", wert=100, typ="Magische Schriftrolle"),
    MagischeSchriftrolle(name="Wasserstrahl-Schriftrolle", schaden=55, kosten=75, mana_kosten=35, zauberart="Wasser", wert=110, typ="Magische Schriftrolle"),
    MagischeSchriftrolle(name="Heilungs-Schriftrolle", schaden=-50, kosten=100, mana_kosten=50, zauberart="Heilung", wert=160, typ="Magische Schriftrolle"),
    MagischeSchriftrolle(name="Schattenklinge-Schriftrolle", schaden=65, kosten=85, mana_kosten=45, zauberart="Schatten", wert=140, typ="Magische Schriftrolle"),
    MagischeSchriftrolle(name="Lichtstrahl-Schriftrolle", schaden=75, kosten=95, mana_kosten=55, zauberart="Licht", wert=150, typ="Magische Schriftrolle"),
    MagischeSchriftrolle(name="Meteor-Schriftrolle", schaden=120, kosten=200, mana_kosten=80, zauberart="Feuer", wert=220, typ="Magische Schriftrolle")
]


BENUTZBARE_GEGENSTAENDE.extend(MAGISCHE_SCHRIFTROLLEN)

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
    def __init__(self, name, level=1, max_level=10, gold_cost=1000, grundschaden=0):
        self.name = name
        self.level = level
        self.max_level = max_level
        self.gold_cost = gold_cost
        self.grundschaden = grundschaden 

    def level_up(self, gold):
        if self.level < self.max_level:
            if gold >= self.gold_cost:
                self.level += 1
                self.grundschaden = int(self.grundschaden * 1.1)  # 10% Erhöhung des Grundschadens
                print(f"{self.name} hat Level {self.level} erreicht! Neuer Grundschaden: {self.grundschaden}")
                return gold - self.gold_cost
            else:
                raise ValueError("Nicht genügend Gold")
        else:
            raise ValueError("Maximales Level erreicht")

    def berechne_schaden(self):
        return self.grundschaden + (self.level * 5)  # Beispiel: 5 Schaden pro Level

    def __repr__(self):
        return f"{self.name} (Level {self.level}/{self.max_level}, Gold-Kosten: {self.gold_cost})"


class Skillsystem:
    def __init__(self):
        self.skills = []

    def add_skill(self, skill):
        self.skills.append(skill)

    def level_up_skill(self, skill_name, gold):
        for skill in self.skills:
            if skill.name == skill_name:
                remaining_gold = skill.level_up(gold)
                return skill, remaining_gold
        raise ValueError(f"Skill {skill_name} nicht gefunden")

    def zeige_skills(self):
        for skill in self.skills:
            print(skill)

    def __repr__(self):
        return "\n".join(str(skill) for skill in self.skills)



class KriegerSkillsystem(Skillsystem):
    def __init__(self):
        super().__init__()
        self.add_skill(Skill("Schwertkampf", gold_cost=1000))
        self.add_skill(Skill("Schildnutzung", gold_cost=1000))
        self.add_skill(Skill("Berserker-Rage", gold_cost=2000))
        self.add_skill(Skill("Kampfgeschick", gold_cost=1200))
        self.add_skill(Skill("Kriegerstärke", gold_cost=1800))

class MagierSkillsystem(Skillsystem):
    def __init__(self):
        super().__init__()
        self.add_skill(Skill("Feuerball", gold_cost=1500))
        self.add_skill(Skill("Eislanze", gold_cost=1200))
        self.add_skill(Skill("Blitzschlag", gold_cost=1800))
        self.add_skill(Skill("Magische Barriere", gold_cost=1000))
        self.add_skill(Skill("Arkane Macht", gold_cost=2000))

class SchurkeSkillsystem(Skillsystem):
    def __init__(self):
        super().__init__()
        self.add_skill(Skill("Schleichangriff", gold_cost=1400))
        self.add_skill(Skill("Vergiften", gold_cost=1000))
        self.add_skill(Skill("Doppelschlag", gold_cost=1500))
        self.add_skill(Skill("Diebeskunst", gold_cost=800))
        self.add_skill(Skill("Meuchelmord", gold_cost=2000))

class HeilerSkillsystem(Skillsystem):
    def __init__(self):
        super().__init__()
        self.add_skill(Skill("Heilung", gold_cost=1000))
        self.add_skill(Skill("Schutzschild", gold_cost=1200))
        self.add_skill(Skill("Wiederbelebung", gold_cost=1500))
        self.add_skill(Skill("Heiliger Segen", gold_cost=800))
        self.add_skill(Skill("Göttliche Gnade", gold_cost=2000))


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
    magische_schriftrollen: List[MagischeSchriftrolle] = field(default_factory=list)
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
        skill, remaining_gold = self.skillsystem.level_up_skill(skill_name, self.gold)
        self.gold = remaining_gold
        return skill
                                                                     
    def skills_anzeigen(self):
        print("Aktuelle Skills:")
        print(self.skillsystem)
        return self.skill_menue()
    
    def skills_xp_anzeigen(self):
        print("XP für aktuelle Skills:")
        self.skillsystem.zeige_skills_xp()
        return self.skill_menue()

    def skill_menue(self):
        print("\nSkill-Menü")
        print("1: Skills anzeigen")
        print("2: Skill leveln")
        print("3: Skill-Status anzeigen")
        print("4: Zum Hauptmenü zurückkehren")

        choice = input("Wähle eine Option: ")

        if choice == '1':
            self.skills_anzeigen()
        elif choice == '2':
            self.skill_level_up_menue()
        elif choice == '3':
            self.skills_anzeigen()
        elif choice == '4':
            return zeige_menü(self)
        else:
            print("Ungültige Wahl. Bitte versuche es erneut.")
        return self.skill_menue()

    def skill_level_up_menue(self):
        print("Wähle einen Skill zum Leveln:")
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

    def add_magische_schriftrolle(self, schriftrolle: MagischeSchriftrolle) -> None:
        if len(self.magische_schriftrollen) < 2:
            self.magische_schriftrollen.append(schriftrolle)
            print(f"Magische Schriftrolle {schriftrolle.name} wurde erlernt.")
        else:
            print("Du kannst nur 2 magische Schriftrollen erlernen.")

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

    def schriftrolle_auswählen(self) -> Optional[MagischeSchriftrolle]:
        if not self.magische_schriftrollen:
            print("Keine magischen Schriftrollen verfügbar.")
            return None
        print("Verfügbare magische Schriftrollen:")
        for i, schriftrolle in enumerate(self.magische_schriftrollen):
            print(f"{i + 1}: {schriftrolle.name} - Schaden: {schriftrolle.schaden}, Mana-Kosten: {schriftrolle.mana_kosten}")
        wahl = int(input("Wähle eine magische Schriftrolle (Nummer eingeben): "))
        if 1 <= wahl <= len(self.magische_schriftrollen):
            ausgewählte_schriftrolle = self.magische_schriftrollen[wahl - 1]
            if self.mana >= ausgewählte_schriftrolle.mana_kosten:
                return ausgewählte_schriftrolle
            else:
                print("Nicht genügend Mana.")
                return None
        else:
            print("Ungültige Wahl.")
            return None

    def schriftrolle_verwenden(self, schriftrolle: MagischeSchriftrolle, gegner: Gegner) -> None:
        gegner.lebenspunkte -= schriftrolle.schaden
        self.mana -= schriftrolle.mana_kosten
        print(f"Magische Schriftrolle {schriftrolle.name} verwendet und {schriftrolle.schaden} Schaden verursacht. {gegner.name} hat noch {gegner.lebenspunkte} Lebenspunkte.")

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
        'schwach': f"{Fore.YELLOW}Achtung! Du bist auf einen {gegner.name} gestoßen. Bereite dich auf einen Kampf vor!{Style.RESET_ALL}",
        'mittel': f"{Fore.BLUE}Vorsicht! Ein wilder {gegner.name} kreuzt deinen Weg. Zeige ihm deine Stärke!{Style.RESET_ALL}",
        'stark': f"{Fore.RED}Ein mächtiger {gegner.name} erscheint! Dies wird eine wahre Herausforderung!{Style.RESET_ALL}",
        'boss': f"{Fore.MAGENTA}Ein epischer Kampf steht bevor! Der {gegner.name} fordert dich heraus!{Style.RESET_ALL}"
    }
    print(einleitungen[gegner.typ])

def kampf(spieler: Spieler, gegner: Gegner) -> None:
    kampfeinleitung(gegner)
    while spieler.lebenspunkte > 0 and gegner.lebenspunkte > 0:
        print("\nKampfmenü")
        print("1: Angriff")
        print("2: Fähigkeit verwenden")
        print("3: Magische Schriftrolle verwenden")
        print("4: Heiltrank verwenden")
        print("5: Kampf abbrechen und ins Hauptmenü zurückkehren")

        choice = input("Wähle eine Option: ")

        if choice == '1':
            schaden = spieler.angreifen()
            gegner.lebenspunkte -= schaden
            print(f"{Fore.GREEN}Du verursachst {schaden} Schaden. {gegner.name} hat noch {gegner.lebenspunkte} Lebenspunkte.{Style.RESET_ALL}")
        elif choice == '2':
            fähigkeit = spieler.fähigkeit_auswählen()
            if fähigkeit:
                gegner.lebenspunkte -= fähigkeit.schaden
                spieler.mana -= fähigkeit.mana_kosten
                print(f"{Fore.CYAN}Fähigkeit {fähigkeit.name} verwendet und {fähigkeit.schaden} Schaden verursacht. {gegner.name} hat noch {gegner.lebenspunkte} Lebenspunkte.{Style.RESET_ALL}")
        elif choice == '3':
            schriftrolle = spieler.schriftrolle_auswählen()
            if schriftrolle:
                spieler.schriftrolle_verwenden(schriftrolle, gegner)
        elif choice == '4':
            spieler.heiltrank_nutzen()
        elif choice == '5':
            print("Du hast den Kampf abgebrochen und kehrst ins Hauptmenü zurück.")
            return zeige_menü(spieler)
        else:
            print("Ungültige Wahl. Bitte wähle eine Option aus dem Menü.")

        if gegner.lebenspunkte <= 0:
            print(f"{Fore.YELLOW}{gegner.name} wurde besiegt!{Style.RESET_ALL}")
            spieler.add_muenzen(gegner.kupfer, gegner.silber, gegner.gold)
            print(f"{Fore.YELLOW}Du hast {gegner.kupfer} Kupfer, {gegner.silber} Silber und {gegner.gold} Gold erhalten.{Style.RESET_ALL}")
            if gegner.seltene_gegenstände:
                for gegenstand in gegner.seltene_gegenstände:
                    spieler.add_gegenstand(gegenstand)
                    print(f"{Fore.YELLOW}Du hast einen seltenen Gegenstand gefunden: {gegenstand.name} - Wert: {gegenstand.wert} Kupfer{Style.RESET_ALL}")
            if gegner.benutzbare_gegenstände:
                for gegenstand in gegner.benutzbare_gegenstände:
                    spieler.add_gegenstand(gegenstand)
                    print(f"{Fore.YELLOW}Du hast einen benutzbaren Gegenstand gefunden: {gegenstand.name}{Style.RESET_ALL}")
            spieler.erfahrung_sammeln(50)
            spieler.heilen()
            spieler.finde_heiltränke()
            spieler.quest_fortschritt_aktualisieren('gegner', 1)
            speichere_spielerdaten(spieler)
            return

        gegner_schaden = gegner.angreifen()
        reduzierter_schaden = spieler.verteidigen(gegner_schaden)
        if spieler.lebenspunkte <= 0:
            print(f"{Fore.RED}{gegner.name} verursacht {gegner_schaden} Schaden. Der Spieler wurde besiegt.{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.RED}{gegner.name} verursacht {gegner_schaden} Schaden. Nach Verteidigung hat der Spieler noch {spieler.lebenspunkte} Lebenspunkte.{Style.RESET_ALL}")
            spieler.heiltrank_nutzen()

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
    print("3: Magische Schriftrolle wirken")
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
        spieler.skill_menue()
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
