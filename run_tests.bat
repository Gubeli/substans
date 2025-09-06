@echo off
echo ========================================
echo   Lancement des tests Substans.AI
echo ========================================
echo.

REM Activer l'environnement virtuel si nécessaire
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

echo [1/4] Tests unitaires...
echo ----------------------------------------
pytest tests\unit -v --tb=short

echo.
echo [2/4] Tests d'intégration...
echo ----------------------------------------
pytest tests\integration -v --tb=short

echo.
echo [3/4] Tests de charge...
echo ----------------------------------------
pytest tests\load -v --tb=short

echo.
echo [4/4] Génération du rapport de couverture...
echo ----------------------------------------
pytest --cov=backend --cov-report=html --cov-report=term

echo.
echo ✅ Tests terminés !
echo Rapport de couverture : htmlcov\index.html
echo.
pause