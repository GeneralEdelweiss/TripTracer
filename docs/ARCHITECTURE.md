# TripTracer Architektur (aus dem KiCad-V0.3-Entwurf)

- Zweck: universeller GPS-Tripmaster fuer Rallye, Touren und Fahrzeuge, nicht auf Offroad beschraenkt.
- Steuerung: ESP32-S3-MINI-1-N8, USB-C zum Flashen, J1 als 12-V-Betriebsversorgung.
- GNSS: u-blox MAX-M10N-00B mit U.FL und optionaler aktiver Antenne.
- Anzeige: Display Visions EA DOGL128W-6 (128x64, transflektiv) und EA LED68X51-A (Amber-LED-Backlight); PWM-Treiber.
- Bedienung: 5 Fronttaster, separater Boot/Reset; externer Trip-Reset-Anschluss.
- Speicherung: FRAM MB85RC256VPNF per I2C im V0.3-Schaltplan vorgesehen.
- Stromversorgung: 12 V -> Schutzkonzept (F1, D1, TVS) -> TI LMR36510ADDAR -> 3.3 V.
- V0.1-Mechanik: Front ca. 126x76 mm; PCB-Konzept 118x68 mm; ASA-Gehaeuse, 3D-Druck.

**Revisionsstand:** V0.3 ist ein Schaltplan-Prototyp ohne KiCad ERC/DRC oder Fahrzeugfreigabe. 
**Firmwarestand:** V0.1 ist experimentell, nicht gegen V0.3 abgeglichen.

## Beschlossene Anforderungen fuer die naechste Hardware-Revision (noch nicht in V0.3)

**Portabler Einsatz in mehreren Fahrzeugen:** Der TripTracer bleibt ein einziges, leicht umsteckbares Geraet. In jedem Auto/Motorrad kann eine eigene mechanische Schnellwechselhalterung und 12-V-Leitung fest installiert werden.

- **Hauptversorgung ueber M8 A-codiert, 3-polig, verschraubt:** maennlicher Einbaustecker am TripTracer-Gehaeuse, weibliche abgedichtete Kabelkupplung am Fahrzeug. **Geraetesicherung auf der PCB** unmittelbar nach dem 12-V-Eingang. Einfaches, selbst angefertigtes Fahrzeugkabel ohne zusaetzlichen geraetespezifischen Sicherungshalter. **Wichtig:** Der 12-V-Fahrzeugabgriff bzw. die Zuleitung muss bereits an der Quelle abgesichert sein; bei Direktanschluss an die Batterie bleibt eine separate Sicherung nahe der Batterie erforderlich.
- Angestrebte M8-Anschlussbelegung: **Pin 1 = +12 V, Pin 3 = GND, Pin 4 = Reserve / NC**. Pinbelegung am konkreten Stecker und der mating-face-Zeichnung verifizieren.
- M8-Einbaustecker in der Gehaeusewand befestigen und mechanisch entlastet zur Platine verdrahten; nicht die Leiterplattenloetstellen als Gehaeusehalter verwenden.
- **USB-C mit 5 V** fuer Firmwareupdates, USB-Daten und eine alternative Versorgung (z. B. PC oder geeigneter 12-V-Zigarettenanzuender-auf-5-V-USB-C-Adapter). Am USB-C-Stecker niemals rohe 12 V aus dem Fahrzeug anlegen.
- Bordnetzschutzeingang (12 V) und USB-5-V-Eingang muessen **gegeneinander rueckspeisungssicher** sein, auch bei gleichzeitigem Anschluss. USB-Spezifikation und 5-V-Strombudget pruefen.
- Schnelle werkzeuglose Schiebe-/Rasthalterung je Fahrzeug vorsehen; M8 bleibt der separate, gegen Vibration gesicherte elektrische Anschluss.
- Maximalstrom, Spannungsbereich und Freigabe des konkret bestellten M8-Steckers samt Leitung und Sicherung gegen die Gesamtlast verifizieren.
- M8 A-codiert ist ein industrieller Sensorkonnektor; gegen versehentliches Einstecken in fremde 24-V-Sensorleitungen durch eindeutige Markierung und robusten Eingangsschutz vorsorgen.

**Status:** Beschlossene Anschluss- und Nutzungsvorgaben, **noch keine Umsetzung im KiCad-V0.3-Schaltplan**, keine elektrische oder mechanische Freigabe. Aktueller Bestand nutzt J1 als 12-V-Eingang und USB nur fuer Daten.

**Zentrale Hardware-Anforderungen fuer die naechste Revision:** [HARDWARE_REQUIREMENTS.md](HARDWARE_REQUIREMENTS.md). Anforderungen und Bauteilauswahl daraus ableiten; Bestand V0.3 nicht mit Freigabe verwechseln.
