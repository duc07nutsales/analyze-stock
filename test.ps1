$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
    throw 'Chua co .venv. Chay run.ps1 -Install truoc.'
}
New-Item -ItemType Directory -Path '.cache/matplotlib' -Force | Out-Null
$env:PYTHONUTF8 = '1'
$env:MPLBACKEND = 'Agg'
$env:MPLCONFIGDIR = Join-Path $PSScriptRoot '.cache/matplotlib'
& '.\.venv\Scripts\python.exe' -m tests.test_analysis
if ($LASTEXITCODE -ne 0) { throw 'Kiem thu phan tich that bai.' }
& '.\.venv\Scripts\python.exe' -m tests.test_ml
if ($LASTEXITCODE -ne 0) { throw 'Kiem thu hoc may that bai.' }
