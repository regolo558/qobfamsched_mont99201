# Qobuz Bot - Cloud Edition Backend

## Setup

### 1. Installa le dipendenze Python

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configura le variabili d'ambiente

Crea un file `.env` nella cartella `backend` con le tue credenziali Supabase:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
```

Puoi trovare queste credenziali nel file `.env` della root del progetto.

### 3. Installa ChromeDriver

Il bot utilizza Selenium con Chrome. Assicurati di avere:
- Google Chrome installato
- ChromeDriver compatibile con la tua versione di Chrome

Su Mac (con Homebrew):
```bash
brew install chromedriver
```

Su Ubuntu/Debian:
```bash
sudo apt-get install chromium-chromedriver
```

Su Windows:
- Scarica ChromeDriver da https://chromedriver.chromium.org/
- Aggiungi ChromeDriver al PATH

## Utilizzo

### Modalità 1: Scheduler Daemon (CONSIGLIATO)

Lo scheduler daemon è un servizio persistente che rimane in esecuzione e controlla automaticamente ogni minuto se ci sono schedule pianificati da eseguire. Quando trova uno schedule all'ora esatta, lo esegue automaticamente.

**Windows:**
```bash
cd backend
start_scheduler.bat
```

**Linux/Mac:**
```bash
cd backend
./start_scheduler.sh
```

Lo scheduler daemon:
- Controlla ogni 60 secondi se ci sono schedule da eseguire
- Esegue automaticamente gli schedule all'ora pianificata
- Registra tutti i log nel database
- Può essere interrotto con CTRL+C

Questa è la modalità più comoda per chi vuole semplicemente pianificare esecuzioni future dalla web app e lasciare che il bot si avvii automaticamente all'ora prestabilita.

### Modalità 2: Esecuzione Manuale

```bash
python cloud_bot.py
```

Avrai due opzioni:
1. **Esegui schedule pianificato**: Cerca nel database uno schedule con data/ora passata e status "pending" e lo esegue
2. **Esegui manualmente**: Esegue immediatamente tutti i guest con status "pending" senza uno schedule specifico

### Modalità 3: Esecuzione Automatica con Cron (Linux/Mac)

Per eseguire automaticamente il bot a intervalli regolari senza lo scheduler daemon, usa cron:

```bash
crontab -e
```

Aggiungi una riga per controllare ogni ora:
```
0 * * * * cd /path/to/project/backend && /usr/bin/python3 auto_scheduler.py
```

### Modalità 4: Esecuzione Automatica con Task Scheduler (Windows)

1. Apri Task Scheduler
2. Crea una nuova attività
3. Imposta il trigger (es: ogni ora)
4. Imposta l'azione: Avvia `python.exe` con argomento `auto_scheduler.py` nella cartella backend

## Come Funziona

1. Il bot si connette al database Supabase
2. Legge l'account master configurato
3. Cerca i guest accounts con status "pending"
4. Per ogni guest:
   - Cambia lo status a "processing"
   - Esegue il ciclo di automazione Selenium
   - Aggiorna lo status a "completed" o "failed"
   - Registra tutti i log nel database
5. Tutti i log sono visibili in tempo reale nella web app

## Note Importanti

- **Headless Mode**: Per eseguire su server senza display, modifica `bot_logic.py` aggiungendo `options.add_argument("--headless")` in `setup_driver()`
- **Rate Limiting**: Il bot attende 30 secondi tra un guest e l'altro per evitare rate limiting
- **Sicurezza**: Le password sono salvate in chiaro nel database. Per produzione, considera di criptarle
- **Errori**: Se un guest fallisce, il bot continua con il prossimo. Controlla i logs per dettagli

## Deploy su Server

### Opzione 1: VPS (Ubuntu/Debian)

```bash
# Installa dipendenze
sudo apt-get update
sudo apt-get install python3 python3-pip chromium-chromedriver

# Clona il progetto
cd /opt
git clone your-repo
cd your-repo/backend

# Installa dipendenze Python
pip3 install -r requirements.txt

# Configura .env
nano .env

# Configura cron
crontab -e
# Aggiungi: 0 3 * * * cd /opt/your-repo/backend && python3 cloud_bot.py >> /var/log/qobuz-bot.log 2>&1
```

### Opzione 2: Esecuzione Locale con Schedule

Puoi anche eseguire il bot sul tuo computer locale quando necessario:
1. Configura tutto tramite la web app
2. Quando è il momento, esegui `python cloud_bot.py`
3. Il bot leggerà le configurazioni dal cloud e registrerà i risultati

Questo è ideale per uso mensile occasionale (5-7 minuti) come menzionato.
