# ACC/HOLD: irreversible Abschaltung pro ACC-Zyklus

Stand 14.10.2026. Gegenueber dem bisherigen Behavioral-Modell wird **jede** Deaktivierung waehrend ACC AUS verriegelt, auch wenn die nominelle Timeout-Frist noch laeuft. Implementierung im Referenzmodell: `tools/test_acc_hold_state_machine.py`, Commit `39d2547`.

## Motivation

Bisher war die Freigabe waehrend ACC AUS nur `HOLD_REQ AND VEHICLE_5V AND TIMER_WINDOW`. Falls HOLD_REQ nach einem geordneten Dateischluss auf LOW ging und durch Firmware-/GPIO-Fehler wieder HIGH wurde, konnte MAIN_ENABLE im verbleibenden Zeitfenster erneut aktiv werden. Auch ein voruebergehender Einbruch der Fahrzeug-5-V-Versorgung konnte einen erneuten Start verursachen. Die selbsthaltende Versorgung darf nach ihrem ersten OFF-Ereignis ohne neues gueltiges ACC EIN **nicht erneut starten**.

## Soll-Zustandsautomat

| Zustand | Eingang / Ereignis | Neuer Zustand / MAIN_ENABLE |
| --- | --- | --- |
| OFF_LOCKED | ACC_VALID=0, beliebiges HOLD, USB-only oder BAT+ | OFF_LOCKED / 0 |
| OFF_LOCKED | qualifiziertes ACC_VALID=1 | ACC_ON / 1 |
| ACC_ON | ACC_VALID=1 | ACC_ON / 1 |
| ACC_ON | qualifiziertes ACC_VALID 1→0 und Fahrzeug-5V gueltig und HOLD_REQ=1 | HOLD_WINDOW / 1 |
| ACC_ON | ACC-Abfall ohne gueltige Haltebedingungen | OFF_LOCKED / 0 |
| HOLD_WINDOW | HOLD_REQ=1, Fahrzeug-5V gueltig, Zeitfenster noch offen | HOLD_WINDOW / 1 |
| HOLD_WINDOW | HOLD_REQ=0 **oder** Fahrzeug-5V ungueltig **oder** Deadline abgelaufen | OFF_LOCKED / 0 |
| HOLD_WINDOW | qualifiziertes ACC_VALID=1 | ACC_ON / 1 |

`USB_5V` darf den Fahrzeug-5V-Qualifikator nicht treiben. Eine echte ACC-EIN-Qualifikation ist notwendig, um aus OFF_LOCKED wieder herauszukommen. Der gewaehlte Testwert von 30 s ist nicht die freigegebene Zeit.

## Hardware-Realisierung: wesentliche Sperrpunkte

Ein einfaches OR aus ACC und Timer-OUT oder ein reines nicht retriggerbares Monoflop erfuellt diese Zustandsmaschine **nicht**. Es braucht ein physisches verriegelndes Sperrelement, dessen RESET nur durch echtes, gefiltertes ACC EIN erfolgt. Nach Verlust von V5_BUCK_RAW muss eine Kombination aus passiven Defaults und Schaltzustand verhindern, dass der Hauptpfad unabsichtlich wieder aufstartet. Ein nur aus V5_BUCK_RAW gespeistes Flipflop speichert nach dessen Wegfall seinen Zustand nicht garantiert; beim Restart ist dessen Power-On-Default nachzuweisen. Reset-/Set-Prioritaet, Triggerentprellung, Schmitt-Schwellen, Synchronisations- und Versorgungsluecken sind daher noch nicht ausgelegt.

**Konstruktiver Vorbehalt:** Die Logik muss im echten Pfad 6 V Motorstart und ACC-Uebergaenge aushalten. Dieser Testcode ist keine Schaltungssimulation, kein Nachweis der Peripherieversorgung und kein KiCad/ERC-/DRC-Ergebnis. Die vorhandene LM74930-/LMR36520-Architektur sowie fahrzeugseitige Absicherung bleiben unveraendert.

## Naechste Hardwarearbeiten

1. Physikalische OFF_LOCKED-Verriegelung mit definiertem Zustand bei kollabierendem Fahrzeug-5V entwickeln.
2. ACC-Validierung einschliesslich Wiederanlauf nach echtem ACC-Neustart und Kontaktflattern dimensionieren.
3. LTC6993-3 versus TLC555-Q1 als **komplette Schaltung einschliesslich Sperre** in Pinout, Ruhestrom und Einkaufskosten vergleichen.
4. MCU_HOLD-Ausgang beim Power-up, Brownout, USB-only, offenen/kurzgeschlossenen GPIO und festhaengendem HIGH pruefen.
5. Erst nach funktionsfaehiger elektrischer Netztopologie Unterseite in KiCad 10 aendern, native ERC-/DRC- und realistische SPICE-Tests durchfuehren.

Kostenstand: **NICHT BELASTBAR**. Keine neue Bestellung, kein freigegebener Timer-MPN.
