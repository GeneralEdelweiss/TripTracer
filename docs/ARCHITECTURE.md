# TripTracer – Hardwarekonzept

Stand: Elektronik V0.3; Mechanik/Firmware V0.1

| Baugruppe | Festgelegter Baustein / Funktion |
| --- | --- |
| Steuerung | ESP32-S3-MINI-1-N8 |
| GPS/GNSS | u-blox MAX-M10N-00B, U.FL-Antennenanschluss |
| Anzeige | EA DOGL128W-6, 128 × 64 Pixel, transflektiv |
| Beleuchtung | EA LED68X51-A, amber, per PWM geregelt |
| Versorgung | 12-V-Eingang mit Sicherung/TVS, TI LMR36510ADDAR auf 3,3 V |
| Datenspeicher | MB85RC256VPNF, I²C-FRAM |
| Bedienung | 5 Fronttasten, separater MCU-Reset/BOOT |
| USB | USB-C für Daten/Flashen, keine USB-Speisung der Elektronik in V0.3 |
| Gehäuse | 3D-Druck, grober Frontentwurf 126 × 76 mm, bevorzugt ASA |
| Platinenkonzept | ca. 118 × 68 mm im V0.1-Entwurf; noch kein geroutetes Produktionslayout |

Die Bauteile sind auf einer gemeinsamen Trägerplatine vorgesehen. Ein vollständiger Test unter realen Fahrzeugbedingungen steht aus.
