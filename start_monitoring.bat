# Créer le fichier avec PowerShell
@'
@echo off
echo ========================================
echo   Demarrage du Monitoring Substans.AI
echo ========================================
echo.

echo [1/2] Demarrage du serveur de metriques...
start "Metrics Server" cmd /k python backend\monitoring\metrics_endpoint.py

timeout /t 3 >nul

echo [2/2] Test de connexion...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo OK - Serveur de metriques demarre avec succes
    echo.
    echo URLs disponibles:
    echo   - Metriques: http://localhost:8000/metrics
    echo   - Health: http://localhost:8000/health
    echo   - Test: http://localhost:8000/test_metrics
) else (
    echo ATTENTION - Le serveur n'est pas encore pret
    echo Verifiez la fenetre "Metrics Server"
)

echo.
pause
'@ | Out-File -FilePath start_monitoring.bat -Encoding ASCII