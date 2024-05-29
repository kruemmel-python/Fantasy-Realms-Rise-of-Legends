# Herz der Mutigen: Das Schicksal des Königreichs

## Über das Spiel

"Herz der Mutigen: Das Schicksal des Königreichs" ist ein textbasiertes Abenteuerspiel, das dich in die Rolle eines mutigen Helden versetzt. Deine Mission ist es, das zerstückelte Land zu vereinen und den Frieden wiederherzustellen, indem du furchterregende Kreaturen besiegst, Rätsel löst und mächtige Artefakte sammelst. Dein ultimatives Ziel ist es, das legendäre Artefakt "Herz der Mutigen" zu finden und die Dunkelheit zu vertreiben.

## Spielanleitung

1. Klone das Repository und navigiere in das entsprechende Verzeichnis.
2. Führe das Spiel aus, indem du `python SchicksalDesKoenigreichs.py` in deiner Konsole eingibst.
3. Folge den Anweisungen auf dem Bildschirm, um deinen Charakter zu erstellen und dein Abenteuer zu beginnen.

## Features

- Dynamisches Level-System: Sammle Erfahrungspunkte und steige im Level auf, um deine Fähigkeiten zu verbessern.
- Vielfältige Gegner: Stelle dich einer Reihe von Gegnern, von schwachen Kobolden bis hin zu mächtigen Drachen. Sie alle werden stärke mit jeden Levelaufstieg deines Spielcharacters.
- Inventarsystem: Sammle Gegenstände und Fähigkeiten, die dir auf deiner Reise helfen werden.
- Spannende Kämpfe: Nutze Strategie und Geschick, um in rundenbasierten Kämpfen zu triumphieren.

## Mitwirken

Ich freue mich über Beiträge von der Community! Bitte lese `CONTRIBUTING.md` für Details zu meinem Code of Conduct und dem Prozess für das Einreichen von Pull Requests.

## Lizenz

Dieses Projekt ist unter Lizenz lizenziert - siehe die `LICENSE.md`-Datei für Details.

## Danksagungen

- besonderer Dank geht an karriere tutor® https://www.karrieretutor.de deren Dozenten (Boris Dreyer und Michael Schmitz), die mich im Laufe meiner Schulung, auf diese Idee gebracht haben.


Das Spiel "Schicksal des Königreichs" ist ein textbasiertes Rollenspiel, das in Python programmiert wurde. Hier ist eine ausführliche Beschreibung des Spiels:

**Spielkonzept:**
- Spieler beginnen ihr Abenteuer mit einer festgelegten Anzahl von Lebenspunkten und können verschiedene Gegenstände und Fähigkeiten sammeln.
- Das Ziel ist es, durch ein Spielfeld zu navigieren, das mit Gegnern verschiedener Stärke gefüllt ist.
- Spieler können Erfahrungspunkte sammeln, um im Level aufzusteigen, was ihre Lebenspunkte erhöht und sie stärker macht.

**Hauptmerkmale:**
- **Gegner:** Es gibt drei Typen von Gegnern – schwach, mittel und stark – mit jeweils unterschiedlichen Lebenspunkten und Schadenswerten.
- **Level-System:** Spieler können Erfahrungspunkte sammeln und im Level aufsteigen, was ihre maximalen Lebenspunkte erhöht.
- **Gegenstände:** Spieler können Gegenstände wie Heiltränke finden und verwenden, um ihre Lebenspunkte zu regenerieren.
- **Fähigkeiten:** Spieler können spezielle Fähigkeiten erlernen, die im Kampf gegen Gegner eingesetzt werden können.
- **Kämpfe:** Spieler treten in rundenbasierten Kämpfen gegen Gegner an, wobei sie abwechselnd angreifen.
- **Speichern und Laden:** Spielerdaten können in einer CSV-Datei gespeichert und geladen werden, um den Fortschritt zu behalten.

**Spielablauf:**
1. Das Spiel beginnt mit einer Einführungsgeschichte, die den Hintergrund und das Ziel des Spiels erläutert.
2. Spieler geben ihren Namen ein und starten entweder ein neues Spiel oder laden einen bestehenden Spielstand.
3. Auf dem Spielfeld würfeln die Spieler, um sich fortzubewegen, und treffen auf Gegner, mit denen sie kämpfen müssen.
4. Nach jedem gewonnenen Kampf haben die Spieler die Möglichkeit, Heiltränke zu finden und ihre Lebenspunkte zu regenerieren.
5. Das Spiel endet, wenn der Spieler das Ende des Spielfelds erreicht oder keine Lebenspunkte mehr hat.

**Technische Details:**
- Das Spiel verwendet die `random`-Bibliothek für Zufallsereignisse wie Würfelwürfe und das Finden von Gegenständen.
- Es gibt Klassen für Gegenstände, Fähigkeiten, das Level-System, Gegner und den Spieler, die die Logik des Spiels definieren.
- Funktionen ermöglichen das Speichern und Laden von Spielerdaten sowie das Erstellen des Spielfelds und das Durchführen von Kämpfen.

Das Spiel bietet eine interaktive Erfahrung, bei der Entscheidungen und Zufallselemente das Ergebnis beeinflussen. Es ist eine gute Übung für Programmieranfänger, um objektorientierte Programmierung und Dateiverwaltung in Python zu lernen.

