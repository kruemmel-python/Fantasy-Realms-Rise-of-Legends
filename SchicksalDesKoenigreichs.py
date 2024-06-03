from typing import Tuple, List, Optional
import random
import csv
import os
from dataclasses import dataclass, field

# Zufällige Farbauswahl ohne Weiß
def zufallsfarbe():
    farben = ["\033[31m", "\033[32m", "\033[33m", "\033[34m", "\033[35m", "\033[36m"]
    return random.choice(farben)

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

# Dropraten for seltene Gegenstände
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
    Rüstung(name="Lederhandschuhe", typ="Handschuhe", wert=60, verteidigung=5)
]
@dataclass
class MagischeSchriftrolle(Gegenstand):
    schaden: int
    kosten: int
    mana_kosten: int
    zauberart: str

MAGISCHE_SCHRIFTROLLEN = [
    MagischeSchriftrolle(name="Feuerball-Schriftrolle", typ="Schriftrolle", wert=100, schaden=50, kosten=100, mana_kosten=30, zauberart="Feuer"),
    MagischeSchriftrolle(name="Blitz-Schriftrolle", typ="Schriftrolle", wert=120, schaden=60, kosten=120, mana_kosten=40, zauberart="Blitz"),
    MagischeSchriftrolle(name="Eislanzen-Schriftrolle", typ="Schriftrolle", wert=80, schaden=40, kosten=80, mana_kosten=20, zauberart="Eis")
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
        spieler.max_lebenspunkte += 10
        spieler.max_mana += 20
        spieler.lebenspunkte = spieler.max_lebenspunkte
        spieler.mana = spieler.max_mana
        print(f"{spieler.name} ist jetzt Level {self.level}!")
        if self.level == 10:
            spieler.waehle_spezialisierung()

class Skill:
    def __init__(self, name, level=1, max_level=10, grandschaden=0, gold_cost=1):
        self.name = name
        self.level = level
        self.max_level = max_level
        self.grandschaden = grandschaden
        self.gold_cost = gold_cost

    def level_up(self, spieler, fähigkeit: Fähigkeit):
        if self.level < self.max_level:
            if spieler.gold >= self.gold_cost:
                spieler.gold -= self.gold_cost
                self.level += 1
                self.grandschaden = int(self.grandschaden * 1.1)  # 10% Erhöhung des Grandschadens
                fähigkeit.schaden_erhoehen(10)  # Erhöht den Schaden der Fähigkeit um 10%
                print(f"{self.name} hat Level {self.level} erreicht! Neuer Grandschaden: {self.grandschaden}")
            else:
                raise ValueError("not genügend Gold")
        else:
            raise ValueError("Maximales Level erreicht")

    def berechne_schaden(self):
        return self.grandschaden + (self.level * 5)  # Beispiel: 5 Schaden pro Level

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
        self.add_skill(Skill("Schwertkampf", gold_cost=10))
        self.add_skill(Skill("Schildnutzung", gold_cost=10))
        self.add_skill(Skill("Berserker-Rage", gold_cost=20))
        self.add_skill(Skill("Kampfgeschick", gold_cost=12))
        self.add_skill(Skill("Kriegerstärke", gold_cost=18))

class MagierSkillsystem(Skillsystem):
    def __init__(self):
        super().__init__()
        self.add_skill(Skill("Feuerball", gold_cost=15))
        self.add_skill(Skill("Eislanze", gold_cost=12))
        self.add_skill(Skill("Blitzschlag", gold_cost=18))
        self.add_skill(Skill("Magische Barriere", gold_cost=10))
        self.add_skill(Skill("Arkane Macht", gold_cost=20))

class SchurkeSkillsystem(Skillsystem):
    def __init__(self):
        super().__init__()
        self.add_skill(Skill("Schleichangriff", gold_cost=14))
        self.add_skill(Skill("Vergiften", gold_cost=10))
        self.add_skill(Skill("Doppelschlag", gold_cost=15))
        self.add_skill(Skill("Diebeskunst", gold_cost=8))
        self.add_skill(Skill("Meuchelmord", gold_cost=20))

class HeilerSkillsystem(Skillsystem):
    def __init__(self):
        super().__init__()
        self.add_skill(Skill("Heilung", gold_cost=10))
        self.add_skill(Skill("Heiliger Blitz", gold_cost=12))
        self.add_skill(Skill("Manaregeneration", gold_cost=15))
        self.add_skill(Skill("Heiliger Segen", gold_cost=8))
        self.add_skill(Skill("Göttliche Gnade", gold_cost=20))

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

        if self.waffeninventar:
            print("\033[34m**** Waffen im Inventar: ****\033[0m")
            for i, waffe in enumerate(self.waffeninventar, 1):
                print(f"{zufallsfarbe()}{i}: {waffe.name} - Schaden: {waffe.schaden}, Wert: {waffe.wert} Kupfer\033[0m")

        if self.rüstungsinventar:
            print("\033[34m**** Rüstungen im Inventar: ****\033[0m")
            for i, rüstung in enumerate(self.rüstungsinventar, 1):
                print(f"{zufallsfarbe()}{i}: {rüstung.name} - Verteidigung: {rüstung.verteidigung}, Wert: {rüstung.wert} Kupfer\033[0m")

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
            return zeige_menü
        print("\033[34m**** Wähle eine Waffe zum Ausrüsten: ****\033[0m")
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
        print("\033[34m**** Wähle eine Rüstung zum Ausrüsten: ****\033[0m")
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

def speichere_spielerdaten(spieler: Spieler) -> None:
    daten = [
        spieler.name,
        spieler.lebenspunkte,
        spieler.max_lebenspunkte,
        spieler.level_system.erfahrung,
        spieler.level_system.level,
        ';'.join([f"{g.name},{g.typ},{g.wert}" for g in spieler.gegenstände]),
        ';'.join([fähigkeit.name for fähigkeit in spieler.fähigkeiten]),
        spieler.kupfer,
        spieler.silber,
        spieler.gold,
        spieler.waffe.name if spieler.waffe else '',
        spieler.rüstung.name if spieler.rüstung else '',
        spieler.klasse,
        '|'.join([f"{q.name}|{q.beschreibung}|{q.belohnung[0]}|{q.belohnung[1]}|{q.belohnung[2]}|{q.ziel_typ}|{q.ziel_menge}|{q.abgeschlossen}|{q.fortschritt}" for q in spieler.quests])
    ]

    vorhandene_daten = []
    if os.path.exists(CSV_DATEI):
        with open(CSV_DATEI, 'r', newline='') as file:
            reader = csv.reader(file)
            vorhandene_daten = list(reader)

    with_kopfzeile = False
    expected_headers = [
        'Name', 'Lebenspunkte', 'MaxLebenspunkte', 'Erfahrung', 'Level',
        'Gegenstände', 'Fähigkeiten', 'Kupfer', 'Silber', 'Gold', 'Waffe', 'Rüstung', 'Klasse', 'Quests'
    ]
    if len(vorhandene_daten) == 0 or vorhandene_daten[0] != expected_headers:
        with_kopfzeile = True

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
        if with_kopfzeile:
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
                gegenstände = [Gegenstand(*name.split(',')) for name in row['Gegenstände'].split(';') if name]
                fähigkeiten = [Fähigkeit(name, 0, 0, 0) for name in row['Fähigkeiten'].split(';') if name]
                kupfer = int(row['Kupfer'])
                silber = int(row['Silber'])
                gold = int(row['Gold'])
                waffe = next((w for w in BENUTZBARE_GEGENSTAENDE if isinstance(w, Waffe) and w.name == row['Waffe']), None)
                rüstung = next((r for r in BENUTZBARE_GEGENSTAENDE if isinstance(r, Rüstung) and r.name == row['Rüstung']), None)
                klasse = row['Klasse']
                quests = [
                    Quest(
                        name=q[0],
                        beschreibung=q[1],
                        belohnung=(int(q[2]), int(q[3]), int(q[4])),
                        ziel_typ=q[5],
                        ziel_menge=int(q[6]),
                        abgeschlossen=q[7] == 'True',
                        fortschritt=int(q[8]) if q[8] else 0
                    )
                    for q in [quest.split('|') for quest in row['Quests'].split(';') if quest]
                ]

                # Erstelle die Instanz der entsprechenden Klasse
                spieler = Spieler(name, klasse, lebenspunkte, max_lebenspunkte, erfahrung, level, gegenstände, fähigkeiten)

                # Setze die zusätzlichen Attribute des Spielers
                spieler.kupfer = kupfer
                spieler.silber = silber
                spieler.gold = gold
                spieler.waffe = waffe
                spieler.rüstung = rüstung
                spieler.quests = quests

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
        'schwach': f"\033[31mAchtung! Du bist auf einen {gegner.name} gestoßen. Bereite dich auf einen Kampf vor!\033[0m",
        'mittel': f"\033[31mVorsicht! Ein wilder {gegner.name} kreuzt deinen Weg. Zeige ihm deine Stärke!\033[0m",
        'stark': f"\033[31mEin mächtiger {gegner.name} erscheint! Dies wird eine wahre Herausforderung!\033[0m",
        'boss': f"\033[31mEin epischer Kampf steht bevor! Der {gegner.name} fordert dich heraus!\033[0m"
    }
    print(einleitungen[gegner.typ])

  
