@echo off
echo ==================================
echo Qobuz Bot - Setup Script
echo ==================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python non trovato. Installalo da python.org
    pause
    exit /b 1
)
echo [OK] Python trovato

REM Install dependencies
echo.
echo Installazione dipendenze Python...
pip install -r requirements.txt

if errorlevel 1 (
    echo X Errore installazione dipendenze
    pause
    exit /b 1
)
echo [OK] Dipendenze installate

REM Setup .env
echo.
if exist .env (
    echo [!] File .env gia esistente
    set /p overwrite="Vuoi sovrascriverlo? (s/n): "
    if /i not "%overwrite%"=="s" (
        echo Setup completato (file .env non modificato)
        pause
        exit /b 0
    )
)

echo Configurazione .env
set /p supabase_url="Inserisci SUPABASE_URL: "
set /p supabase_key="Inserisci SUPABASE_KEY: "

(
echo SUPABASE_URL=%supabase_url%
echo SUPABASE_KEY=%supabase_key%
) > .env

echo [OK] File .env creato

echo.
echo ==================================
echo [OK] Setup completato!
echo ==================================
echo.
echo Prossimi passi:
echo 1. Configura l'account master sulla web app
echo 2. Aggiungi i guest accounts sulla web app
echo 3. Esegui: python cloud_bot.py
echo.
pause
