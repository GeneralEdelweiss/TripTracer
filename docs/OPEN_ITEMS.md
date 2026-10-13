# Offene Punkte (Stand V0.3)

1. Schaltplan in KiCad 10 laden und native ERC-Pruefung durchfuehren.
2. Komplettes PCB layouten und nach JLCPCB-Regeln DRC pruefen. Der V0.1-Placement-Entwurf ist explizit kein Fertigungs-PCB.
3. Automobilversorgung: Load Dump, Transienten, ESD/EMV, Verpolung, Sicherung und Temperaturbelastung nachweisen.
4. 3.3-V-Buck-Spule, Kondensator-Derating, Ripple und thermische Auslegung pruefen.
5. GNSS-Antenne und Bias-T (50 Ohm, aktive Antenne) am konkreten Aufbau testen.
6. LCD-40-Pin-Layout, Modulabmessungen und Ladungspumpen-Kondensatoren gegen Herstellerunterlagen pruefen.
7. USB-C: VBUS versorgt laut V0.3 nicht das Geraet; Firmwareflash erfordert zusaetzlich J1.
8. Firmware V0.1 mit V0.3-Schaltplan abgleichen, ESP32-S3-Build und 10-Hz-GNSS-Konfiguration testen.
9. Mechanik V0.1: Druck- und Passprobe; Schalterhoehe, Dichtung, Vibration und Antennenanschluss bestaetigen.
10. Bibliothek: 3D-Modelle sind teils vereinfachte Geometrien, keine freigegebenen Hersteller-CAD-Modelle.

Nichts hiervon darf als abgeschlossen oder getestet bezeichnet werden, bevor ein konkreter Testbericht existiert.
