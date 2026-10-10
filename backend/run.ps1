$env:PYTHONPATH = "$env:PYTHONPATH;$(Get-Location)"
Set-Location $PSScriptRoot
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
