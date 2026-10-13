# Einmaliger Dateiupload

Der bisherige Tripmaster-Schaltplan V0.3 mit allen vorhandenen KiCad-10-Libraries und 3D-Modellen sowie die noch aktuellen Gehäuse- und Firmwareartefakte V0.1 sind in **TripTracer-Project-Bundle.zip** zusammengefasst.

1. Von ChatGPT das **TripTracer-Project-Bundle.zip** herunterladen.
2. In diesem Ordner auf GitHub `Add file → Upload files` wählen.
3. Datei **unverändert** unter exakt `imports/TripTracer-Project-Bundle.zip` committen.
4. GitHub Action `Import TripTracer project bundle` verarbeitet nur die Datei mit erwarteter SHA-256-Prüfsumme.
5. Unter `Actions` den erfolgreichen Durchlauf prüfen; erst danach sind die importierten KiCad-Dateien im Repo.

Der Import ersetzt README-/Bibliotheksdateien ausschließlich beim erstmaligen Upload der kuratierten ZIP. Kein Archiv aus anderen Projekten hochladen.

**Einschränkung:** Erfolgreiches Entpacken ist keine KiCad-ERC-/DRC- oder Fahrzeugfreigabe.
