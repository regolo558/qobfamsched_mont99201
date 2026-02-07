#!/bin/bash

echo "===================================="
echo "Avvio Scheduler Daemon"
echo "===================================="
echo ""
echo "Questo servizio controlla automaticamente"
echo "gli schedule pianificati e li esegue"
echo "all'ora prestabilita."
echo ""
echo "Premi CTRL+C per interrompere"
echo "===================================="
echo ""

# Attiva l'ambiente virtuale se esiste
if [ -f "venv/bin/activate" ]; then
    echo "Attivazione ambiente virtuale..."
    source venv/bin/activate
fi

# Avvia lo scheduler daemon
python scheduler_daemon.py
