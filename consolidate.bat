@echo off
echo ========================================
echo  CONSOLIDATION DES SYSTEMES MANQUANTS
echo ========================================
echo.

REM Vérifier Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Python n'est pas installé ou pas dans le PATH
    pause
    exit /b 1
)

REM Exécuter le script de consolidation
echo Exécution du script de consolidation...
python consolidate_systems.py

if %errorlevel% equ 0 (
    echo.
    echo ✅ Consolidation réussie!
) else (
    echo.
    echo ❌ Erreur lors de la consolidation
)

pause