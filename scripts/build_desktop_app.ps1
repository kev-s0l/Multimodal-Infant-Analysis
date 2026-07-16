$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
  $python = Get-Command py -ErrorAction SilentlyContinue
}
if (-not $python) {
  throw "Python was not found. Install Python or add it to PATH before building."
}

& $python.Source -m PyInstaller `
  --noconfirm `
  --clean `
  --onedir `
  --windowed `
  --name MultimodalInfantAnalysis `
  --add-data "language_analysis;language_analysis" `
  --add-data "movement_analysis;movement_analysis" `
  --add-data "sleep_analysis;sleep_analysis" `
  --add-data "multimodal_analysis;multimodal_analysis" `
  --collect-all matplotlib `
  --collect-all PySide6 `
  --collect-all h5py `
  --collect-all scipy `
  --collect-all sklearn `
  --collect-all seaborn `
  --collect-all mne `
  --collect-all yasa `
  --collect-all edfio `
  app/main.py

Write-Host "Built dist\MultimodalInfantAnalysis\MultimodalInfantAnalysis.exe"
