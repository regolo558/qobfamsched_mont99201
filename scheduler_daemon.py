"""
Scheduler Daemon - Servizio persistente per esecuzione automatica degli schedule

Questo script rimane in esecuzione in background e controlla ogni minuto
se ci sono schedule da eseguire. Quando trova uno schedule all'ora pianificata,
lo esegue automaticamente.

Uso: python scheduler_daemon.py
"""

import os
import sys
import time
from datetime import datetime
from cloud_bot import CloudQobuzManager

class SchedulerDaemon:
    def __init__(self):
        self.manager = CloudQobuzManager()
        self.running = True
        self.check_interval = 60  # Controlla ogni 60 secondi

    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {message}")

    def run(self):
        self.log("=" * 60)
        self.log("Scheduler Daemon avviato")
        self.log("Controllo schedule ogni 60 secondi")
        self.log("Premi CTRL+C per interrompere")
        self.log("=" * 60)

        while self.running:
            try:
                # Controlla se ci sono schedule da eseguire
                schedule = self.manager.get_next_scheduled_execution()

                if schedule:
                    self.log(f"Schedule trovato: {schedule['name']} (ID: {schedule['id']})")
                    self.log(f"Data pianificata: {schedule['scheduled_date']}")
                    self.log("Avvio esecuzione automatica...")

                    success = self.manager.run_scheduled_execution()

                    if success:
                        self.log("Esecuzione completata con successo")
                    else:
                        self.log("Esecuzione completata con errori")
                else:
                    # Log silenzioso per non intasare i log
                    self.log("Nessun schedule da eseguire. Prossimo controllo in 60s...")

                # Attendi prima del prossimo controllo
                time.sleep(self.check_interval)

            except KeyboardInterrupt:
                self.log("\nInterruzione richiesta dall'utente")
                self.running = False
                break
            except Exception as e:
                self.log(f"ERRORE: {e}")
                self.log("Riprovo tra 60 secondi...")
                time.sleep(self.check_interval)

        self.log("Scheduler Daemon terminato")

def main():
    try:
        daemon = SchedulerDaemon()
        daemon.run()
    except Exception as e:
        print(f"ERRORE CRITICO: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
