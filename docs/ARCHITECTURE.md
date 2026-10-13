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
