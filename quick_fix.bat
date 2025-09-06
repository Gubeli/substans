@echo off
echo ========================================
echo   Correction rapide des problèmes
echo ========================================x
echo.

echo [1/3] Installation du module redis Python...
pip install redis

echo.
echo [2/3] Création du dossier manquant...
mkdir monitoring\prometheus 2>nul

echo.
echo [3/3] Configuration du cache...
echo Mode sans Redis activé (développement)

echo.
echo Relançons le test...
python test_setup.py

pause