param([switch]$Install)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Khong tao duoc moi truong Python.' }
}
if ($Install) {
    & '.\.venv\Scripts\python.exe' -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw 'Khong cai duoc thu vien.' }
}
New-Item -ItemType Directory -Path 'outputs','outputs/tables','outputs/figures','.cache/matplotlib' -Force | Out-Null
$env:MPLBACKEND = 'Agg'
$env:MPLCONFIGDIR = Join-Path $PSScriptRoot '.cache/matplotlib'
$env:PYTHONUTF8 = '1'
& '.\.venv\Scripts\python.exe' -u sp500_analysis.py
if ($LASTEXITCODE -ne 0) { throw 'Phan tich that bai; khong dung ket qua chay do.' }
