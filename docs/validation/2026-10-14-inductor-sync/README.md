# L101 auf ausgewählte Bourns-Spule synchronisiert

14.10.2026. **Keine Fertigungs-/Thermikfreigabe.** Ausgangsstand 530e04f.

Schaltplan: SRP6030VA-100M, 10 µH. PCB zuvor: alte SRN6045-Bauform für 22 µH. L101 wurde an unveränderter Position/Orientierung durch den bereits vorhandenen lokalen SRP6030VA-Footprint ersetzt. PCB-UUID und Schaltplanpfad sowie sämtliche vorhandenen PCB-Pad-Netze erhalten. Der vollständige Root-Netzlistenvergleich bestätigt unveränderte 260 Pin-Netz-Zuordnungen. Wert präzisiert auf **Isat typ 5A** in Schaltplan/PCB; keine garantierte 5-A-Sättigungsgrenze behaupten.

## Hersteller-Geometrie

[Bourns SRP6030VA, Seite 1](https://www.bourns.com/docs/product-datasheets/SRP6030VA.pdf): Empfohlener Landpattern außen 8,0 mm, innen 3,7 mm, Höhe 3,4 mm. Daraus zwei Pads 2,15 × 3,4 mm mit Mittelpunkten ±2,925 mm. Native pcbnew-Ladung nach Save/Reload bestätigt diese Maße und zwei Padnummern. Nicht polarisiertes Induktorelement. Datenblatt-Zeichnung einschließlich Landpattern visuell geprüft. Courtyard erweitert auf x=±4,25 mm, damit 0,25 mm Platz außerhalb der äußeren Kupferpadkante besteht; y=±3,8 mm unverändert. Maximale Bauteilabmessungen 7,4 × 6,8 mm liegen innerhalb. Kein erfundenes 3D-Modell: Gehäuse-/Höhen-/Bestückungskollisionen weiterhin offen.

Elektrisch nennt Bourns 10 µH ±20 %, DCR maximal 68 mOhm bei 25 °C sowie Irms/Isat jeweils **typisch** 5 A. Isat beschreibt 30 % Induktivitätsabfall; Irms 40 °C Temperaturanstieg unter Herstellerbedingungen. Diese Angaben sind keine garantierte Entwurfsreserve über alle Temperaturen oder ein Test unseres Boards.

## Rechenszenarien

[TI LMR36520, Rev. C](https://www.ti.com/lit/ds/symlink/lmr36520.pdf) nennt für die 400-kHz-Variante 340–460 kHz und im 5-V-Beispiel 10 µH. Die reproduzierbare Rechnung in tools/calculate_power_corners.py verwendet idealisierten CCM-Ripple bei 2 A Last. Bei 30 V/10 µH/400 kHz: Spitzenstrom 2,521 A. Bei 8 µH/340 kHz: 2,766 A, RMS 2,048 A, allein DCR-Verlust bei 25 °C etwa 0,285 W. Zusätzliche 6-µH-Sensitivität ergibt 3,021 A Spitze; **angenommener Biasfall**, kein garantierter Datenblattwert.

Die ±20-%-Anfangstoleranz deckt Strom-/Temperatur-Induktivitätsverlust nicht ab. Kernverluste, DCR-Anstieg, heißer Sättigungs-/Kurzschlussfall, Regelschleife, EMI und 6-V-Dropout noch prüfen. Keine Übernahme des typischen 5-A-Werts als garantierte Kurzschlussgrenze.

## Tatsächliche DRC-Ausgabe

Weiterhin 6 DRC-Meldungen (4 USB-Lochabstände, fehlender Umriss, U201-Library-Abweichung) und 79 unverbundene Verbindungen. Parität von 45 auf **43 ausschließlich fehlende Footprints** gesenkt; beide L101-Abweichungen behoben. Keine neue DRC-Meldung durch größeren Spulen-Footprint. Kein Routing ergänzt, keine Warnung ausgeschlossen.

Kosten: bereits ausgewählter Spulentyp, keine zusätzliche BOM-Position oder Bestellung. Aktueller deutscher Warenkorb/2-/10-/100-Gerätepreis ungeprüft; bestehende Preisansätze bleiben keine Beschaffungsfreigabe. Native Berichte und Rechenszenarien liegen in diesem Verzeichnis.
