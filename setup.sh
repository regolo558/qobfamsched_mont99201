#!/bin/bash

echo "=================================="
echo "Qobuz Bot - Setup Script"
echo "=================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 non trovato. Installalo prima di continuare."
    exit 1
fi
echo "✅ Python 3 trovato"

# Check Chrome
if ! command -v google-chrome &> /dev/null && ! command -v chromium &> /dev/null; then
    echo "⚠️  Chrome/Chromium non trovato. Assicurati di installarlo."
else
    echo "✅ Chrome/Chromium trovato"
fi

# Install Python dependencies
echo ""
echo "📦 Installazione dipendenze Python..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dipendenze installate"
else
    echo "❌ Errore nell'installazione delle dipendenze"
    exit 1
fi

# Setup .env
echo ""
if [ -f ".env" ]; then
    echo "⚠️  File .env già esistente"
    read -p "Vuoi sovrascriverlo? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup completato (file .env non modificato)"
        exit 0
    fi
fi

echo "📝 Configurazione .env"
read -p "Inserisci SUPABASE_URL: " supabase_url
read -p "Inserisci SUPABASE_KEY: " supabase_key

cat > .env << EOF
SUPABASE_URL=$supabase_url
SUPABASE_KEY=$supabase_key
EOF

echo "✅ File .env creato"

echo ""
echo "=================================="
echo "✅ Setup completato!"
echo "=================================="
echo ""
echo "Prossimi passi:"
echo "1. Configura l'account master sulla web app"
echo "2. Aggiungi i guest accounts sulla web app"
echo "3. Esegui: python3 cloud_bot.py"
echo ""
