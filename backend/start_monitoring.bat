@echo off
echo ========================================
echo   Démarrage du Monitoring Substans.AI
echo ========================================
echo.

echo [1/2] Démarrage du serveur de métriques...
start "Metrics Server" cmd /k python backend\monitoring\metrics_endpoint.py

timeout /t 3 >nul

echo [2/2] Test de connexion...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Serveur de métriques démarré avec succès
    echo.
    echo URLs disponibles:
    echo   - Métriques: http://localhost:8000/metrics
    echo   - Health: http://localhost:8000/health
    echo   - Test: http://localhost:8000/test_metrics
) else (
    echo ⚠️ Le serveur n'est pas encore prêt
    echo Vérifiez la fenêtre "Metrics Server"
)

echo.
pause