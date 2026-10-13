# 6-V-Motorstart: Kernlast und Spannungsreserve getrennt prüfen

14.10.2026. **36 rechnerische Sensitivitätsszenarien; kein bestandener 6-V-Test.**

PWR-15/17 fordert bei mindestens 6 V an BAT+ stabilen MCU/GNSS/SD/FRAM- und Messbetrieb. Hintergrundbeleuchtung darf aussetzen; Anzeigeelektronik soll weiterlaufen. Das ist nicht automatisch die volle 5-V-/2-A-Leistung während des Motorstarts. **5 V/2 A im normalen 9–30-V-Bereich bleiben Entwicklungsziel.** Kein Lastbudget wurde erfunden oder zugesagte Kernfunktion abgeschwächt.

[TI LMR36520, Rev. C, elektrische Eigenschaften/Systemmerkmale](https://www.ti.com/lit/ds/symlink/lmr36520.pdf) nennt HS-RDS(on) maximal 465 mOhm, LS maximal 310 mOhm sowie 98 % maximalen Duty als typisches Systemmerkmal. HS-Stromlimit beträgt 2,4/3,0/3,6 A (min/typ/max); TI weist ausdrücklich auf Unterschiede zwischen produktionsgeprüfter offener Schleife und Anwendung mit geschlossener Schleife hin. Diese Daten sind keine garantierte 2-A-/6-V-Systemzusage.

Modell: angenommener Duty 0,98; Induktor-DCR heiß pauschal 1,4 × 68 mOhm; komplette Frontend-Widerstandsszenarien 0,1/0,25/0,5 Ohm; Buck-Wirkungsgrad angenommen 80/90 %. Frontend-R ist **kein festgelegter FET-/Shunt-/Kabelwert**. Lastfälle 0,25/0,5/0,75/1/1,5/2 A sind hypothetische Sensitivitäten, kein gemessenes Gerätebudget.

Vbuck_min = (5 V + Iout × [D×RHS+(1−D)×RLS+RL]) / D.
Iin = 5 V × Iout / (η × Vbuck_min).
Vbat_min = Vbuck_min + Iin × Rfrontend.

| Beispiel, Frontend 0,5 Ohm / η=80 % | Berechneter BAT+-Bedarf |
|---|---:|
| 0,25 A Ausgangslast | 5,393 V |
| 0,50 A | 5,676 V |
| 0,75 A | 5,952 V |
| 1,00 A | 6,222 V |
| 1,50 A | 6,742 V |
| 2,00 A | 7,241 V |

Die positiven Reserven sind **kein garantierter Startnachweis**; 0,75 A hat in diesem Szenario bereits nur 48 mV Reserve. PWM-Frequenzabsenkung, dynamischer Motorstart, VS-/Charge-Pump-Bootstrap, FET-Gates, Kälte-/Heißinduktivität, Regelschleife, LDO-Mindestspannung und Lastsprünge fehlen. Die Modelle mit heißem RDS(on) und angenommener Induktivität sind keine vollständig korrelierten garantierten Eckwerte.

Zusätzlich liegt die idealisierte 2-A-Spitze bei 30 V/8 µH/340 kHz bei 2,766 A, oberhalb des tabellierten HS-Limits von mindestens 2,4 A. Das allein beweist **kein** Versagen des TI-Referenzentwurfs, kennzeichnet aber fehlende Stromreserve im einfachen Modell. Referenz-10-µH-Auslegung nicht blind durch eine andere Induktivität ersetzen; Hersteller-Regelbereich, Verlustleistung, Bias und reale Volllast zuerst prüfen.

Nächster notwendiger Schritt: tatsächliche Kernlast einschließlich MCU/GNSS/SD-Schreibspitzen, Displaylogik und Sensoren messen bzw. mit maximalen Herstellerwerten budgetieren; Backlight-Dimming beim Motorstart als bereits erlaubten Betriebszustand berücksichtigen. Daraus Frontend-RDS(on), Gate-/VS-Versorgung und Buck-Dropout dimensionieren. Keine beliebige Reduktion des 2-A-Normalbetriebs, kein zusätzlicher Controller oder Energiespeicher ohne nachgewiesenen Bedarf. Preis-/BOM unverändert; nur Auslegungsrechnung ergänzt.

## Hersteller-Grundlagen der Kernlast

[Partielle Kernlast-Eingaben](../../CORE_POWER_BUDGET.md) unterscheiden MCU-Versorgungskapazität, GNSS-Anlauf und typische 1-Hz-Ströme von dem noch unbekannten 5-Hz-/SD-/Display-Spitzenbedarf. Kein vollständiges Budget.
