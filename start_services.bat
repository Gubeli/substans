@echo off
echo ========================================
echo   Démarrage de Substans.AI Services
echo ========================================
echo.

REM Démarrer Redis
echo [1/4] Démarrage de Redis...
start /B redis-server
timeout /t 2 >nul

REM Démarrer PostgreSQL si nécessaire
echo [2/4] Vérification de PostgreSQL...
sc query postgresql-x64-14 >nul 2>&1
if %errorlevel% neq 0 (
    echo PostgreSQL non trouvé comme service
) else (
    net start postgresql-x64-14 2>nul
    echo PostgreSQL démarré
)

REM Activer l'environnement virtuel
echo [3/4] Activation de l'environnement Python...
call venv\Scripts\activate.bat

REM Démarrer le backend
echo [4/4] Démarrage du backend Substans.AI...
start /B python backend\main.py

REM Démarrer le monitoring
echo [5/5] Démarrage du monitoring...
start /B python backend\monitoring\metrics_collector.py

echo.
echo ✅ Tous les services sont démarrés !
echo.
echo URLs d'accès :
echo - Backend API : http://localhost:5000
echo - Métriques : http://localhost:8000/metrics
echo - Redis : localhost:6379
echo.
echo Appuyez sur Ctrl+C pour arrêter les services
pause >nul