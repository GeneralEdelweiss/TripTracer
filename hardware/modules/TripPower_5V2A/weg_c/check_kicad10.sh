#!/usr/bin/env bash
# TripPower C – Native KiCad10 ERC + netlist + calculation regressions.
# Run from any shell in a clone of design/trippower-c. Requires KiCad 10.
set -euo pipefail
cd "$(dirname "$0")"
if ! command -v kicad-cli >/dev/null 2>&1; then
  echo "BLOCKED: native kicad-cli missing; no ERC/netlist result claimed" >&2
  exit 69
fi
VERSION="$(kicad-cli version)"
case "$VERSION" in
  10.*) echo "KiCad version: $VERSION";;
  *) echo "BLOCKED: requires KiCad 10, found: $VERSION" >&2; exit 70;;
esac
mkdir -p reports
kicad-cli sch erc --exit-code-violations --severity-all \
  -o reports/TripPower_C_ERC.rpt TripPower_C.kicad_sch
kicad-cli sch export netlist --format kicadsexpr \
  -o reports/TripPower_C.net TripPower_C.kicad_sch
python3 -m unittest -q protection_budget
echo "Native ERC+netlist generated under reports; no PCB exists; DRC not possible."
echo "IMPORTANT: This does not imply 200V surge, 125C or manufacturing qualification."
