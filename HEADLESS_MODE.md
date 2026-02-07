# Configurazione Headless Mode

Per eseguire il bot su un server senza interfaccia grafica (headless), devi modificare il file `bot_logic.py`.

## Modifica Necessaria

Apri `bot_logic.py` e trova la funzione `setup_driver()`. Sostituisci con:

```python
def setup_driver(self):
    options = webdriver.ChromeOptions()

    # MODALITÀ HEADLESS - Decommentare per server senza GUI
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    # Opzioni standard
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    return webdriver.Chrome(options=options)
```

## Quando Usare Headless Mode

**USA headless mode se**:
- Esegui su un server Linux/VPS senza desktop environment
- Vuoi eseguire il bot in background senza finestre visibili
- Esegui tramite cron/systemd

**NON usare headless mode se**:
- Esegui sul tuo computer locale (puoi vedere cosa succede)
- Stai facendo debug (utile vedere il browser)
- Hai problemi con l'automazione (headless può avere comportamenti diversi)

## Installazione ChromeDriver su Server Linux

### Ubuntu/Debian

```bash
# Installa Chrome/Chromium
sudo apt-get update
sudo apt-get install -y chromium-browser chromium-chromedriver

# Se preferisci Google Chrome stabile
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb

# Installa ChromeDriver
sudo apt-get install -y chromium-chromedriver
```

### CentOS/RHEL

```bash
# Installa Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
sudo yum install ./google-chrome-stable_current_x86_64.rpm

# Installa ChromeDriver
sudo yum install chromium-chromedriver
```

## Verifica Installazione

```bash
# Verifica Chrome
google-chrome --version
# o
chromium --version

# Verifica ChromeDriver
chromedriver --version

# Verifica Python Selenium
python3 -c "from selenium import webdriver; print('Selenium OK')"
```

## Test Headless

Crea un file `test_headless.py`:

```python
from selenium import webdriver

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)
driver.get("https://www.google.com")
print(f"Titolo pagina: {driver.title}")
driver.quit()

print("✅ Headless mode funziona!")
```

Esegui:
```bash
python3 test_headless.py
```

Se vedi "✅ Headless mode funziona!", sei pronto!

## Troubleshooting Headless Mode

### Errore: Chrome binary not found

Specifica il percorso di Chrome:

```python
options = webdriver.ChromeOptions()
options.binary_location = "/usr/bin/chromium"  # o /usr/bin/google-chrome
options.add_argument("--headless")
# ... altre opzioni
```

### Errore: DevToolsActivePort file doesn't exist

Aggiungi:

```python
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--remote-debugging-port=9222")
```

### Errore: selenium.common.exceptions.SessionNotCreatedException

Versione di ChromeDriver incompatibile con Chrome. Aggiorna entrambi:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get upgrade chromium-browser chromium-chromedriver
```

### Screenshot per Debug in Headless

Aggiungi dopo le operazioni nel bot:

```python
driver.save_screenshot('/tmp/debug_screenshot.png')
```

## Esecuzione Completa su Server

Una volta configurato:

```bash
# Test manuale
cd /opt/project/backend
python3 cloud_bot.py

# Setup cron per esecuzione automatica ogni ora
crontab -e
# Aggiungi:
0 * * * * cd /opt/project/backend && python3 auto_scheduler.py >> /var/log/qobuz-bot.log 2>&1
```

## Differenze tra Normale e Headless

**Normale** (con GUI):
- Vedi il browser aprirsi
- Utile per debug
- Più lento
- Richiede desktop environment

**Headless** (senza GUI):
- Nessuna finestra visibile
- Più veloce
- Usa meno risorse
- Ideale per server
- Alcuni siti potrebbero comportarsi diversamente

## Best Practices

1. **Sviluppa in modalità normale** (con GUI visibile)
2. **Testa in headless** prima di deployare su server
3. **Abilita logging dettagliato** in produzione
4. **Salva screenshot** in caso di errori
5. **Monitora i logs** regolarmente
