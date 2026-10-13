# Kernlast: Herstellerdaten und noch fehlendes Leistungsbudget

14.10.2026. **Teilweise quellenbasierte Eingaben, kein vollständiges Strombudget und keine Messung.** 5 V/2 A im normalen 9–30-V-Bereich sowie der stabile Kernbetrieb ab 6 V bleiben unverändert. Keine Architektur-/Bauteiländerung beschlossen.

## Geprüfte Bauteile

[Espressif ESP32-S3-MINI-1/1U v1.7, Abschnitte 6.2/6.4](https://www.espressif.com/sites/default/files/documentation/esp32-s3-mini-1_mini-1u_datasheet_en.pdf): Versorgung 3,0–3,6 V; externe Versorgung soll mindestens 0,5 A liefern können. Das ist **Versorgungskapazität, kein gemessener Dauerstrom**. WiFi-TX wird bei 3,3 V/25 °C mit 355 mA Spitze angegeben; Bluetooth-TX bei hoher Sendeleistung mit 340 mA. Modem-sleep-Werte bis 107,9 mA sind typische CPU-/Peripherie-Szenarien; Flashzugriffe können zusätzlich Strom benötigen. Daraus keinen garantierten vollständigen MCU-/Firmware-Spitzenwert über Temperatur ableiten.

[u-blox MAX-M10N-00B R05, Abschnitt 4.3](https://content.u-blox.com/sites/default/files/documents/MAX-M10N-00B_DataSheet_UBXDOC-963802114-13143.pdf): VCC-Inrush bis 100 mA; Versorgung dafür auslegen. Bei 3,0 V, 1 Hz und GPS+Galileo+BeiDou nennt die Tabelle typisch 7 mA VCC beim Tracking plus 3,7 mA V_IO; Acquisition 9,5+3,7 mA. TripTracer verwendet **5 Hz**, deshalb sind diese 1-Hz-Werte kein geeigneter garantierter 5-Hz-Lastwert. Aktive Antenne und deren Bias-Versorgung separat addieren. MAX-M10S ist ein anderes Teil und wurde nicht als Stromquelle für MAX-M10N übernommen.

## Noch fehlende Eingaben

| Last | Benötigter Nachweis |
|---|---|
| microSD, 32 GB FAT32 | Konkrete Karte/MPN; Schreib-, Erase-, Flush-/Power-up-Spitzen und Dauer; Messung auch nach Alterung/Füllstand |
| Riverdi RVT35HITNWC00-B | Displaylogik getrennt von Backlight, Controllerzustände und Bootstrom |
| FRAM/RTC/Licht-/Temperatursensoren | Exakte MPNs, maximal aktive/Standby-Ströme und gleichzeitige Busaktivität |
| Radsensoren und Taster-LEDs | Tatsächliche Sensor-/LED-Ströme, Motorstart-Betriebszustand und Rückspeisung |
| 3V3-/USB-/SD-Lastschalter | Regler-/Schalter-Eigenstrom, USB-only-Service und Flankenlast |

Unbekannte Werte stehen in source-inputs.json als null, nicht als 0 mA. Die fehlenden Lasten dürfen nicht aus dem Budget verschwinden.

## Konsequenz für 6 V und 3V3

Eine **vorläufige Kapazitätsreservierung**, 500 mA für MCU plus 100 mA GNSS-Start, ergibt 600 mA und lässt SD/Displaylogik/Antennenbias/Rest noch vollständig offen. Das ist **kein gemessener oder garantierter simultaner Geräteverbrauch**. Lastsequenz und Betriebsmodi müssen die Reserven tatsächlich belegen.

Würde eine lineare 5→3,3-V-Stufe 600 mA führen, ergäbe allein ihr Spannungsabfall rechnerisch **1,02 W** Verlustleistung, ohne Eigenstrom. Die 5-V-Quelle sieht dabei ungefähr denselben Strom wie die 3,3-V-Last, nicht nur 3,3/5 ihres Wertes. LDO-Thermik/Kupferfläche und Spitzenstrom sind deshalb vor Festlegung der noch leeren 03_3V3_USB-Seite zu prüfen. Keine automatischen 1-W-Freigaben für kleine SOT-Gehäuse.

[Dropout-Sensitivitäten](validation/2026-10-14-motor-start-headroom/README.md) zeigen, dass eine hohe Kernlast mit heißem, hochohmigem Frontend die 6-V-Reserve aufbrauchen kann. Erlaubtes Backlight-Dimming ersetzt keinen Nachweis der weiterlaufenden Anzeigeelektronik/MCU/GNSS/SD. Tatsächliche Last-/Temperaturwerte und Frontend-FETs bestimmen den nächsten Schaltungsschritt. Ein 3V3-Schaltregler wäre erst nach Strom-/Thermik-/Gesamtkostenvergleich eine begründete Alternative, keine jetzt beschlossene Zusatzbaugruppe.

Kosten/BOM derzeit unverändert; kein neuer Controller, keine Bestellung, keine bewusste Verkleinerung des Funktionsumfangs. Vollständige Kernauslegung bleibt offen. Quellenwerte maschinenlesbar in [source-inputs.json](validation/2026-10-14-core-load-sources/source-inputs.json).