# Update the `kampf` function to drop magical scrolls
def kampf(spieler: Spieler, gegner: Gegner) -> None:
    kampfeinleitung(gegner)
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
    if random.random() < 0.2:  # 20% Chance, einen NPC zu treffen
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

    print(f"{len(angebote) + 1}: Gegenstände verkaufen")
    print(f"{len(angebote) + 2}: Zum Hauptmenü zurückkehren")

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
                print("Du hast not genug Kupfer, Silber oder Gold.")
        elif choice == len(angebote) + 1:
            verkaufe_gegenstände(spieler)
        elif choice == len(angebote) + 2:
            return zeige_menü(spieler)
        else:
            print("Ungültige Wahl. Bitte versuche es erneut.")

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
        while spieler.kupfer >= 100:
            spieler.kupfer -= 100
            spieler.silber += 1
        while spieler.silber >= 100:
            spieler.silber -= 100
            spieler.gold += 1
        print(f"Du hast {ausgewählter_gegenstand.name} for {ausgewählter_gegenstand.wert} Kupfer verkauft.")
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
    print("3: Magische Schriftrolle verwenden")
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
        return zeige_menü(spieler)
    elif choice == '9':
        name = input("Gib deinen Spielernamen ein: ")
        spieler = lade_spielerdaten(name)
        if spieler:
            print(f"Willkommen zurück, {spieler.name}!")
            return zeige_menü(spieler)
        else:
            print("Spieler not gefanden. Neues Spiel starten.")
            return starte_spiel()
    elif choice == '10':
        spiel_beenden()
    else:
        print("Ungültige Wahl. Bitte versuche es erneut.")
        return zeige_menü(spieler)

