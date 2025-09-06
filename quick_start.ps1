# quick_start.ps1
Write-Host "🚀 Démarrage rapide Substans.AI v3.2.0" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Démarrer le monitoring
Write-Host "`n📊 Démarrage du monitoring..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "python backend/monitoring/metrics_endpoint.py" -WindowStyle Minimized

# Message de succès
Write-Host "`n✅ Services démarrés:" -ForegroundColor Green
Write-Host "  • Monitoring: http://localhost:8000/metrics" -ForegroundColor White
Write-Host "  • Health: http://localhost:8000/health" -ForegroundColor White

Write-Host "`n💡 Pour arrêter: Fermez les fenêtres PowerShell" -ForegroundColor Yellow
