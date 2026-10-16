# TripPower / TripTracer – verbindliche Entscheidung zur Sicherungsplatzierung (16.10.2026)

**Nutzerentscheidung – gilt für TripPower V1 REV6 und alle Entwicklungswege A, B, C, D.** Ergänzt [REV6-Praxisanforderungen](TRIPPOWER_V1_PRACTICAL_REQUIREMENTS_REV6_2026-10-15.md) und [Hardwareanforderungen](HARDWARE_REQUIREMENTS.md) PWR-05/PWR-55/PWR-56. Historische Berichte und Stücklisten dürfen Sicherungen/halter nur dann als **TripPower-Bestückung** interpretieren, wenn es sich um einen neuen ausdrücklich genehmigten Entwurf handelt – diese Genehmigung gibt es derzeit **nicht**.

## 1. Harte Bestückungsgrenze

- **Auf der kleinen, abnehmbaren TripPower-Platine gibt es keine konventionelle Schmelzsicherung, keinen Sicherungshalter und keine einmalig auslösende SMD-Schmelz-/Thermosicherung.** Kein F_MAIN/F302/MINI/ATO/SMD-One-Shot-Element in KiCad-TripPower-Schaltplan oder in der TripPower-BOM.
- Eine austauschbare konventionelle Sicherung darf in der **Fahrzeugzuleitung vor dem Gerät** bzw. als **zusätzliche zugängliche Gerätesicherung auf der größeren TripTracer-Hauptplatine** sitzen. Eine Sicherung auf der Hauptplatine schützt **nicht** die davorliegende Strecke von Batterie/Abgriff bis zum Gerät; die speisende ACC- bzw. BAT+-Leitung muss deshalb schon **möglichst nahe an ihrer Energiequelle** passend abgesichert sein oder aus einem passend abgesicherten Fahrzeugabgriff kommen. Hauptplatinen-Fuse ist kein Ersatz für vorgeschalteten Kabelschutz.
- **Allenfalls optional** auf TripPower: kleine **rückstellende SMD-PPTC/Polyfuse** (oder eine tatsächlich automatisch rückstellende geeignete Temperaturschutzvorrichtung), **kein Einmal-Thermofuse**. Sie wird nach Überstrom-/Temperaturereignis hochohmig und kehrt nach Abkühlen/Fehlerbeseitigung ohne Auslöten zurück, sofern in ihrer spezifizierten Anwendung und unter geeigneten Bedingungen betrieben. Ein PPTC ist keine galvanisch öffnende Schmelzsicherung und kann im Tripzustand nennenswerten Reststrom führen.
- **PTC ist keine Pflicht!** Wenn ein passender elektronischer Überstromschutz/eFuse und extern vorschriftsmäßig abgesicherte Leitung alle Fehler abdecken, werden **keine zusätzlichen PTC-Positionen aus Vorsicht** eingebaut. Weniger Bauteile ist ein positives Kriterium, nie Ersatz für einen funktionalen Nachweis.

## 2. Fachliche Auslegungs-/Prüfgates

- Eine optional gewählte PPTC muss hinsichtlich **maximal zulässiger Spannung an ihrem eigenen Pad** (REV6 normal10–32V, 36V/400ms, begrenzter58V/350ms am Moduleingang *plus lokale Transienten*), Fehler-/Kurzschlussstrom, Temperatur, **I_hold(T)**/**I_trip(T)**, Ruhestrom/Leckstrom, Trip- und Rückstellzeit, Leistung im ausgelösten Zustand, Alterung und Pulswiederholung mit Herstellerangaben qualifiziert sein. Nur wenn die konkrete PPTC das ermöglicht, darf sie eingesetzt werden; Standard-30V-/32V-PPTCs nicht pauschal für 58V qualifiziert deklarieren.
- **PPTC ersetzt weder** die vorgeschaltete, austauschbare Leitungssicherung mit korrektem DC-Ausschaltvermögen, **noch** OVP/Verpol-/Rückspeisepfad, **noch** eine ggf. nötige schnelle elektronische Strombegrenzung für RAW0,5A. Manche PPTCs sprechen zu langsam oder bei hohen/wechselnden Temperaturen zu früh an; bei +60°C Volllast einen Fehl-Trip ausschließen, bei dauerndem Fehler gefährliche Erwärmung verhindern.
- Sicherungs-/Halter-Teile, DC-Interrupt-Rating, Kabelquerschnitt und Installationsanforderungen dürfen im **System-/Fahrzeug-Harness-Kostenregister** enthalten sein, aber **nicht als auf TripPower zu bestückende Bauteile** gezählt werden. Im Vergleich stets getrennt erfassen: (a) bestückte TripPower-Positionen, (b) Komponenten auf TripTracer, (c) Fahrzeugzuleitung und Sicherung.
- Einbau nur in nachweislich zentral begrenzte 12-/24V-Bordnetze. Die Wahl der Stelle und Spannungsklasse der Fahrzeugleitungssicherung darf die 58V-/350ms- und Kurzschluss-Fehlerprofilgrenzen nicht ignorieren.

## 3. Arbeitsauftrag an alle Wege

A: Separate REV6-KiCad-BOM **ohne** Hauptsicherung/halter; optional PPTC nur bei vollständiger belegter Eignung. B: Vor-Ort-Sicherung/halter/Kabel gegen Fehler prüfen, ohne daraus eine TripPower-PCB-Forderung abzuleiten. C: alle Varianten in gleicher BOM-Grenze erfassen. D: gefundene 58VDC-MINI-/Halterkombination dem **Fahrzeug-Harness/TripTracer-System** zuweisen; nicht in die kleine TripPower-Platine zeichnen.

**Status:** verbindliche Architektur-/BOM-Randbedingung; daraus folgt **keine automatische Sicherheits- oder Fertigungsfreigabe**.