def magische_schriftrolle_erlernen(spieler: Spieler) -> None:
    print("\033[34m**** Verfügbare magische Schriftrollen zum Erlernen: ****\033[0m")
    for i, schriftrolle in enumerate(spieler.gegenstände):
        if isinstance(schriftrolle, MagischeSchriftrolle):
            print(f"{i + 1}: {schriftrolle.name} - Schaden: {schriftrolle.schaden}, Mana-Kosten: {schriftrolle.mana_kosten}")
    choice = int(input("Wähle eine magische Schriftrolle (Nummer eingeben) oder 0, um zurückzukehren: "))
    if 1 <= choice <= len(spieler.gegenstände):
        ausgewählte_schriftrolle = spieler.gegenstände[choice - 1]
        if isinstance(ausgewählte_schriftrolle, MagischeSchriftrolle):
            if any(s.name == ausgewählte_schriftrolle.name for s in spieler.magische_schriftrollen):
                print(f"Du hast die Schriftrolle {ausgewählte_schriftrolle.name} bereits erlernt.")
            elif len(spieler.magische_schriftrollen) < 2:
                spieler.magische_schriftrollen.append(ausgewählte_schriftrolle)
                spieler.gegenstände.remove(ausgewählte_schriftrolle)
                print(f"Magische Schriftrolle {ausgewählte_schriftrolle.name} wurde erlernt.")
            else:
                print("Du kannst nur 2 magische Schriftrollen erlernen.")
    elif choice == 0:
        return zeige_menü(spieler)
    else:
        print("Ungültige Wahl.")
    return magische_schriftrolle_erlernen(spieler)


def erkunden(spieler: Spieler) -> None:
    position = 0
    while position < SPIELFELD_GROESSE and spieler.lebenspunkte > 0:
        input("\033[33mDrücke Enter, um zu würfeln...\033[0m")
        wurf = random.randint(1, 6)
        position += wurf
        position = min(position, SPIELFELD_GROESSE - 1)
        print(f"Der Spieler würfelt eine {wurf} and bewegt sich auf Feld {position}.")
        if spieler.spielfeld[position] is not None:
            kampf(spieler, spieler.spielfeld[position])
            if spieler.lebenspunkte <= 0:
                print("Der Spieler hat keine Lebenspunkte mehr and verliert das Spiel.")
                break
        else:
            npc_treffen(spieler)
        if position >= SPIELFELD_GROESSE - 1:
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
