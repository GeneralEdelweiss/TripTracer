# TripPower D Round12: NON-SIMULATING, UNTESTED Windows vendor model acquisition recipe.
# Requires licensed/download-authorized Internet access, PowerShell 5+ and explicit
# manufacturer redistribution-license verification. Never commit vendor models.
# Run from a private writable local folder, NOT the GitHub checkout.
[CmdletBinding()]
param(
    [string]$OutputDirectory = ".\trippower_vendor_private"
)
$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$root = (Resolve-Path $OutputDirectory).Path

$urls = @(
    @{File="TI_SLVMD03A_download.zip"; Url="https://www.ti.com/lit/zip/SLVMD03"},
    # Vishay SPICE download remains a MANUAL step from official page:
    # https://www.vishay.com/en/product/67027/tab/designtools-ppg/
    # Select 'SPICE Models for SQM100N10-10 (*.zip)' and keep licence notice.
    # Do NOT replace this with guessed ZIP URL.
    @{File="TPS2663_datasheet.pdf"; Url="https://www.ti.com/lit/ds/symlink/tps2663.pdf"}
)
foreach ($item in $urls) {
    $target = Join-Path $root $item.File
    Write-Host "Requesting official manufacturer file:" $item.Url
    Invoke-WebRequest -Uri $item.Url -OutFile $target -UseBasicParsing
    if (-not (Test-Path $target)) { throw "Not downloaded: $($item.File)" }
    $itemHash = Get-FileHash -Algorithm SHA256 $target
    "$($item.File),$($item.Url),$($itemHash.Hash)" |
        Add-Content -Encoding UTF8 (Join-Path $root "MANIFEST_LOCAL_DO_NOT_COMMIT.txt")
    Write-Host "SHA256 $($item.File): $($itemHash.Hash)"
}
$zipFile = Join-Path $root "TI_SLVMD03A_download.zip"
$bytes = [IO.File]::ReadAllBytes($zipFile)
if ($bytes.Length -lt 4 -or $bytes[0] -ne 0x50 -or $bytes[1] -ne 0x4B) {
    throw "TI model is NOT a ZIP (may be HTML redirect / access denied). No SPICE run."
}
$dst = Join-Path $root "TI_EXTRACTED_PRIVATE"
Expand-Archive -Path $zipFile -DestinationPath $dst -Force
$files = @(Get-ChildItem -Path $dst -File -Recurse)
$files | ForEach-Object { $_.FullName.Substring($dst.Length) } |
    Out-File -Encoding UTF8 (Join-Path $root "TI_ARCHIVE_FILELIST_LOCAL.txt")
$libs = @($files | Where-Object { $_.Extension -match '(?i)^\.(lib|cir|sub|txt|inc)$' })
if ($libs.Count -eq 0) {
    Write-Warning "No obvious readable model libraries found. Inspect archive by hand."
} else {
    foreach ($f in $libs) {
        "SOURCE=$($f.FullName)" | Add-Content -Encoding UTF8 (Join-Path $root "SUBCKTS_LOCAL.txt")
        Select-String -Path $f.FullName -Pattern '^\s*\.SUBCKT\b' |
            ForEach-Object { $_.Line } |
            Add-Content -Encoding UTF8 (Join-Path $root "SUBCKTS_LOCAL.txt")
        "SHA256 $($f.FullName) $((Get-FileHash -Algorithm SHA256 $f.FullName).Hash)" |
            Add-Content -Encoding UTF8 (Join-Path $root "LIB_HASHES_LOCAL.txt")
    }
}
Write-Host "END: no simulation executed, no model pin mapping established yet."
Write-Host "Next steps: install approved TI PSpice for TI Windows; open original testbench;"
Write-Host "inspect exact TPS26631 .SUBCKT, map pins to U201 PWP pins, run official test;"
Write-Host "then A23, capture full waveform and simulator build/version. Verify license before sharing."
