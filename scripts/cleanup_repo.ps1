Write-Host "CryptoAI cleanup helper" -ForegroundColor Cyan

Write-Host "This script does NOT delete .env automatically." -ForegroundColor Yellow
Write-Host "Recommended checks:" -ForegroundColor Yellow

git status

Write-Host ""
Write-Host "To remove accidentally tracked runtime files, run these manually if needed:" -ForegroundColor Yellow
Write-Host "git rm -r --cached venv data logs __pycache__ 2>`$null"
Write-Host "git rm --cached .env 2>`$null"
Write-Host ""
Write-Host "Then commit the cleanup if files were removed from Git tracking."
