@echo off
echo ====================================
echo Avvio Scheduler Daemon
echo ====================================
echo.
echo Questo servizio controlla automaticamente
echo gli schedule pianificati e li esegue
echo all'ora prestabilita.
echo.
echo Premi CTRL+C per interrompere
echo ====================================
echo.

REM Attiva l'ambiente virtuale se esiste
if exist "venv\Scripts\activate.bat" (
    echo Attivazione ambiente virtuale...
    call venv\Scripts\activate.bat
)

REM Avvia lo scheduler daemon
python scheduler_daemon.py

pause
