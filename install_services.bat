@echo off
echo ========================================
echo Installation des services Substans.AI
echo ========================================
echo.

REM Vérifier les privilèges administrateur
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Ce script nécessite des privilèges administrateur
    echo Relancez en tant qu'administrateur
    pause
    exit /b 1
)

echo [1/4] Installation de Redis pour Windows...
echo ----------------------------------------

REM Télécharger Redis pour Windows si nécessaire
if not exist "C:\Program Files\Redis\redis-server.exe" (
    echo Téléchargement de Redis...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/microsoftarchive/redis/releases/download/win-3.2.100/Redis-x64-3.2.100.msi' -OutFile 'Redis-x64.msi'"
    echo Installation de Redis...
    msiexec /i Redis-x64.msi /quiet
    del Redis-x64.msi
)

echo [2/4] Configuration de PostgreSQL...
echo ----------------------------------------

REM Vérifier si PostgreSQL est installé
where psql >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ PostgreSQL n'est pas installé
    echo Téléchargez-le depuis : https://www.postgresql.org/download/windows/
    pause
) else (
    echo ✅ PostgreSQL détecté
)

echo [3/4] Installation des outils Python...
echo ----------------------------------------

pip install --upgrade pip
pip install virtualenv

REM Créer l'environnement virtuel si nécessaire
if not exist "venv" (
    echo Création de l'environnement virtuel...
    python -m venv venv
)

echo [4/4] Installation des dépendances...
echo ----------------------------------------

REM Activer l'environnement virtuel et installer les dépendances
call venv\Scripts\activate.bat

pip install -r requirements.txt

echo.
echo ✅ Installation terminée !
pause